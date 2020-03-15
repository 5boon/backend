import pytest

from apps.users.models import User


@pytest.fixture(scope='function')
def user_context(db):
    user = User.objects.create(
        username='test_user',
        nickname='test_nickname',
        password='test_pw'
    )

    # 이름(문자열), 기반 클래스 튜플, 속성과 메서드 딕셔너리
    ret_data = {
        'user': user,
    }
    ret = type('context', (), ret_data)

    return ret
