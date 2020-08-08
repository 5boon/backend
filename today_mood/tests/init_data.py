import hashlib

from apps.mood_groups.models import MoodGroup, UserMoodGroup
from apps.users.models import User


class InitTestData(object):

    def __init__(self):
        self.OAUTH2_CLIENT_KEY = None

    def create_user(self,
                    username: str = 'test_user',
                    name: str = 'test_name',
                    password: str = 'test_pw',
                    email: str = 'test@5boon.com') -> User:
        """
            User 생성
            - username
        """

        user_data = User.objects.create(
            username=username,
            name=name,
            password=password,
            email=email
        )
        return user_data

    def create_groups(self, user: User, title: str, summary: str):
        """
            Group 생성
            - user: User 객체
            - title: 그룹 타이틀
            - summary: 그룹 설명
        """

        if not isinstance(user, User):
            raise

        code = hashlib.sha256(title.encode()).hexdigest()
        mood_group = MoodGroup.objects.create(
            title=title,
            summary=summary,
            code=code
        )

        user_mood_group = UserMoodGroup.objects.create(
            user=user,
            mood_group=mood_group,
        )

        return mood_group, user_mood_group
