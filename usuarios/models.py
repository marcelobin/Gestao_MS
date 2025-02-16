from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver


def validate_cpf(value):
    if not value.isdigit() or len(value) != 11:
        raise ValidationError("CPF inválido.")


class Filial(models.Model):
    ds_filial = models.CharField("Filial", max_length=45, null=True, blank=True)

    def __str__(self):
        return self.ds_filial or f"Filial {self.id}"


class Perfil(models.Model):
    ADMINISTRADOR = "ADMINISTRADOR"
    MESA_OPERACOES = "MESA_OPERACOES"
    OPERADOR = "OPERADOR"

    PERFIS_CHOICES = [
        (ADMINISTRADOR, "Administrador"),
        (MESA_OPERACOES, "Mesa de Operações"),
        (OPERADOR, "Operador"),
    ]

    ds_perfil = models.CharField(
        "Perfil de Acesso",
        max_length=45,
        choices=PERFIS_CHOICES,
        unique=True
    )

    def __str__(self):
        return self.ds_perfil


class Operador(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="operador"
    )
    nm_operador = models.CharField("Nome", max_length=60, null=True, blank=True)
    cpf_operador = models.CharField(
        "CPF", max_length=14, null=True, blank=True, validators=[validate_cpf]
    )
    dt_nascimento = models.DateField("Data de Nascimento", null=True, blank=True)
    cel_operador = models.CharField("Celular", max_length=15, null=True, blank=True)
    email_operador = models.EmailField("E-Mail", max_length=60, null=True, blank=True)
    filial = models.ForeignKey(
        Filial,
        on_delete=models.CASCADE,
        related_name="operadores",
        null=True,
        blank=True
    )
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE)

    def __str__(self):
        if self.nm_operador:
            partes_nome = self.nm_operador.split()
            return f"{partes_nome[0]} {partes_nome[-1]}" if len(partes_nome) > 1 else self.nm_operador
        return f"Operador {self.id}"

    def save(self, *args, **kwargs):
        """
        Sobrescreve o método save() para garantir que,
        sempre que o Operador for salvo, ajustamos o usuário
        para superusuário/staff se o perfil for Administrador.
        """
        if self.perfil.ds_perfil == Perfil.ADMINISTRADOR:
            self.user.is_superuser = True
            self.user.is_staff = True
        else:
            self.user.is_superuser = False
            self.user.is_staff = False

        self.user.save()  # Salva as mudanças no User
        super().save(*args, **kwargs)  # Salva o Operador


@receiver(post_save, sender=User)
def criar_operador_para_admin(sender, instance, created, **kwargs):
    """
    Se um usuário for criado como superusuário, criamos automaticamente
    um Operador com perfil de Administrador (caso ainda não exista).
    """
    if created and instance.is_superuser:
        perfil_admin, _ = Perfil.objects.get_or_create(ds_perfil=Perfil.ADMINISTRADOR)
        # Cria automaticamente um Operador vinculado ao user
        Operador.objects.create(
            user=instance,
            nm_operador=instance.username,
            perfil=perfil_admin
        )
