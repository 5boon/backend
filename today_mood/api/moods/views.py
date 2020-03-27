from datetime import datetime

from rest_framework import permissions, mixins, status, exceptions
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.moods.serializers import MoodSerializer
from apps.moods.models import Mood, UserMood

MOOD_LIMITED_COUNT = 100


class MoodViewSet(mixins.CreateModelMixin,
                  mixins.ListModelMixin,
                  GenericViewSet):
    """
        - Mood (기분) 생성
        endpoint : /moods/
    """

    queryset = Mood.objects.all()
    serializer_class = MoodSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        today = datetime.today()
        user = self.request.user

        user_mood_count = UserMood.objects.filter(
            user=user,
            created__date=today.date()
        ).count()

        # 오늘 기분 생성
        if user_mood_count < MOOD_LIMITED_COUNT:
            api_status = status.HTTP_201_CREATED
            mood = serializer.save()

            UserMood.objects.create(
                created=today,
                modified=today,
                user=self.request.user,
                mood=mood
            )
        else:
            err_data = {
                'err_code': 'limited',
                'description': 'You have exceeded 100 moods.'
            }
            return err_data, status.HTTP_400_BAD_REQUEST

        return self.get_serializer(instance=mood).data, api_status

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mood, api_status = self.perform_create(serializer)

        return Response(mood, status=api_status)

    def list(self, request, *args, **kwargs):
        if request.GET.get('date'):
            date = datetime.strptime(request.GET.get('date'), '%Y-%m-%d').date()
        else:
            date = datetime.today().date()

        user = self.request.user
        mood_list = Mood.objects.filter(
            usermood__user=user,
            usermood__created__date=date
        )

        if not mood_list:
            raise exceptions.NotFound

        mood = self.get_serializer(mood_list, many=True).data

        return Response(mood)
