from calendar import monthrange
from datetime import datetime, timedelta

from django.utils import timezone
from rest_framework import permissions, mixins, status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.moods.exceptions import LimitTodayMood, ServiceUnavailable
from api.moods.permissions import IsUserMoodGroup
from api.moods.serializers import MoodSerializer
from api.moods.services import MoodDto, MoodManageService
from api.pagination import CustomCursorPagination
from apps.moods.models import Mood, UserMood
from utils.slack import slack_notify_new_mood

MOOD_DICT = {
    Mood.WORST: ['최악이에요', '#383B47'],
    Mood.BAD: ['나빠요', '#494F67'],
    Mood.MOPE: ['우울해요', '#5070C2'],
    Mood.SOSO: ['그냥그래요', '#9795FF'],
    Mood.GOOD: ['좋아요', '#F4B1BA'],
    Mood.BEST: ['최고에요', '#EA6D7D'],
}


class MoodViewSet(mixins.CreateModelMixin,
                  mixins.ListModelMixin,
                  GenericViewSet):
    """
        - Mood (기분) 생성
        endpoint : /moods/
    """

    queryset = Mood.objects.all()
    serializer_class = MoodSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly, IsUserMoodGroup)
    pagination_class = CustomCursorPagination

    def perform_create(self, serializer) -> dict:
        """
            - show_summary_group_list 가 empty list 이면 전체 공개
        """

        mood_manage_service = MoodManageService(self.request)
        mood = self._build_mood_from_validated_data(self.request.data)

        try:
            response_data = mood_manage_service.update_my_mood(mood)
        except LimitTodayMood:
            raise ServiceUnavailable

        return response_data

    def create(self, request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        my_mode = self.perform_create(serializer)

        slack_notify_new_mood(
            MOOD_DICT[my_mode.get('status')],
            request.user.name,
            my_mode.get('simple_summary')
        )

        return Response(my_mode, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs) -> Response:
        self.pagination_class.cursor = self.request.query_params.get('cursor')

        if request.GET.get('date'):
            date = datetime.strptime(request.GET.get('date'), '%Y-%m-%d').date()
        else:
            date = timezone.now().date()

        user = self.request.user
        mood_qs = self.get_queryset().filter(
            usermood__created__date=date,
            usermood__user=user,
            usermood__mood_group=None
        )

        if not mood_qs:
            Response(status=status.HTTP_200_OK)

        page = self.paginate_queryset(mood_qs)
        serializer = self.get_serializer(page, many=True)

        return self.get_paginated_response(serializer.data)

    @staticmethod
    def _build_mood_from_validated_data(data):
        serializer = MoodSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        return MoodDto(
            status=data["status"],
            simple_summary=data["simple_summary"],
        )


class MoodListViewSet(mixins.CreateModelMixin,
                      mixins.ListModelMixin,
                      GenericViewSet):
    """
        - Mood (기분) 리스트 (유저 필터링)
        endpoint : /moods/list/
        참고 : 날짜 필터링이 아닌 user의 기분으로 필터링 (기획변경)
    """

    queryset = Mood.objects.all()
    serializer_class = MoodSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = CustomCursorPagination

    def list(self, request, *args, **kwargs) -> Response:
        self.pagination_class.ordering = '-id'
        self.pagination_class.cursor = self.request.query_params.get('cursor')

        user = self.request.user
        mood_qs = self.get_queryset().filter(
            usermood__user=user,
            usermood__mood_group=None
        )

        if not mood_qs:
            Response(status=status.HTTP_200_OK)

        page = self.paginate_queryset(mood_qs)
        serializer = self.get_serializer(page, many=True)

        return self.get_paginated_response(serializer.data)


class WeekMoodViewSet(mixins.CreateModelMixin,
                      mixins.ListModelMixin,
                      GenericViewSet):
    """
        - 최근 7일 Mood (기분)
          endpoint : /moods/week/
    """

    queryset = UserMood.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def list(self, request, *args, **kwargs) -> Response:
        user = self.request.user
        today = timezone.now() + timedelta(days=1)
        week_ago = today - timedelta(days=7)

        user_mood_qs = self.get_queryset().filter(
            created__range=[week_ago.date(), today.date()],
            user=user,
            mood_group=None,
            mood__is_day_last=True
        ).prefetch_related('mood')

        mood_list = self.get_week_mood(user_mood_qs, week_ago.day)
        data = {
            'mood_list': mood_list
        }

        return Response(data=data, status=status.HTTP_200_OK)

    @staticmethod
    def get_week_mood(user_mood_qs, day) -> list:
        week_mood_list = []
        user_mood_list = list(user_mood_qs)

        for _ in range(0, 7):
            matched_day = False

            for idx, user_mood in enumerate(user_mood_list):
                if day == user_mood.created.day:
                    week_mood_list.append(user_mood.mood.status)
                    user_mood_list.pop(idx)
                    matched_day = True
                    break

            if matched_day is False:
                week_mood_list.append(-1)

            day += 1

        return week_mood_list


class MonthMoodViewSet(mixins.CreateModelMixin,
                       mixins.ListModelMixin,
                       GenericViewSet):
    """
        - 1개월 Mood (기분)
          endpoint : /moods/<year>/<month>/
    """

    queryset = UserMood.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def list(self, request, *args, **kwargs) -> Response:
        user = self.request.user
        year = int(kwargs.get('year'))
        month = int(kwargs.get('month'))

        user_mood_qs = self.get_queryset().filter(
            created__year=year,
            created__month=month,
            user=user,
            mood_group=None,
            mood__is_day_last=True
        ).prefetch_related('mood')

        month_range, mood_list = self.get_month_mood(user_mood_qs, year, month)
        data = {
            'month_range': month_range,
            'mood_list': mood_list
        }

        return Response(data=data, status=status.HTTP_200_OK)

    @staticmethod
    def get_month_mood(user_mood_qs, year, month):
        month_range = monthrange(year, month)[1]
        month_mood_list = [-1 for _ in range(0, month_range)]

        for user_mood in user_mood_qs:
            month_mood_list[user_mood.created.day-1] = user_mood.mood.status

        return month_range, month_mood_list


class YearMoodViewSet(MonthMoodViewSet):
    """
        - 1년 Mood (기분)
          endpoint : /moods/<year>/
    """

    queryset = UserMood.objects.all()
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def list(self, request, *args, **kwargs) -> Response:
        user = self.request.user
        year = int(kwargs.get('year'))
        data = {}

        user_mood_qs = self.get_queryset().filter(
            created__year=year,
            user=user,
            mood_group=None,
            mood__is_day_last=True
        ).prefetch_related('mood')

        for month in range(1, 13):
            month_qs = user_mood_qs.filter(created__month=month)
            month_range, mood_list = self.get_month_mood(month_qs, year, month)
            data[month] = {
                'month_range': month_range,
                'mood_list': mood_list
            }

        return Response(data=data, status=status.HTTP_200_OK)
