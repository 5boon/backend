from django.utils import timezone
from rest_framework import permissions, mixins, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.mood_groups.serializers import MoodGroupSerializers, UserMoodGroupSerializers
from api.moods.serializers import UserMoodSerializers
from apps.mood_groups.models import MoodGroup, UserMoodGroup
from apps.moods.models import UserMood
from apps.users.models import User


class GroupViewSet(mixins.CreateModelMixin,
                   GenericViewSet):
    """
        - 그룹(mood_groups) 생성
        endpoint : /mood_groups/
    """

    queryset = MoodGroup.objects.all()
    serializer_class = MoodGroupSerializers
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        group = serializer.save()
        return group

    def create(self, request, *args, **kwargs):
        today = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        data = request.data
        data['created'] = today
        data['modified'] = today

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        group = self.perform_create(serializer)

        # 그룹을 생성한 경우 그룹의 리더가 됨
        UserMoodGroup.objects.create(
            user=request.user,
            mood_group=group,
            is_reader=True
        )

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MyGroupViewSet(mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     GenericViewSet):
    """
        - 내 그룹(mood_groups) 조회
        endpoint : /mood_groups/mine/
    """

    queryset = UserMoodGroup.objects.all()
    serializer_class = UserMoodGroupSerializers
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(user=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        # 그룹에 속한 사람들 리스트
        user_mood_group = self.get_object()

        if user_mood_group.user != request.user:
            raise PermissionDenied

        search_group_id = user_mood_group.mood_group.id
        today_date = timezone.now().date()

        user_id_list = UserMoodGroup.objects.filter(
            mood_group_id=search_group_id
        ).values_list('user_id', flat=True)

        user_mood_list = []
        for user_id in user_id_list:
            try:
                user = User.objects.filter(id=user_id).get()
            except User.DoesNotExist:
                # 로그 남길지 생각중
                continue

            # 가장 최근 기분을 가져옴
            user_mood = UserMood.objects.filter(
                user=user,
                created__date=today_date
            ).last()
            user_mood_data = UserMoodSerializers(instance=user_mood).data
            mood_data = user_mood_data.get('mood')
            do_show_summary = mood_data.get('do_show_summary')

            data = {
                'user': user.nickname,
                'mood': {
                    'created': user_mood_data.get('created'),
                    'status': mood_data.get('status'),
                    'simple_summary': mood_data.get('simple_summary') if do_show_summary else None,
                }
            }

            user_mood_list.append(data)

        return Response(user_mood_list)
