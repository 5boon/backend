from django.db import models

from apps.users.models import User


class MoodGroup(models.Model):
    created = models.DateTimeField('created date', blank=True)
    modified = models.DateTimeField('modified date', blank=True)
    title = models.CharField(max_length=30, blank=True)
    summary = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = 'group'


class UserMoodGroup(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mood_group = models.ForeignKey(MoodGroup, on_delete=models.CASCADE)
    is_reader = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'user_mood_group'

    def __str__(self):
        return '{}-{}'.format(self.mood_group.title, self.user.username)