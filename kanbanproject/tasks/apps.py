from django.apps import AppConfig

class TasksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'kanbanproject.tasks'

    def ready(self):
        from . import signals
