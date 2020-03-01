from rest_framework import serializers

from apps.users.models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'


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
        fields = ('username', 'nickname', 'password', 'is_active')

    def create(self, validated_data):
        instance = User.objects.create_user(**validated_data)
        return instance
