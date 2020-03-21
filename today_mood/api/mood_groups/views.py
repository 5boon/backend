from django.utils import timezone
from rest_framework import permissions, mixins, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.mood_groups.serializers import MoodGroupSerializers, UserMoodGroupSerializers
from apps.mood_groups.models import MoodGroup, UserMoodGroup


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

        return Response(group, status=status.HTTP_201_CREATED)


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
