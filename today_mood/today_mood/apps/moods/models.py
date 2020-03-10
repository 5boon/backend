from django.db import models

from apps.users.models import User


class Mood(models.Model):
    SOSO, GOOD, BEST, BAD, WORST = 0, 1, 2, 3, 4
    STATUS_CHOICES = (
        (SOSO, 'soso'),
        (GOOD, 'good'),
        (BEST, 'best'),
        (BAD, 'bad'),
        (WORST, 'worst'),
    )

    status = models.SmallIntegerField('status', choices=STATUS_CHOICES, blank=False) # 상태
    simple_summary = models.CharField(max_length=200, blank=True) # 한줄 요약

    class Meta:
        verbose_name = 'mood'


class UserMood(models.Model):
    created = models.DateTimeField('created date', blank=True, editable=False)
    modified = models.DateTimeField('modified date', blank=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mood = models.ForeignKey(Mood, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'user_mood'

    def __str__(self):
        return '{}-{}-{}'.format(self.user.username, self.created, self.mood.status)