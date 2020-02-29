from django.conf import settings
from rest_framework import viewsets
from rest_framework.response import Response

from api.users.serializers import UserSerializer
from apps.users.models import User


class UserInformationViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = UserSerializer(queryset, many=True)
        response = Response(serializer.data, content_type='application/json')

        return response

    def perform_create(self, serializer):
        result = serializer.save()
        return result
