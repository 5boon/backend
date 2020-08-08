from django.db.models.signals import post_delete
from django.dispatch import receiver

from apps.mood_groups.models import UserMoodGroup, MoodGroup


@receiver(post_delete, sender=UserMoodGroup)
def delete_user_mood_group(sender, instance, **kwargs):
    if not UserMoodGroup.objects.filter(mood_group_id=instance.mood_group.id).exists():
        MoodGroup.objects.filter(id=instance.mood_group.id).delete()
