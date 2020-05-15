from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from apps.moods.models import Mood, UserMood


@receiver(post_save, sender=UserMood)
def save_mood(sender, instance, created, **kwargs):
    if created:
        Mood.objects.filter(
            usermood__created__date=instance.created.date(),
            usermood__user=instance.user,
            is_day_last=True
        ).update(is_day_last=False)

        instance.mood.is_day_last = True
        instance.mood.save(update_fields=['is_day_last'])
