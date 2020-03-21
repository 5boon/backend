# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from rest_framework import routers

from api.mood_groups.views import GroupViewSet, MyGroupViewSet

app_name = 'mood_groups'


router = routers.SimpleRouter()
router.register(r'', GroupViewSet, basename='group')
router.register(r'mine', MyGroupViewSet, basename='my_group')
urlpatterns = router.urls
