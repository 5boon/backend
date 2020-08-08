from django.conf.urls import url

from api.me.views import MeViewSet


me = MeViewSet.as_view({
    'get': 'list',
})


urlpatterns = [
    url(r'^$', me, name='me'),
]
