from apps.users.models import User


class InitTestData(object):
    def __init__(self):
        self.OAUTH2_CLIENT_KEY = None

    def create_user(self,
                    username='test_user',
                    name='test_name',
                    password='test_pw',
                    email='test@5boon.com'):

        user_data = User.objects.create(
            username=username,
            name=name,
            password=password,
            email=email
        )
        return user_data
