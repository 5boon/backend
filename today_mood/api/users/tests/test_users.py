import mock

import pytest
from rest_framework import status

from rest_framework.reverse import reverse


@pytest.fixture(scope='function')
def mock_update_employment_center_name():
    with mock.patch('api.users.views.notify_slack') as patch:
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

    response = client.post(url, data=data)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data.get('username') == data.get('username')
    assert response.data.get('nickname') == data.get('nickname')
