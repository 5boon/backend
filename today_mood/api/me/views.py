from rest_framework import mixins
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.users.serializers import UserSerializer
from apps.users.models import User


class MeViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    """
    /me 엔드포인트
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def list(self, request) -> Response:
        instance = request.user
        serializer = UserSerializer(instance)

        return Response(serializer.data)
