from datetime import datetime

from rest_framework import permissions, mixins, status, exceptions
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.moods.serializers import MoodSerializer
from apps.moods.models import Mood, UserMood


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
        user_mood = UserMood.objects.filter(
            user=user,
            created__date=today.date()
        ).prefetch_related('mood').first()

        # 오늘 기분 수정
        if user_mood:
            mood = user_mood.mood
            update_fields = []

            if mood.status != serializer.validated_data.get('status'):
                mood.status = serializer.validated_data.get('status')
                update_fields.append('status')

            if mood.simple_summary != serializer.validated_data.get('simple_summary'):
                mood.simple_summary = serializer.validated_data.get('simple_summary')
                update_fields.append('simple_summary')

            if update_fields:
                api_status = status.HTTP_200_OK
                user_mood.modified = today
                user_mood.save(update_fields=['modified'])
                mood.save(update_fields=update_fields)

        # 오늘 기분 생성
        else:
            api_status = status.HTTP_201_CREATED
            mood = serializer.save()

            UserMood.objects.create(
                created=today,
                modified=today,
                user=self.request.user,
                mood=mood
            )

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
        user_mood = UserMood.objects.filter(
            user=user,
            created__date=date
        ).prefetch_related('mood').first()

        if not user_mood:
            raise exceptions.NotFound

        mood = self.get_serializer(instance=user_mood.mood).data

        return Response(mood)
