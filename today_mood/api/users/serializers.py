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
    password = serializers.CharField(min_length=6, max_length=20, write_only=True)
    email = serializers.EmailField(allow_blank=False, required=True)

    class Meta:
        model = User
        fields = ('username', 'name', 'password', 'email')

    def validate(self, data):
        try:
            user = User.objects.filter(username=data.get('username'))
            if len(user) > 0:
                raise serializers.ValidationError(_("Username already exists"))
        except User.DoesNotExist:
            pass

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
    unique_id = serializers.IntegerField(required=True)
    email = serializers.EmailField(allow_null=False, allow_blank=False, required=True)
    name = serializers.CharField(max_length=50, required=True)

    class Meta:
        fields = ['type', 'unique_id', 'email', 'name']
