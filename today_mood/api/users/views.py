from rest_framework import viewsets, permissions, mixins
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.users.serializers import UserSerializer, UserRegisterSerializer
from apps.users.models import User
from utils.slack import notify_slack


class UserInformationViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = UserSerializer(queryset, many=True)
        response = Response(serializer.data, content_type='application/json')

        return response

    def perform_create(self, serializer):
        result = serializer.save()
        return result


class UserRegister(mixins.CreateModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    """

        User 등록 API

    """

    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    lookup_url_kwarg = 'username'
    lookup_field = 'username'

    def perform_create(self, serializer):
        instance = serializer.save()

        attachments = [
            {
                "color": "#36a64f",
                "pretext": "새로운 유저가 가입했습니다.",
                "author_name": instance.username,
                "fields": [
                    {
                        "title": "닉네임",
                        "value": instance.nickname
                    }
                ]
            }
        ]

        notify_slack(attachments, '#join-user')
        return instance

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = (permissions.AllowAny,)
        return super(UserRegister, self).get_permissions()
