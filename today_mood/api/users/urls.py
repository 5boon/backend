# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
from rest_framework import routers

from api.users.views import UserInformationViewSet, UserRegisterViewSet, UserPasswordViewSet

app_name = 'users'

information = UserInformationViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

resister = UserRegisterViewSet.as_view({
    'post': 'create'
})

password = UserPasswordViewSet.as_view({
    'post': 'create',
    'patch': 'update'
})

urlpatterns = [
    url(r'^register/$', resister, name='user_register'),
    url(r'^password/$', password, name='user_password'),
]

router = routers.SimpleRouter()
router.register(r'', UserInformationViewSet, basename='information')

urlpatterns += router.urls

