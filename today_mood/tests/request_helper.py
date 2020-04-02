from urllib.parse import urlencode

from django.contrib.sessions.backends.cache import SessionStore
from django.urls import resolve
from rest_framework.test import force_authenticate


def pytest_request(rf, method, url, user, data=None, token=None):
    """
        : Test 를 위한 request 생성하는 함수
        - rf 설명: https://pytest-django.readthedocs.io/en/latest/helpers.html#rf-requestfactory
    """

    content_type = 'application/json'
    caller = getattr(rf, method)
    request = caller(path=url, data=data, content_type=content_type)

    if not hasattr(request, 'session'):
        setattr(request, 'session', SessionStore())

    # Oauth2.0 test 로직 구현 안되서 login 안하고 바로 넣어줌
    force_authenticate(
        request=request,
        user=user,
        token=token
    )
    request.user = user

    # 실제 호출하는 url 에 대한 view 정보를 가져옴
    resolver_match = resolve(url)
    test_func, test_args, test_kwargs = resolver_match
    request.resolver_match = resolver_match
    response = test_func(request, *test_args, **test_kwargs)

    return response
