import hashlib

import pytest

from apps.mood_groups.models import MoodGroup
from scripts.insert_group_code import insert_group_code


@pytest.mark.urls(urls='urls')
@pytest.mark.django_db
def test_insert_group_code(rf, client, user_context):
    """
        code가 없는 그룹에 code 넣어주는 스크립트
    """

    title = '5boon_test_group'
    MoodGroup.objects.create(
        title=title,
        summary='test_summary',
        code=''
    )

    code = hashlib.sha256(title.encode()).hexdigest()
    assert not MoodGroup.objects.filter(code=code).exists()
    insert_group_code()
    assert MoodGroup.objects.filter(code=code).exists()
