from django.utils import timezone
from rest_framework import permissions, mixins, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.mood_groups.serializers import MoodGroupSerializers, UserMoodGroupSerializers
from api.moods.serializers import MoodSerializer
from api.users.serializers import UserSerializer
from apps.mood_groups.models import MoodGroup, UserMoodGroup
from apps.moods.models import Mood, UserMood


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
        search_group_id = user_mood_group.mood_group.id
        today_date = timezone.now().date()

        user_mood_group_qs = UserMoodGroup.objects.filter(
            mood_group_id=search_group_id
        ).prefetch_related('user')

        user_id_list = list(user_mood_group_qs.values_list('user_id', flat=True))
        today_user_mood_list = list(UserMood.objects.filter(user_id__in=user_id_list, created__date=today_date))

        user_mood_list = []
        for user_mood_group in user_mood_group_qs:
            user_mood = None
            user_id = user_mood_group.user_id
            for today_user_mood in today_user_mood_list:
                if today_user_mood.user_id == user_id:
                    user_mood = today_user_mood.mood

            data = UserSerializer(instance=user_mood_group.user).data
            if user_mood:
                data['mood'] = MoodSerializer(instance=user_mood).data
            else:
                data['mood'] = None

            user_mood_list.append(data)

        return Response(user_mood_list)
