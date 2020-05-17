from django.db import models

from apps.core.mixins import TimeModelMixin
from apps.users.models import User


class MoodGroup(TimeModelMixin, models.Model):
    title = models.CharField(max_length=30, blank=True)
    summary = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = 'group'


class UserMoodGroup(TimeModelMixin, models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mood_group = models.ForeignKey(MoodGroup, on_delete=models.CASCADE)
    is_reader = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'user_mood_group'

    def __str__(self):
        return '{}-{}'.format(self.mood_group.title, self.user.name)


class MoodGroupInvitation(TimeModelMixin, models.Model):
    mood_group = models.ForeignKey(MoodGroup, on_delete=models.CASCADE)
    invited_by = models.CharField(max_length=50)
    guest = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'user_mood_group'

    def __str__(self):
        return 'group: {} - guest {}'.format(self.mood_group.title, self.guest.name)
