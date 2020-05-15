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

        # 오늘 하루 마지막 기분으로 업데이트
        instance.mood.is_day_last = True
        instance.mood.save(update_fields=['is_day_last'])
