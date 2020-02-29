from django.conf.urls import url
from django.urls import include

app_name = 'api'

urlpatterns = [
    url(r'users/', include('api.users.urls')),
]
