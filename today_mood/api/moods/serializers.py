from rest_framework import serializers

from apps.moods.models import Mood, UserMood


class MoodSerializer(serializers.ModelSerializer):

    class Meta:
        model = Mood
        fields = ['id', 'status', 'simple_summary']

    def to_representation(self, instance):
        ret = super(MoodSerializer, self).to_representation(instance)
        # ret['status'] = instance.get_status_display()
        return ret


class UserMoodSerializers(serializers.ModelSerializer):
    mood = MoodSerializer()

    class Meta:
        model = UserMood
        fields = ['id', 'user', 'mood', 'do_show_summary']
