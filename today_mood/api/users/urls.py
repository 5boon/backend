from django.conf.urls import url
from rest_framework import routers

from api.users.views import UserInformationViewSet, UserRegisterViewSet, UserPasswordViewSet, UserIDViewSet, \
    UserCheckViewSet, SNSLoginViewSet

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

identification = UserIDViewSet.as_view({
    'post': 'create'
})

check = UserCheckViewSet.as_view({
    'get': 'list'
})

sns = SNSLoginViewSet.as_view({
    'post': 'create'
})

urlpatterns = [
    url(r'^register/$', resister, name='user_register'),
    url(r'^sns/$', sns, name='user_sns'),
    url(r'^check/$', check, name='user_check'),
    url(r'^password/$', password, name='user_password'),
    url(r'^id/$', identification, name='user_id'),
]

router = routers.SimpleRouter()
router.register(r'', UserInformationViewSet, basename='information')

urlpatterns += router.urls

