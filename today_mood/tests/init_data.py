import base64

from apps.users.models import User


class InitTestData(object):
    def __init__(self):
        self.OAUTH2_CLIENT_KEY = None

    def create_test_user(self):
        user_data = User.objects.create(
            username='test_user',
            nickname='test_nickname',
            password='test_pw'
        )
        return user_data
