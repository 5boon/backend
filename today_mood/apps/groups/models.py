from django.db import models

from apps.users.models import User


class Group(models.Model):
    created = models.DateTimeField('created date', blank=True, editable=False, db_index=True)
    modified = models.DateTimeField('modified date', blank=True, editable=False)
    title = models.CharField(max_length=30, blank=True)
    summary = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = 'group'


class UserGroup(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    is_reader = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'user_group'

    def __str__(self):
        return '{}-{}'.format(self.crew.title, self.user.username)
