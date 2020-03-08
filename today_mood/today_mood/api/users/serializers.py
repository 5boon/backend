from rest_framework import serializers

from apps.users.models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'date_joined', 'last_login', 'email', 'nickname']


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=6, max_length=20, write_only=True)

    def validate(self, data):
        try:
            user = User.objects.filter(username=data.get('username'))
            if len(user) > 0:
                raise serializers.ValidationError(_("Username already exists"))
        except User.DoesNotExist:
            pass

        return data

    class Meta:
        model = User
        fields = ('username', 'nickname', 'password',)

    def create(self, validated_data):
        instance = User.objects.create_user(**validated_data)
        return instance


class SnsOauthSerializer(serializers.BaseSerializer):
    token = serializers.CharField(min_length=1, max_length=100, required=True)
    sns_type = serializers.ChoiceField(choices=['apple', 'kakao'], required=True)

    class Meta:
        fields = ['token']

    def to_internal_value(self, data):
        token = data.get('token')
        sns_type = data.get('sns_type')

        if not token:
            raise serializers.ValidationError({
                'token': 'This field is required.'
            })

        if not sns_type:
            raise serializers.ValidationError({
                'sns_type': 'This field is required.'
            })

        return {
            'token': token,
            'sns_type': sns_type
        }
