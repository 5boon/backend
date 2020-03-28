import mock
import pytest
from django.utils import timezone
from rest_framework import status
from rest_framework.reverse import reverse

from apps.moods.models import UserMood, Mood
from apps.users.models import User
from tests.request_helper import pytest_request

MOOD_FIELDS_LIST = ['id', 'status', 'simple_summary', 'do_show_summary']


# Oauth2 인증 Mock 처리 ( TODO: Oauth2.0 도 테스트 될 수 있게 로직 추가해야함 )
@pytest.fixture(scope='function')
def mock_is_authenticated():
    with mock.patch('rest_framework.permissions.IsAuthenticatedOrReadOnly') as patch:
        yield patch


@pytest.mark.urls(urls='urls')
@pytest.mark.django_db
@pytest.mark.parametrize(
    'mood_status',
    [0, 1, 2, 3, 4]
)
def test_today_mood_create(rf, client, mood_status, mock_is_authenticated):
    data = {
        "status": mood_status,
        "simple_summary": "테스트 기분"
    }

    user = User.objects.create(
        username='test_user',
        nickname='test_nickname',
        password='test_pw'
    )

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
def test_no_today_mood_list(rf, client, mock_is_authenticated):
    user = User.objects.create(
        username='test_user',
        nickname='test_nickname',
        password='test_pw'
    )

    url = reverse(viewname="moods:today_mood")
    response = pytest_request(rf,
                              method='get',
                              url=url,
                              user=user)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.urls(urls='urls')
@pytest.mark.django_db
def test_today_mood_list(rf, client, mock_is_authenticated):
    user = User.objects.create(
        username='test_user',
        nickname='test_nickname',
        password='test_pw'
    )

    today = timezone.localtime()

    mood = Mood.objects.create(
        status=0,
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
    assert list(response.data[0].keys()) == MOOD_FIELDS_LIST
