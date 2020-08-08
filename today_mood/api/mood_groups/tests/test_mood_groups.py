import hashlib

import mock
import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from apps.mood_groups.models import UserMoodGroup
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
def test_group_create(rf, client, user_context, mock_is_authenticated):

    data = {
        'title': '5boon',
        'summary': '5boon 팀원들과의 기분 공유'
    }

    user = user_context.init.create_user()

    url = reverse(viewname="mood_groups:group-list")
    response = pytest_request(rf,
                              method='post',
                              url=url,
                              user=user,
                              data=data)

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.urls(urls='urls')
@pytest.mark.django_db
def test_my_group_list(rf, client, user_context, mock_is_authenticated):
    user = user_context.init.create_user()
    user_context.init.create_groups(
        user=user,
        title='5boon',
        summary='5boon 팀원들과의 기분 공유'
    )

    url = reverse(viewname="mood_groups:my_group-list")
    response = pytest_request(rf,
                              method='get',
                              url=url,
                              user=user)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.urls(urls='urls')
@pytest.mark.django_db
def test_my_group_delete(rf, client, user_context, mock_is_authenticated):
    user = user_context.init.create_user()
    # 그룹 생성
    mood_group, user_mood_group = user_context.init.create_groups(
        user=user,
        title='5boon',
        summary='5boon 팀원들과의 기분 공유'
    )

    guest = User.objects.create(
        username='test_guest',
        name='test_guest',
        password='test_pw'
    )

    # user 기분 생성
    mood = Mood.objects.create(status=Mood.GOOD, simple_summary='test')
    UserMood.objects.create(user=user, mood=mood)

    # guest 기분 생성
    guest_mood = Mood.objects.create(status=Mood.BAD, simple_summary='guest mood summary')
    UserMood.objects.create(user=guest, mood=guest_mood)
    UserMood.objects.create(
        user=guest,
        mood=guest_mood,
        mood_group=mood_group
    )

    # 그룹에 게스트 추가
    UserMoodGroup.objects.create(
        user=guest,
        mood_group=mood_group,
    )

    url = reverse(
        viewname="mood_groups:my_group-detail",
        kwargs={"pk": user_mood_group.id}
    )
    response = pytest_request(rf,
                              method='delete',
                              url=url,
                              user=user)

    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not UserMoodGroup.objects.filter(id=user_mood_group.id).exists()


@pytest.mark.urls(urls='urls')
@pytest.mark.django_db
def test_my_group_list_detail(rf, client, user_context, mock_is_authenticated):
    user = user_context.init.create_user()
    # 그룹 생성
    mood_group, user_mood_group = user_context.init.create_groups(
        user=user,
        title='5boon',
        summary='5boon 팀원들과의 기분 공유'
    )

    guest = User.objects.create(
        username='test_guest',
        name='test_guest',
        password='test_pw'
    )

    # user 기분 생성
    mood = Mood.objects.create(status=Mood.GOOD, simple_summary='test')
    UserMood.objects.create(user=user, mood=mood)

    # guest 기분 생성
    guest_mood = Mood.objects.create(status=Mood.BAD, simple_summary='guest mood summary')
    UserMood.objects.create(user=guest, mood=guest_mood)
    UserMood.objects.create(
        user=guest,
        mood=guest_mood,
        mood_group=mood_group
    )

    # 그룹에 게스트 추가
    UserMoodGroup.objects.create(
        user=guest,
        mood_group=mood_group,
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


@pytest.mark.urls(urls='urls')
@pytest.mark.django_db
def test_invitation_join(rf, client, user_context, mock_is_authenticated):
    user = user_context.init.create_user()
    title = '5boon'
    user_context.init.create_groups(
        user=user,
        title=title,
        summary='5boon 팀원들과의 기분 공유'
    )

    # 게스트 추가
    guest = User.objects.create(
        username='test_guest',
        name='test_guest',
        password='test_pw'
    )

    data = {
        'code': hashlib.sha256(title.encode()).hexdigest(),
    }

    url = reverse(
        viewname="mood_groups:invitation-list",
    )
    response = pytest_request(rf,
                              method='post',
                              url=url,
                              user=guest,
                              data=data)

    assert response.status_code == status.HTTP_201_CREATED
