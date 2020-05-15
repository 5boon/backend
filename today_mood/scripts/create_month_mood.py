from calendar import monthrange
from random import choice, randint

from django.utils import timezone
from pip._vendor.distlib.compat import raw_input

from apps.moods.models import Mood, UserMood

THIS_YEAR = 2020
MOOD_LIST = [Mood.WORST, Mood.BAD, Mood.MOPE, Mood.SOSO, Mood.GOOD, Mood.BEST]
TEST_STRING_LIST = [
    '기분이~너무나~좋아요~^&^',
    '회사에서 실수를 했다:D',
    '날씨가 너무 좋다! ^_^',
    '한강 Gang Gang Gang!',
    '5boon(오늘의 기분) 가즈아!',
    '토이프로젝트는 정말 재밌다^__^'
]


def create_sample_month_mood(month: int, user_id: int):
    date = timezone.now().replace(year=THIS_YEAR, month=month, day=1)
    month_range = monthrange(THIS_YEAR, month)[1]

    for day in range(1, month_range + 1):
        user_mood_list = []
        rand_int = randint(0, 4)
        for _ in range(0, rand_int + 1):
            mood = Mood(
                status=choice(MOOD_LIST),
                simple_summary=choice(TEST_STRING_LIST),
                is_day_last=True if _ == rand_int else False
            )
            mood.save()

            user_mood_list.append(
                UserMood(
                    created=date.replace(day=day),
                    modified=date.replace(day=day),
                    user_id=user_id,
                    mood=mood,
                    mood_group=None,
                    do_show_summary=True
                )
            )

        if user_mood_list:
            UserMood.objects.bulk_create(user_mood_list)


def create_sample_year_mood(user_id: int, start_month: int = 1, end_month: int = 12):
    for month in range(start_month, end_month + 1):
        create_sample_month_mood(month, user_id)


def run():
    while True:
        try:
            user_id = int(raw_input("* 샘플 기분을 생성할 user_id를 입력하세요: "))
        except Exception as e:
            print('잘못 입력하셨습니다. 숫자만 입력됩니다.')
            return

        while True:
            create_month_type = raw_input("* 1개월치 생성은 [a], n 개월치 생성은 [b]: ")
            if create_month_type.lower() in ('a', 'b'):
                break

        if create_month_type == 'a':
            while True:
                try:
                    month = int(raw_input("* 생성할 월을 입력하세요: "))
                except Exception as e:
                    print('잘못 입력하셨습니다. 숫자만 입력됩니다.')
                    return

                if 1 <= month <= 12:
                    create_sample_month_mood(month, user_id)
                    print('[----- END -----]')
                    return

        elif 'b':
            while True:
                month_range = raw_input("* 생성할 월 범위를 입력하세요(ex: 2~3) : ")

                try:
                    _month_range = month_range.split('~')
                    start_month = int(_month_range[0])
                    end_month = int(_month_range[1])
                except Exception as e:
                    print('잘못 입력하셨습니다. 숫자만 입력됩니다.')
                    return

                if 1 <= start_month <= 12 and 1 <= end_month <= 12 and start_month < end_month:
                    create_sample_year_mood(user_id, start_month, end_month)
                    print('[----- END -----]')
                    return
