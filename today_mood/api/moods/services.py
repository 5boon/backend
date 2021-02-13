from dataclasses import dataclass

from django.utils import timezone

from api.moods.exceptions import LimitTodayMood
from api.moods.serializers import MoodSerializer
from apps.mood_groups.models import UserMoodGroup
from apps.moods.models import UserMood, Mood


MOOD_LIMITED_COUNT = 1000


@dataclass
class MoodDto:
    status: int # 기분(상태)
    simple_summary: str # 기분 설명


class MoodManageService(object):

    def __init__(self, request):
        self.user = request.user
        self.show_summary_group_ids = request.data.get('group_list', [])  # 기분 설명(summary) 보여줄 그룹

    def update_my_mood(self, mood: MoodDto) -> dict:
        self.check_today_mood_limit()

        mood_group_create_list = []

        new_mood = Mood.objects.create(
            status=mood.status,
            simple_summary=mood.simple_summary,
            is_day_last=False,
        )

        # 그룹과 별개로, 개인 기분(mood) 생성 - 그룹이 없을수도 있어서, mood_group=None 을 기본으로 생성
        UserMood.objects.create(
            mood_id=new_mood.id,
            user_id=self.user.id,
            mood_group=None
        )

        # 현재 속한 그룹 리스트 가져옴
        mood_group_ids = list(UserMoodGroup.objects.filter(
            user_id=self.user.id
        ).values_list('mood_group_id', flat=True))

        # 내가속한 그룹에 기분을 저장
        for mood_group_id in mood_group_ids:
            mood_group_create_list.append(
                UserMood(
                    do_show_summary=True if mood_group_id in self.show_summary_group_ids else False,
                    mood_group_id=mood_group_id,
                    user_id=self.user.id,
                    mood_id=new_mood.id
                )
            )

        if mood_group_create_list:
            UserMood.objects.bulk_create(mood_group_create_list)

        return MoodSerializer(instance=new_mood).data

    def check_today_mood_limit(self):
        today = timezone.now()

        user_mood_count = UserMood.objects.filter(
            user_id=self.user.id,
            created__date=today.date(),
            mood_group=None
        ).count()

        if user_mood_count > MOOD_LIMITED_COUNT:
            raise LimitTodayMood
