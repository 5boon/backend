# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

from api.moods.views import MoodViewSet, WeekMoodViewSet, YearMoodViewSet, MonthMoodViewSet

app_name = 'moods'

today_mood = MoodViewSet.as_view({
    'post': 'create',
    'get': 'list'
})

week_mood = WeekMoodViewSet.as_view({
    'get': 'list'
})

year_mood = YearMoodViewSet.as_view({
    'get': 'list'
})

month_mood = MonthMoodViewSet.as_view({
    'get': 'list'
})

urlpatterns = [
    url(r'^$', today_mood, name='today_mood'),
    url(r'^week/$', week_mood, name='week_mood'),
    url(r'^(?P<year>[0-9]{4})/$', year_mood, name='year_mood'),
    url(r'^(?P<year>[0-9]{4})/(?P<month>[0-9])/$', month_mood, name='month_mood'),
]
