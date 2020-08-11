import pytest

from apps.moods.models import UserMood
from scripts.create_month_mood import create_sample_month_mood, create_sample_year_mood


@pytest.mark.urls(urls='urls')
@pytest.mark.django_db
def test_create_sample_month_mood(rf, client, user_context):
    """
        샘플 기분 만드는 스크립트 테스트
    """

    user = user_context.init.create_user()
    user_context.init.create_groups(
        user=user,
        title='5boon',
        summary='5boon 팀원들과의 기분 공유'
    )

    assert not UserMood.objects.filter(user_id=user.id).exists()
    create_sample_month_mood(user_id=user.id, year=2020, month=1)
    assert UserMood.objects.filter(user_id=user.id).exists()


@pytest.mark.urls(urls='urls')
@pytest.mark.django_db
def test_create_sample_year_mood(rf, client, user_context):
    """
        샘플 기분 만드는 스크립트 테스트
    """

    user = user_context.init.create_user()
    user_context.init.create_groups(
        user=user,
        title='5boon',
        summary='5boon 팀원들과의 기분 공유'
    )

    assert not UserMood.objects.filter(user_id=user.id).exists()
    create_sample_year_mood(user_id=user.id, year=2020)
    for month in range(1, 12):
        assert UserMood.objects.filter(user_id=user.id, created__day=month).exists()
