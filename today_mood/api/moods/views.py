from datetime import datetime

from django.conf import settings
from django.utils import timezone
from rest_framework import permissions, mixins, status, exceptions
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.moods.serializers import MoodSerializer
from apps.mood_groups.models import UserMoodGroup
from apps.moods.models import Mood, UserMood
from utils.slack import notify_slack

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

    def perform_create(self, serializer, show_summary_group_list=[]):
        """
            - show_summary_group_list 가 empty list 이면 전체 공개

        """

        today = timezone.now()
        user = self.request.user
        is_show_alone = False # 그룹 공개 여부
        mood_group_create_list = []

        if mood_group_create_list:
            is_show_alone = True

        user_mood_count = UserMood.objects.filter(
            user=user,
            created__date=today.date()
        ).count()

        # 오늘 기분 생성
        if user_mood_count < MOOD_LIMITED_COUNT:
            mood = serializer.save()

            # 그룹과 별개로, 개인 기분(mood) 생성
            UserMood.objects.create(
                mood=mood,
                user=self.request.user
            )

            # 현재 속한 그룹 리스트 가져옴
            mood_group_ids = UserMoodGroup.objects.filter(
                user=user
            ).values_list('mood_group_id', flat=True)

            for mood_group_id in mood_group_ids:
                do_show_summary = False

                if not is_show_alone and mood_group_id in show_summary_group_list:
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
        show_summary_group_list = request.data.get('group_list', [])

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        my_mode = self.perform_create(serializer, show_summary_group_list)

        attachments = [
            {
                "color": "#F0896A",
                "pretext": "앙! 기분띠!\n'{}'님이 '기분'을 생성했습니다!".format(request.user.name),
                "fields": [
                    {
                        "title": "상태",
                        "value": MOOD_LIST[my_mode.get('status')]
                    },
                    {
                        "title": "간단설명",
                        "value": my_mode.get('simple_summary')
                    }
                ]
            }
        ]
        notify_slack(attachments, settings.SLACK_CHANNEL_CREATE_MOOD)

        return Response(my_mode, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        if request.GET.get('date'):
            date = datetime.strptime(request.GET.get('date'), '%Y-%m-%d').date()
        else:
            date = timezone.now().date()

        user = self.request.user
        mood_list = self.get_queryset().filter(
            usermood__user=user,
            usermood__created__date=date
        )

        if not mood_list:
            raise exceptions.NotFound

        mood = self.get_serializer(mood_list, many=True).data

        return Response(mood)
