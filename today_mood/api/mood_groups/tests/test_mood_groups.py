import mock
import pytest
from django.utils import timezone
from rest_framework import status
from rest_framework.reverse import reverse

from apps.mood_groups.models import MoodGroup, UserMoodGroup
from apps.moods.models import UserMood, Mood
from apps.users.models import User
from tests.request_helper import pytest_request

MOOD_FIELDS_LIST = ['id', 'status', 'simple_summary']


# Oauth2 인증 Mock 처리 ( TODO: Oauth2.0 도 테스트 될 수 있게 로직 추가해야함 )
@pytest.fixture(scope='function')
def mock_is_authenticated():
    with mock.patch('rest_framework.permissions.IsAuthenticatedOrReadOnly') as patch:
        yield patch


@pytest.mark.urls(urls='urls')
@pytest.mark.django_db
def test_group_create(rf, client, mock_is_authenticated):

    data = {
        'title': '5boon',
        'summary': '5boon 팀원들과의 기분 공유'
    }

    user = User.objects.create(
        username='test_user',
        name='test_name',
        password='test_pw'
    )

    url = reverse(viewname="mood_groups:group-list")
    response = pytest_request(rf,
                              method='post',
                              url=url,
                              user=user,
                              data=data)

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.urls(urls='urls')
@pytest.mark.django_db
def test_my_group_list(rf, client, mock_is_authenticated):
    user = User.objects.create(
        username='test_user',
        name='test_name',
        password='test_pw'
    )

    today = timezone.now()
    mood_group = MoodGroup.objects.create(
        created=today,
        modified=today,
        title='5boon',
        summary='5boon 팀원들과의 기분 공유'
    )

    UserMoodGroup.objects.create(
        user=user,
        mood_group=mood_group,
        is_reader=True
    )

    url = reverse(viewname="mood_groups:my_group-list")
    response = pytest_request(rf,
                              method='get',
                              url=url,
                              user=user)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.urls(urls='urls')
@pytest.mark.django_db
def test_my_group_list_detail(rf, client, mock_is_authenticated):
    user = User.objects.create(
        username='test_user',
        name='test_name',
        password='test_pw'
    )

    today = timezone.now()

    # 기분 생성
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

    # 그룹 생성
    mood_group = MoodGroup.objects.create(
        created=today,
        modified=today,
        title='5boon',
        summary='5boon 팀원들과의 기분 공유'
    )

    user_mood_group = UserMoodGroup.objects.create(
        user=user,
        mood_group=mood_group,
        is_reader=True
    )

    url = reverse(
        viewname="mood_groups:my_group-detail",
        kwargs={"pk": user_mood_group.id}
    )
    response = pytest_request(rf,
                              method='get',
                              url=url,
                              user=user)

    assert response.status_code == status.HTTP_200_OK
