from django.conf.urls import url
from django.urls import include

app_name = 'api'

urlpatterns = [
    url(r'users/', include('api.users.urls')),
    url(r'me/', include('api.me.urls')),
    url(r'moods/', include('api.moods.urls')),
    url(r'groups/', include('api.mood_groups.urls')),
]
