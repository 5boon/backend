from apps.users.models import User


class InitTestData(object):
    def __init__(self):
        self.OAUTH2_CLIENT_KEY = None

    def create_test_user(self):
        user_data = User.objects.create(
            username='test_user',
            name='test_name',
            password='test_pw'
        )
        return user_data
