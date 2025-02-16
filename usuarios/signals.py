# usuarios/signals.py
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.conf import settings

from .models import Perfil

@receiver(post_migrate)
def criar_perfis_padrao(sender, **kwargs):
    # Garante que rode apenas para a app 'usuarios'
    if sender.name == 'usuarios':
        PERFIS_INICIAIS = ["ADMINISTRADOR", "MESA_OPERACOES", "OPERADOR"]
        for valor in PERFIS_INICIAIS:
            Perfil.objects.get_or_create(ds_perfil=valor)
