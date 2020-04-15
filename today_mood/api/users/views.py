from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from rest_framework import viewsets, permissions, mixins, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.users.serializers import UserSerializer, UserRegisterSerializer, PasswordFindSerializer, IDFindSerializer, \
    SimpleUserSerializer, SNSLoginSerializer, SNSUserPasswordSerializer
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
                "title": "유저 가입",
                "pretext": "새로운 유저가 가입했습니다.",
                "fields": [
                    {
                        "title": "아이디",
                        "value": instance.username,
                        "short": True
                    },
                    {
                        "title": "이름",
                        "value": instance.name,
                        "short": True
                    },
                    {
                        "title": "이메일",
                        "value": instance.email,
                        "short": True
                    }
                ]
            }
        ]

        notify_slack(attachments, settings.SLACK_CHANNEL_JOINED_USER)
        return instance


class UserCheckViewSet(mixins.ListModelMixin,
                       GenericViewSet):
    """
        User email, id 체크
    """

    queryset = User.objects.all()
    serializer_class = SimpleUserSerializer
    permission_classes = (permissions.AllowAny, )

    def list(self, request, *args, **kwargs):
        data = request.GET
        email = data.get('email')
        username = data.get('username')

        if email:
            user = self.queryset.filter(email=email).first()
        elif username:
            user = self.queryset.filter(username=username).first()
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if user:
            serializer = self.get_serializer(instance=user)
            return Response(data=serializer.data, status=status.HTTP_200_OK)

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
            return Response(status=status.HTTP_400_BAD_REQUEST)

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
            return Response(status=status.HTTP_400_BAD_REQUEST)

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


class SNSLoginViewSet(mixins.CreateModelMixin,
                      GenericViewSet):
    """
        소셜 로그인 /sns/
        : 클라이언트에서 소셜인증으로 가져온 정보로 user 생
    """

    queryset = User.objects.all()
    serializer_class = SNSLoginSerializer
    permission_classes = (permissions.AllowAny, )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        username = "{}-{}".format(
            serializer.validated_data.get('type'),
            serializer.validated_data.get('email').split('@')[0]
        )

        user = User.objects.filter(
            username=username,
            email=serializer.validated_data.get('email'),
        ).first()

        if user:
            sns_data = SNSUserPasswordSerializer(instance=user).data
            return Response(data=sns_data, status=status.HTTP_200_OK)

        new_user_serializer = self.get_new_user_serializer(username, serializer.data)
        if not new_user_serializer.is_valid():
            return Response(
                data=new_user_serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        # todo: 비밀번호를 make_password 로 해싱해서 만듭값을 저장하면 로그인이 안됨...값이 다르게 들어가나?
        new_user = new_user_serializer.save()
        new_user.set_password(self.get_new_password(new_user.email))
        new_user.save(update_fields=['password'])

        sns_data = SNSUserPasswordSerializer(instance=new_user).data
        return Response(data=sns_data, status=status.HTTP_201_CREATED)

    def get_new_user_serializer(self, username, data):
        user_data = {
            'username': username,
            'email': data.get('email'),
            'name': data.get('name'),
            'password': settings.SNS_AUTH_USER_KEY,
        }

        user_serializer = UserRegisterSerializer(data=user_data)

        return user_serializer

    def get_new_password(self, email):
        """
            새로운 비밀번호 만들기
        """
        today = timezone.now()

        new_password = '{}{}{}'.format(
            email.split('@')[0],
            settings.SNS_AUTH_USER_KEY,
            today.strftime('%y%m%d')
        )

        return new_password
