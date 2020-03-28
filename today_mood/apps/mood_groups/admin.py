from django.contrib import admin

from apps.mood_groups.models import MoodGroup, UserMoodGroup

admin.site.register(MoodGroup)
admin.site.register(UserMoodGroup)
