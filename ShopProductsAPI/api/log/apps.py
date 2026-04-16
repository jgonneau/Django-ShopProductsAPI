from django.apps import AppConfig


class LogConfig(AppConfig):
    name = 'api.log'

    def ready(self):
        import api.log.signals  # noqa: F401
