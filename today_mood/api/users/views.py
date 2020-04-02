from rest_framework import viewsets, permissions, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.users.serializers import UserSerializer, UserRegisterSerializer, PasswordFindSerializer, IDFindSerializer
from api.users.utils import send_pw_email, create_temp_pw
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


class UserRegisterViewSet(mixins.CreateModelMixin,
                          mixins.RetrieveModelMixin,
                          GenericViewSet):
    """
        User 등록 API
        : User 등록은 permission 없이 호출 가능
    """

    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = (permissions.AllowAny, )
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
                        "title": "이름",
                        "value": instance.name
                    }
                ]
            }
        ]

        notify_slack(attachments, '#join-user')
        return instance


class UserCheckViewSet(mixins.ListModelMixin,
                       GenericViewSet):
    """
        User email, id 체크
    """

    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny, )

    def list(self, request, *args, **kwargs):
        data = request.GET
        email = data.get('email')
        username = data.get('username')

        if email:
            is_exist = self.queryset.filter(email=email).exists()
        elif username:
            is_exist = self.queryset.filter(username=username).exists()
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if is_exist:
            return Response(status=status.HTTP_200_OK)

        return Response(status=status.HTTP_404_NOT_FOUND)


class UserPasswordViewSet(mixins.CreateModelMixin,
                          mixins.UpdateModelMixin,
                          GenericViewSet):
    """
        비밀번호 찾기, 변경 API
        : User 패스워드 찾기는 permission 없이 호출 가능 ( id, email 로 체크 )
    """

    queryset = User.objects.all()
    serializer_class = PasswordFindSerializer
    permission_classes = (permissions.AllowAny, )

    def create(self, request, *args, **kwargs):
        pw_serializer = self.get_serializer(data=request.data)

        if not pw_serializer.is_valid():
            return Response()

        user = User.objects.filter(
            username=pw_serializer.validated_data.get('username'),
            email=pw_serializer.validated_data.get('email'),
        ).first()

        if user:
            new_pw = create_temp_pw()
            user.set_password(new_pw)
            user.save(update_fields=['password'])
            send_pw_email(email_address=user.email, new_pw=new_pw)

            data = {
                'email': user.email
            }
            return Response(data=data, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_404_NOT_FOUND)

    def update(self, request, *args, **kwargs):
        new_pw = request.data.get('new_password')

        if new_pw is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        user.set_password(new_pw)
        user.save(update_fields=['password'])

        return Response(status=status.HTTP_200_OK)

    def get_permissions(self):
        if self.action == 'update':
            self.permission_classes = (permissions.IsAuthenticated, )
        return super(UserPasswordViewSet, self).get_permissions()


class UserIDViewSet(mixins.CreateModelMixin,
                    GenericViewSet):
    """
        ID 찾기 (permission 없이 호출 가능)
    """

    queryset = User.objects.all()
    serializer_class = IDFindSerializer
    permission_classes = (permissions.AllowAny, )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response()

        user = User.objects.filter(
            name=serializer.validated_data.get('name'),
            email=serializer.validated_data.get('email'),
        ).first()

        if user:
            data = {
                'username': user.username,
                'date_joined': user.date_joined
            }
            return Response(data=data, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_404_NOT_FOUND)
