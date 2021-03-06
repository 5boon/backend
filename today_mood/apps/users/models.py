from django.contrib.auth import models as auth_models
from django.db import models


class User(auth_models.AbstractUser):
    name = models.CharField(verbose_name='name', max_length=50)

    class Meta:
        verbose_name = 'user'

    def __str__(self):
        return "name: {}".format(self.username)

    def save(self, *args, **kwargs):
        return super(User, self).save(*args, **kwargs)
