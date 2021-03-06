import hashlib

from django.utils import timezone
from rest_framework import permissions, mixins, status, exceptions
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.mood_groups.serializers import MoodGroupSerializers, UserMoodGroupSerializers, MoodGroupCodeSerializers
from api.moods.serializers import UserMoodSerializers
from apps.mood_groups.models import MoodGroup, UserMoodGroup
from apps.moods.models import UserMood
from apps.users.models import User
from utils.slack import slack_notify_new_group


import logging

# Get an instance of a logger
logger = logging.getLogger('django')


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
        data['code'] = hashlib.sha256(data.get('title').encode()).hexdigest()

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        group = self.perform_create(serializer)

        UserMoodGroup.objects.create(
            user=request.user,
            mood_group_id=group.id,
        )

        slack_notify_new_group(request.user.name, serializer.validated_data)
        logger.info('action: {}/ menu: {}/ pk: {}/ user_id:{}'.format(
            'create', 'groups', group.id, request.user.id
        ))
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MyGroupViewSet(mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.DestroyModelMixin,
                     GenericViewSet):
    """
        - 내 그룹(mood_groups) 조회
        endpoint : /mood_groups/mine/
    """

    queryset = UserMoodGroup.objects.all()
    serializer_class = UserMoodGroupSerializers
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def list(self, request, *args, **kwargs) -> Response:
        queryset = self.get_queryset().filter(
            user=request.user
        ).prefetch_related('mood_group', 'user')

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs) -> Response:
        user_mood_group = self.get_object()

        if user_mood_group.user_id != request.user.id:
            raise PermissionDenied

        user_mood_group.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def retrieve(self, request, *args, **kwargs) -> Response:
        # 그룹에 속한 사람들 리스트
        user_mood_group = self.get_object()
        display_mine = request.GET.get('display_mine', None)  # 본인 기분 표시 여부

        try:
            if user_mood_group.user != request.user:
                raise PermissionDenied
        except User.DoesNotExist:
            raise exceptions.NotFound

        search_group_id = user_mood_group.mood_group.id
        today_date = timezone.now().date()

        user_id_list = UserMoodGroup.objects.filter(
            mood_group_id=search_group_id
        ).values_list('user_id', flat=True)

        user_mood_list = []
        for user_id in user_id_list:
            mood_data = None

            if display_mine is None and user_id == request.user.id:
                continue

            try:
                user = User.objects.filter(id=user_id).get()
            except User.DoesNotExist:
                # 로그 남길지 생각중
                continue

            # 가장 최근 기분을 가져옴
            user_mood = UserMood.objects.filter(
                user=user,
                created__date=today_date,
                mood_group_id=search_group_id,
            ).last()

            if user_mood:
                user_mood_data = UserMoodSerializers(instance=user_mood).data

                if user_mood_data.get('do_show_summary'):
                    simple_summary = user_mood_data.get('mood').get('simple_summary')
                else:
                    simple_summary = None

                mood_data = {
                    'created': user_mood_data.get('created'),
                    'status': user_mood_data.get('mood').get('status'),
                    'simple_summary': simple_summary
                }

            data = {
                'user': user.name,
                'mood': mood_data
            }

            user_mood_list.append(data)

        return Response(user_mood_list)


class GroupInvitationViewSet(mixins.CreateModelMixin,
                             GenericViewSet):
    """
        - 그룹(mood_groups) 코드로 그룹 가입
        endpoint : /mood_groups/invitation/
    """

    queryset = UserMoodGroup.objects.all()
    serializer_class = UserMoodGroupSerializers
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def create(self, request, *args, **kwargs) -> Response:
        code_serializer = MoodGroupCodeSerializers(data=request.data)
        if not code_serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        code = code_serializer.validated_data.get('code')
        user_id = request.user.id

        has_user_mood = self.get_queryset().filter(
            user_id=user_id,
            mood_group__code=code
        ).exists()

        # 이미 속한 그룹인 경우
        if has_user_mood:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            mood_group = MoodGroup.objects.filter(code=code).get()
        except MoodGroup.DoesNotExist:
            raise exceptions.NotFound

        user_mood_group = UserMoodGroup.objects.create(
            mood_group_id=mood_group.id,
            user_id=user_id,
        )
        data = self.get_serializer(instance=user_mood_group).data

        return Response(data=data, status=status.HTTP_201_CREATED)
