from rest_framework import serializers

from apps.mood_groups.models import MoodGroup, UserMoodGroup


class MoodGroupSerializers(serializers.ModelSerializer):

    class Meta:
        model = MoodGroup
        fields = ['id', 'created', 'modified', 'title', 'summary']


class UserMoodGroupSerializers(serializers.ModelSerializer):
    mood_group = MoodGroupSerializers()

    class Meta:
        model = UserMoodGroup
        fields = ['id', 'user', 'mood_group', 'is_reader']
