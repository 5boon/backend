import pytest

from tests.init_data import InitTestData


@pytest.fixture(scope='function')
def user_context(db):
    ic = InitTestData()

    # 이름(문자열), 기반 클래스 튜플, 속성과 메서드 딕셔너리
    ret_data = {
        'init': ic,
    }
    ret = type('context', (), ret_data)

    return ret
