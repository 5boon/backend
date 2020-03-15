# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

from api.moods.views import MoodViewSet

app_name = 'moods'

today_mood = MoodViewSet.as_view({
    'post': 'create',
    'get': 'list'
})

urlpatterns = [
    url(r'^$', today_mood, name='today_mood'),
]
