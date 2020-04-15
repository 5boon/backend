import mock

import pytest
from rest_framework import status

from rest_framework.reverse import reverse

from apps.users.models import User


# Oauth2 인증 Mock 처리 ( TODO: Oauth2.0 도 테스트 될 수 있게 로직 추가해야함 )
from tests.request_helper import pytest_request


@pytest.fixture(scope='function')
def mock_is_authenticated():
    with mock.patch('rest_framework.permissions.IsAuthenticated') as patch:
        yield patch


@pytest.fixture(scope='function')
def mock_update_employment_center_name():
    with mock.patch('api.users.views.notify_slack') as patch:
        yield patch


@pytest.fixture(scope='function')
def mock_send_pw_email():
    with mock.patch('api.users.views.send_pw_email') as patch:
        yield patch


@pytest.mark.urls(urls='urls')
@pytest.mark.django_db
def test_user_register(rf, client, mock_update_employment_center_name):
    url = reverse(viewname="users:user_register")

    data = {
        'username': 'test',
        'password': '111111',
        'name': 'name',
        'email': '5boon@gmail.com'
    }

    response = pytest_request(rf,
                              method='post',
                              url=url,
                              user=None,
                              data=data)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data.get('username') == data.get('username')
    assert response.data.get('name') == data.get('name')


@pytest.mark.urls(urls='urls')
@pytest.mark.django_db
def test_user_password_find(rf, client, user_context, mock_send_pw_email):
    url = reverse(viewname="users:user_password")

    user = user_context.init.create_user()

    data = {
        'username': user.username,
        'email': user.email
    }

    response = pytest_request(rf,
                              method='post',
                              url=url,
                              user=user,
                              data=data)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.urls(urls='urls')
@pytest.mark.django_db
def test_user_password_update(rf, client, user_context, mock_is_authenticated):
    user = user_context.init.create_user()

    data = {
        'new_password': 'new_pw'
    }

    url = reverse(viewname="users:user_password")
    response = pytest_request(rf,
                              method='patch',
                              url=url,
                              data=data,
                              user=user)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.urls(urls='urls')
@pytest.mark.django_db
def test_user_id_find(rf, client, user_context, mock_send_pw_email):
    url = reverse(viewname="users:user_id")

    user = user_context.init.create_user()
    data = {
        'name': user.name,
        'email': user.email
    }

    response = pytest_request(rf,
                              method='post',
                              url=url,
                              user=user,
                              data=data)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.urls(urls='urls')
@pytest.mark.django_db
def test_user_email_check(rf, client, user_context, mock_send_pw_email):
    url = reverse(viewname="users:user_check")

    user = user_context.init.create_user()
    data = {
        'email': user.email
    }

    response = pytest_request(rf,
                              method='get',
                              url=url,
                              user=user,
                              data=data)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.urls(urls='urls')
@pytest.mark.django_db
@pytest.mark.parametrize(
    'social_type',
    ['kakao', 'apple']
)
def test_sns_first_login(rf, client, user_context, social_type):
    """
        data 는 클라이언트에서 소셜인증으로 받아온 데이터를 가져온다.
        첫 로그인시 user 생성
    """

    url = reverse(viewname="users:user_sns")
    data = {
        'type': social_type,
        'unique_id': 1234567,
        'email': 'test@5boon.com',
        'name': '5boon_user'
    }

    response = pytest_request(rf,
                              method='post',
                              url=url,
                              data=data)

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.urls(urls='urls')
@pytest.mark.django_db
@pytest.mark.parametrize(
    'social_type',
    ['kakao', 'apple']
)
def test_sns_login(rf, client, user_context, social_type):
    """
        data 는 클라이언트에서 소셜인증으로 받아온 데이터를 가져온다.
    """

    url = reverse(viewname="users:user_sns")
    data = {
        'type': social_type,
        'unique_id': 1234567,
        'email': 'test@5boon.com',
        'name': '5boon_user'
    }

    User.objects.create(
        username='{}-{}'.format(data.get('type'), data.get('unique_id')),
        name=data.get('name'),
        password=data.get('unique_id'),
        email=data.get('email'),
    )

    response = pytest_request(rf,
                              method='post',
                              url=url,
                              data=data)

    assert response.status_code == status.HTTP_200_OK
