from rest_framework.exceptions import APIException


class LimitTodayMood(Exception):
    def __str__(self):
        return "limit today mood(1000)"


class ServiceUnavailable(APIException):
    status_code = 503
    default_detail = 'You have exceeded 1000 moods.'
    default_code = 'mood_limited'
