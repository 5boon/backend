from datetime import datetime

from django.utils import timezone
from rest_framework import permissions, mixins, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.moods.serializers import MoodSerializer
from apps.mood_groups.models import UserMoodGroup
from apps.moods.models import Mood, UserMood
from utils.slack import slack_notify_new_mood

MOOD_LIMITED_COUNT = 1000
MOOD_LIST = [
    'soso',
    'good',
    'best',
    'bad',
    'worst'
]


class MoodViewSet(mixins.CreateModelMixin,
                  mixins.ListModelMixin,
                  GenericViewSet):
    """
        - Mood (기분) 생성
        endpoint : /moods/
    """

    queryset = Mood.objects.all()
    serializer_class = MoodSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        """
            - show_summary_group_list 가 empty list 이면 전체 공개
        """

        today = timezone.now()
        user = self.request.user
        mood_group_create_list = []
        show_summary_group_list = self.request.data.get('group_list', [])  # 기분 설명(summary) 보여줄 그룹

        user_mood_count = UserMood.objects.filter(
            user=user,
            created__date=today.date(),
            mood_group=None
        ).count()

        # 오늘 기분 생성
        if user_mood_count < MOOD_LIMITED_COUNT:
            # 현재 속한 그룹 리스트 가져옴
            mood_group_ids = list(UserMoodGroup.objects.filter(
                user=user
            ).values_list('mood_group_id', flat=True))

            if not self.is_my_group(show_summary_group_list, mood_group_ids):
                raise PermissionDenied

            mood = serializer.save()

            # 그룹과 별개로, 개인 기분(mood) 생성 - 그룹이 없을수도 있어서, mood_group=None 을 기본으로 생성
            UserMood.objects.create(
                mood=mood,
                user=self.request.user,
                mood_group=None
            )

            for mood_group_id in mood_group_ids:
                do_show_summary = False

                if mood_group_id in show_summary_group_list:
                    do_show_summary = True

                mood_group_create_list.append(
                    UserMood(
                        do_show_summary=do_show_summary,
                        mood_group_id=mood_group_id,
                        user=user,
                        mood=mood
                    )
                )

            if mood_group_create_list:
                UserMood.objects.bulk_create(mood_group_create_list)

        else:
            err_data = {
                'err_code': 'limited',
                'description': 'You have exceeded 100 moods.'
            }
            return err_data, status.HTTP_400_BAD_REQUEST

        return self.get_serializer(instance=mood).data

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        my_mode = self.perform_create(serializer)

        slack_notify_new_mood(
            MOOD_LIST[my_mode.get('status')],
            request.user.name,
            my_mode.get('simple_summary')
        )

        return Response(my_mode, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        if request.GET.get('date'):
            date = datetime.strptime(request.GET.get('date'), '%Y-%m-%d').date()
        else:
            date = timezone.now().date()

        user = self.request.user
        mood_list = self.get_queryset().filter(
            usermood__created__date=date,
            usermood__user=user,
            usermood__mood_group=None
        )

        if not mood_list:
            Response(status=status.HTTP_200_OK)

        mood = self.get_serializer(mood_list, many=True).data
        return Response(mood, status=status.HTTP_200_OK)

    @staticmethod
    def is_my_group(groups: list, my_groups: list) -> bool:
        other_group = set(groups) - set(my_groups)

        if other_group:
            return False
        else:
            return True
