# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

from api.users.views import UserInformationViewSet

information = UserInformationViewSet.as_view({
    'get': 'list', 'post': 'create'
})


urlpatterns = [
    url(r'^$', information, name='information'),
]
