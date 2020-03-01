# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

from api.users.views import UserInformationViewSet, UserRegister

information = UserInformationViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

resister = UserRegister.as_view({
    'post': 'create'
})

urlpatterns = [
    url(r'^$', information, name='information'),
    url(r'^register/$', resister, name='user_register'),
]
