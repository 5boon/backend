from django.apps import AppConfig


class MoodConfig(AppConfig):
    name = 'moods'

    def ready(self):
        import apps.moods.signals
