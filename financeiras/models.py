from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Financeira(models.Model):
    nome_financeira = models.CharField("Financeira", max_length=50)
    cnpj = models.CharField("CNPJ", max_length=14, unique=True)

    def __str__(self):
        return self.nome_financeira


class Departamento(models.Model):
    nome_departamento = models.CharField("Departamento", max_length=50, null=True, blank=True)
    telefone_fixo = models.CharField("Telefone Fixo", max_length=15, null=True, blank=True)
    celular = models.CharField("Celular", max_length=15, null=True, blank=True)
    email = models.EmailField("E-mail", max_length=100, null=True, blank=True)
    financeira = models.ForeignKey(
        Financeira,
        on_delete=models.CASCADE,
        related_name="departamentos"
    )


    def __str__(self):
        return self.nome_departamento or "Departamento Sem Nome"


class Modalidade(models.Model):
    """ Ex.: 'Financiamento', 'Refinanciamento' """
    nome_modalidade = models.CharField("Modalidade", max_length=50, unique=True,  blank=True, default="Sem Nome")

    def __str__(self):
        return self.nome_modalidade


class Segmento(models.Model):
    """ Ex.: 'Veículos Leves', 'Veículos Pesados' """
    modalidade = models.ForeignKey(
        Modalidade,
        on_delete=models.CASCADE,
        related_name="modalidades"
    )
    nome_segmento = models.CharField("Segmento", max_length=50,  blank=True, default="Sem Nome")

    def __str__(self):
        return f"{self.nome_segmento}"


class Produto(models.Model):
    """
    Produto é específico de uma Financeira + Subsegmento.
    Assim, a Financeira X e a Financeira Y podem usar o mesmo Subsegmento,
    mas ter produtos diferentes.
    """
    financeira = models.ForeignKey(
        Financeira,
        on_delete=models.CASCADE,
        related_name="produtos"
    )
    modalidade = models.ForeignKey(
        Modalidade,
        on_delete=models.CASCADE,
        related_name="produtos"
    )
    
    segmento = models.ForeignKey(
        Segmento,
        on_delete=models.CASCADE,
        related_name="produtos"
    )
    nome_produto = models.CharField("Produto", max_length=50, blank=True)
    comissao_percentual = models.DecimalField(
        "Comissão",
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[
            MinValueValidator(0, message="A comissão não pode ser inferior a 0%"),
            MaxValueValidator(100, message="A comissão não pode ser superior a 100%")
        ],
        help_text="Percentual de comissão (0 a 100)."
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["financeira", "modalidade", "segmento", "nome_produto"],
                name="segmento"
            )
        ]
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"

    def __str__(self):
        return f"{self.nome_produto}"
