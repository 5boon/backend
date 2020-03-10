from django.contrib import admin

from apps.moods.models import Mood, UserMood

admin.site.register(Mood)
admin.site.register(UserMood)
