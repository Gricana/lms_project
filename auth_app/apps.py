from django.apps import AppConfig


class AuthAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'auth_app'
    verbose_name = 'Управление авторизацией'

    def ready(self):
        from .signals import grant_pupil_rights
