from django.contrib.auth import models as auth_models
from django.core import validators
from django.db import models


class User(auth_models.AbstractUser):
    nickname = models.CharField(verbose_name='name', max_length=50)

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'user'

    def __str__(self):
        return "name: {}".format(self.username)
