from django.conf.urls import url
from django.urls import path, include

urlpatterns = [
    # oatuh2 token
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    # api url
    url(r'^', include('api.urls', namespace='api')),
    url(r'^api-auth/', include('rest_framework.urls'))
]
