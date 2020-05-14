from django.db import models
from django.utils import timezone

from apps.mood_groups.models import MoodGroup
from apps.users.models import User


class Mood(models.Model):
    SOSO, GOOD, BEST, BAD, MOPE, WORST = 0, 5, 10, 15, 20, 25
    STATUS_CHOICES = (
        (WORST, 'worst'),  # 최악이에요
        (BAD, 'bad'),  # 나빠요
        (MOPE, 'mope'),  # 우울해요
        (SOSO, 'soso'),  # 그냥 그래요
        (GOOD, 'good'),  # 좋아요
        (BEST, 'best'),  # 최고에요
    )

    status = models.SmallIntegerField('status', choices=STATUS_CHOICES, blank=False)  # 상태
    simple_summary = models.CharField(max_length=200, blank=True)  # 한줄 요약

    class Meta:
        verbose_name = 'mood'


class UserMood(models.Model):
    created = models.DateTimeField('created date', default=timezone.now, blank=True, editable=False, db_index=True)
    modified = models.DateTimeField('modified date', default=timezone.now, blank=True, editable=False)
    mood_group = models.ForeignKey(MoodGroup, on_delete=models.CASCADE, default=None, null=True)
    mood = models.ForeignKey(Mood, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    do_show_summary = models.BooleanField(default=True)  # 한줄 요약 공개 여부

    class Meta:
        verbose_name = 'user_mood'

    def __str__(self):
        return '{}-{}-{}'.format(self.user.username, self.created, self.mood.status)
