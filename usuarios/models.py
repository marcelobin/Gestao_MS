#usuarios/models.py

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


# Função de Validação de CPF
def validate_cpf(value):
    if not value.isdigit() or len(value) != 11:
        raise ValidationError("CPF inválido.")


# Filiais e Operadores
class Filial(models.Model):
    ds_filial = models.CharField("Filial", max_length=45, null=True, blank=True)

    def __str__(self):
        return self.ds_filial or f"Filial {self.id}"


class Perfil(models.Model):
    ds_perfil = models.CharField("Perfil de Acesso", max_length=45)

    def __str__(self):
        return self.ds_perfil


class Operador(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='operador')
    nm_operador = models.CharField("Nome", max_length=60, null=True, blank=True)
    cpf_operador = models.CharField("CPF", max_length=11, null=True, blank=True, validators=[validate_cpf])
    dt_nascimento = models.DateField("Data de Nascimento", null=True, blank=True)
    cel_operador = models.CharField("Celular", max_length=11, null=True, blank=True)
    email_operador = models.EmailField("E-Mail", max_length=60, null=True, blank=True)
    filial = models.ForeignKey(Filial, on_delete=models.CASCADE, related_name="operadores")
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE)

    def __str__(self):
        if self.nm_operador:
            partes_nome = self.nm_operador.split()
            if len(partes_nome) > 1:
                return f"{partes_nome[0]} {partes_nome[-1]}"
            return self.nm_operador  # Retorna o nome completo se não houver sobrenome
        return f"Operador {self.id}"
