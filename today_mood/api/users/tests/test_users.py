import pytest
from rest_framework import status

from rest_framework.reverse import reverse


@pytest.mark.urls(urls='urls')
@pytest.mark.django_db
def test_user_register(rf, client):
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
