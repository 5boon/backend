from rest_framework import serializers

from apps.mood_groups.models import MoodGroup, UserMoodGroup, MoodGroupInvitation


class MoodGroupSerializers(serializers.ModelSerializer):

    class Meta:
        model = MoodGroup
        fields = ['id', 'created', 'modified', 'title', 'summary', 'code']


class UserMoodGroupSerializers(serializers.ModelSerializer):
    mood_group = MoodGroupSerializers()

    class Meta:
        model = UserMoodGroup
        fields = ['id', 'mood_group']

    def to_representation(self, instance):
        data = super(UserMoodGroupSerializers, self).to_representation(instance)

        user_inform = list(UserMoodGroup.objects.filter(
            mood_group_id=instance.mood_group_id
        ).values_list('user', 'user__name'))

        data['people'] = []
        data['people_cnt'] = len(user_inform)
        for _id, _name in user_inform:
            data['people'].append({
                'id': _id,
                'name': _name
            })

        return data


class MoodGroupCodeSerializers(serializers.BaseSerializer):
    code = serializers.CharField(max_length=64)

    def to_internal_value(self, data):
        return data


class MoodInvitationSerializers(serializers.ModelSerializer):

    class Meta:
        model = MoodGroupInvitation
        fields = ['id', 'invited_by', 'mood_group', 'guest']
