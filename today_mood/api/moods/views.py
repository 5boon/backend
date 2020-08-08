from calendar import monthrange
from datetime import datetime, timedelta

from django.utils import timezone
from rest_framework import permissions, mixins, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.moods.serializers import MoodSerializer
from api.pagination import CustomCursorPagination
from apps.mood_groups.models import UserMoodGroup
from apps.moods.models import Mood, UserMood
from utils.slack import slack_notify_new_mood

MOOD_LIMITED_COUNT = 1000
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
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    pagination_class = CustomCursorPagination

    def perform_create(self, serializer) -> dict:
        """
            - show_summary_group_list 가 empty list 이면 전체 공개
        """

        today = timezone.now()
        user = self.request.user
        mood_group_create_list = []
        show_summary_group_list = self.request.data.get('group_list', [])  # 기분 설명(summary) 보여줄 그룹

        user_mood_count = UserMood.objects.filter(
            user=user,
            created__date=today.date(),
            mood_group=None
        ).count()

        # 오늘 기분 생성
        if user_mood_count < MOOD_LIMITED_COUNT:
            # 현재 속한 그룹 리스트 가져옴
            mood_group_ids = list(UserMoodGroup.objects.filter(
                user=user
            ).values_list('mood_group_id', flat=True))

            if not self.is_my_group(show_summary_group_list, mood_group_ids):
                raise PermissionDenied

            mood = serializer.save()

            # 그룹과 별개로, 개인 기분(mood) 생성 - 그룹이 없을수도 있어서, mood_group=None 을 기본으로 생성
            UserMood.objects.create(
                mood=mood,
                user=self.request.user,
                mood_group=None
            )

            for mood_group_id in mood_group_ids:
                do_show_summary = False

                if mood_group_id in show_summary_group_list:
                    do_show_summary = True

                mood_group_create_list.append(
                    UserMood(
                        do_show_summary=do_show_summary,
                        mood_group_id=mood_group_id,
                        user=user,
                        mood=mood
                    )
                )

            if mood_group_create_list:
                UserMood.objects.bulk_create(mood_group_create_list)

        else:
            err_data = {
                'err_code': 'limited',
                'description': 'You have exceeded 100 moods.'
            }
            return err_data

        return self.get_serializer(instance=mood).data

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
    def is_my_group(groups: list, my_groups: list) -> bool:
        other_group = set(groups) - set(my_groups)

        if other_group:
            return False
        else:
            return True


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
