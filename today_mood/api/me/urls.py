# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

from api.me.views import MeViewSet


me = MeViewSet.as_view({
    'get': 'list',
})


urlpatterns = [
    url(r'^$', me, name='me'),
]
