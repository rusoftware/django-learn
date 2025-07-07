from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    # def ready(self):
    #     from .models import ContactGroup
    #     ContactGroup.objects.get_or_create(name='Clients')
