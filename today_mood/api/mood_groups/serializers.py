from rest_framework import serializers

from apps.mood_groups.models import MoodGroup, UserMoodGroup, MoodGroupInvitation


class MoodGroupSerializers(serializers.ModelSerializer):

    class Meta:
        model = MoodGroup
        fields = ['id', 'created', 'modified', 'title', 'summary']


class UserMoodGroupSerializers(serializers.ModelSerializer):
    mood_group = MoodGroupSerializers()

    class Meta:
        model = UserMoodGroup
        fields = ['id', 'mood_group', 'is_reader']

    def to_representation(self, instance):
        data = super(UserMoodGroupSerializers, self).to_representation(instance)
        data['people_cnt'] = UserMoodGroup.objects.filter(
            mood_group_id=instance.mood_group_id
        ).count()

        return data


class MoodInvitationSerializers(serializers.ModelSerializer):

    class Meta:
        model = MoodGroupInvitation
        fields = ['id', 'invited_by', 'mood_group', 'guest']
