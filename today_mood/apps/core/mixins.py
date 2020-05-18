from django.db import models
from django.utils import timezone


class TimeModelMixin(models.Model):
    created = models.DateTimeField('created date', default=timezone.now, blank=True, editable=False, db_index=True)
    modified = models.DateTimeField('modified date', default=timezone.now, blank=True, editable=False)

    class Meta:
        abstract = True
