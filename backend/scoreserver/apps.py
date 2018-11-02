from django.apps import AppConfig


class ScoreserverConfig(AppConfig):
    name = 'scoreserver'

    def ready(self):
        from scoreserver.signals import correct_submission_handler, incorrect_submission_handler
