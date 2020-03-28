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
        'nickname': 'test_nickname'
    }

    response = pytest_request(rf,
                              method='post',
                              url=url,
                              user=None,
                              data=data)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data.get('username') == data.get('username')
    assert response.data.get('nickname') == data.get('nickname')


@pytest.mark.urls(urls='urls')
@pytest.mark.django_db
def test_password_find(rf, client, mock_send_pw_email):
    url = reverse(viewname="users:user_password")

    user = User.objects.create(
        username='test_user',
        nickname='test_nickname',
        password='test_pw',
        email='test@5boon.com'
    )

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
def test_password_update(rf, client, mock_is_authenticated):
    user = User.objects.create(
        username='test_user',
        nickname='test_nickname',
        password='test_pw',
        email='test@5boon.com'
    )

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
