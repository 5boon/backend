import mock
import pytest
from django.utils import timezone
from rest_framework import status
from rest_framework.reverse import reverse

from apps.mood_groups.models import UserMoodGroup, MoodGroup
from apps.moods.models import UserMood, Mood
from tests.request_helper import pytest_request

MOOD_FIELDS_LIST = ['id', 'created', 'status', 'simple_summary']
DAY_MOOD_FIELDS_LIST = ['next', 'previous', 'results']
MONTH_MOOD_FIELDS_LIST = ['month_range', 'mood_list']
WEEK_MOOD_FIELDS_LIST = ['mood_list']


# Oauth2 인증 Mock 처리 ( TODO: Oauth2.0 도 테스트 될 수 있게 로직 추가해야함 )
@pytest.fixture(scope='function')
def mock_is_authenticated():
    with mock.patch('rest_framework.permissions.IsAuthenticatedOrReadOnly') as patch:
        yield patch


@pytest.mark.urls(urls='urls')
@pytest.mark.django_db
@pytest.mark.parametrize(
    'mood_status',
    [Mood.BAD, Mood.GOOD, Mood.BEST, Mood.MOPE, Mood.SOSO, Mood.WORST]
)
def test_today_mood_create(rf, client, user_context, mood_status, mock_is_authenticated):
    user = user_context.init.create_user()
    # 그룹 생성
    mood_group, user_mood_group = user_context.init.create_groups(
        user=user,
        title='5boon',
        summary='5boon 팀원들과의 기분 공유'
    )

    data = {
        "status": mood_status,
        "simple_summary": "테스트 기분",
        "group_list": [mood_group.id]
    }

    url = reverse(viewname="moods:today_mood")
    response = pytest_request(rf,
                              method='post',
                              url=url,
                              user=user,
                              data=data)

    assert response.status_code == status.HTTP_201_CREATED
    assert list(response.data.keys()) == MOOD_FIELDS_LIST


@pytest.mark.urls(urls='urls')
@pytest.mark.django_db
def test_no_today_mood_list(rf, client, user_context, mock_is_authenticated):
    user = user_context.init.create_user()

    url = reverse(viewname="moods:today_mood")
    response = pytest_request(rf,
                              method='get',
                              url=url,
                              user=user)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.urls(urls='urls')
@pytest.mark.django_db
@pytest.mark.parametrize(
    'mood_status',
    [Mood.BAD, Mood.GOOD, Mood.BEST, Mood.MOPE, Mood.SOSO, Mood.WORST]
)
def test_today_mood_list(rf, client, user_context, mock_is_authenticated, mood_status):
    user = user_context.init.create_user()

    today = timezone.now()

    mood = Mood.objects.create(
        status=mood_status,
        simple_summary='test'
    )

    UserMood.objects.create(
        created=today,
        modified=today,
        user=user,
        mood=mood
    )

    url = reverse(viewname="moods:today_mood")
    response = pytest_request(rf,
                              method='get',
                              url=url,
                              user=user)

    assert response.status_code == status.HTTP_200_OK
    assert list(response.data.keys()) == DAY_MOOD_FIELDS_LIST


@pytest.mark.urls(urls='urls')
@pytest.mark.django_db
@pytest.mark.parametrize(
    'mood_status',
    [Mood.BAD, Mood.GOOD, Mood.BEST, Mood.MOPE, Mood.SOSO, Mood.WORST]
)
def test_user_mood_list(rf, client, user_context, mock_is_authenticated, mood_status):
    user = user_context.init.create_user()

    today = timezone.now()

    mood = Mood.objects.create(
        status=mood_status,
        simple_summary='test'
    )

    UserMood.objects.create(
        created=today,
        modified=today,
        user=user,
        mood=mood
    )

    url = reverse(viewname="moods:mood_list")
    response = pytest_request(rf,
                              method='get',
                              url=url,
                              user=user)

    assert response.status_code == status.HTTP_200_OK
    assert list(response.data.keys()) == DAY_MOOD_FIELDS_LIST


@pytest.mark.urls(urls='urls')
@pytest.mark.django_db
@pytest.mark.parametrize(
    'mood_status',
    [Mood.BAD, Mood.GOOD, Mood.BEST, Mood.MOPE, Mood.SOSO, Mood.WORST]
)
def test_month_mood_list(rf, client, user_context, mock_is_authenticated, mood_status):
    user = user_context.init.create_user()
    today = timezone.now()

    mood = Mood.objects.create(
        status=mood_status,
        simple_summary='test'
    )

    UserMood.objects.create(
        created=today,
        modified=today,
        user=user,
        mood=mood
    )

    url = reverse(
        viewname="moods:month_mood",
        kwargs={
            'year': 2020,
            'month': 5
        }
    )
    response = pytest_request(rf,
                              method='get',
                              url=url,
                              user=user)

    assert response.status_code == status.HTTP_200_OK
    assert list(response.data.keys()) == MONTH_MOOD_FIELDS_LIST


@pytest.mark.urls(urls='urls')
@pytest.mark.django_db
@pytest.mark.parametrize(
    'mood_status',
    [Mood.BAD, Mood.GOOD, Mood.BEST, Mood.MOPE, Mood.SOSO, Mood.WORST]
)
def test_week_mood_list(rf, client, user_context, mock_is_authenticated, mood_status):
    user = user_context.init.create_user()
    today = timezone.now()

    mood = Mood.objects.create(
        status=mood_status,
        simple_summary='test'
    )

    UserMood.objects.create(
        created=today,
        modified=today,
        user=user,
        mood=mood
    )

    url = reverse(viewname="moods:week_mood")
    response = pytest_request(rf,
                              method='get',
                              url=url,
                              user=user)

    assert response.status_code == status.HTTP_200_OK
    assert list(response.data.keys()) == WEEK_MOOD_FIELDS_LIST


@pytest.mark.urls(urls='urls')
@pytest.mark.django_db
@pytest.mark.parametrize(
    'mood_status',
    [Mood.BAD, Mood.GOOD, Mood.BEST, Mood.MOPE, Mood.SOSO, Mood.WORST]
)
def test_year_mood_list(rf, client, user_context, mock_is_authenticated, mood_status):
    user = user_context.init.create_user()
    today = timezone.now()

    mood = Mood.objects.create(
        status=mood_status,
        simple_summary='test'
    )

    UserMood.objects.create(
        created=today,
        modified=today,
        user=user,
        mood=mood
    )

    url = reverse(
        viewname="moods:year_mood",
        kwargs={
            'year': 2020,
        }
    )
    response = pytest_request(rf,
                              method='get',
                              url=url,
                              user=user)

    assert response.status_code == status.HTTP_200_OK
