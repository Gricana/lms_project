from django.apps import AppConfig


class LearningConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'learning'
    verbose_name = 'Управление обучением'

    def ready(self):
        from .signals import check_quantity
