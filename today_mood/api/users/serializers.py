import re

from django.conf import settings
from rest_framework import serializers

from apps.users.models import User


class SimpleUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'name', 'email']


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'date_joined', 'name', 'username', 'email']


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=6, write_only=True)
    email = serializers.EmailField(allow_blank=False, required=True)

    class Meta:
        model = User
        fields = ('username', 'name', 'password', 'email')

    def validate_username(self, username):
        code_regex = re.compile('[a-zA-Z|0-9|\-_]')  # 영어 + 숫자 + -,_
        if code_regex.sub('', username):
            raise serializers.ValidationError('유효하지 않은 정규식입니다.', 'regex_error')

        return username

    def validate(self, data):
        try:
            user = User.objects.filter(username=data.get('username'))
            if len(user) > 0:
                raise serializers.ValidationError("Username already exists")
        except User.DoesNotExist:
            pass

        if User.objects.filter(email=data.get('email')).exists():
            raise serializers.ValidationError("email already exists")

        return data

    def create(self, validated_data):
        instance = User.objects.create_user(**validated_data)
        return instance


class PasswordFindSerializer(serializers.Serializer):
    email = serializers.EmailField(allow_null=False, allow_blank=False, required=True)
    username = serializers.CharField(max_length=150, required=True)

    class Meta:
        fields = ('email', 'username')


class IDFindSerializer(serializers.Serializer):
    email = serializers.EmailField(allow_null=False, allow_blank=False, required=True)
    name = serializers.CharField(max_length=50, required=True)

    class Meta:
        fields = ('email', 'name')


class SNSLoginSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=['apple', 'kakao'], required=True)
    email = serializers.EmailField(allow_null=False, allow_blank=False, required=True)
    name = serializers.CharField(max_length=50, required=True)

    class Meta:
        fields = ['type', 'unique_id', 'email', 'name']


class SNSUserPasswordSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined']

    def to_representation(self, user):
        new_password = '{}{}{}'.format(
            user.email.split('@')[0],
            settings.SNS_AUTH_USER_KEY,
            user.date_joined.strftime('%y%m%d')
        )

        ret = {
            'username': user.username,
            'password': new_password
        }

        return ret
