from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.dispatch import receiver

class UsuariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'usuarios'
    
    def ready(self):
        # Importa o sinal para ser registrado
        import usuarios.signals    
