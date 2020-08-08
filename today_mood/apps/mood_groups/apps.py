from django.apps import AppConfig


class GroupConfig(AppConfig):
    name = 'mood_groups'

    def ready(self):
        import apps.moods.signals
