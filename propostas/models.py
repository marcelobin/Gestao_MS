from django.db import models
from django.core.validators import RegexValidator
from usuarios.models import Operador, Filial
from financeiras.models import Financeira, Segmento, Modalidade, Produto
from decimal import Decimal, ROUND_HALF_UP
from django.utils import timezone





class Proposta(models.Model):
    nr_proposta = models.CharField("Número da Proposta", max_length=15, unique=True)
    vl_financiado = models.FloatField("Valor Financiado")
    prazo = models.IntegerField("Prazo (meses)")
    vl_parcela = models.FloatField("Valor da Parcela")
    receita = models.DecimalField("Receita", max_digits=12, decimal_places=2, default=0.00)
    loja = models.ForeignKey(
        "lojas.Loja", 
        on_delete=models.CASCADE, 
        related_name="propostas"
    )
    vendedor = models.ForeignKey(
        "lojas.Vendedor", 
        null=True,
        blank=True,
        on_delete=models.PROTECT, 
        related_name="propostas"
    )
    operador = models.ForeignKey(
        "usuarios.Operador", 
        on_delete=models.CASCADE, 
        related_name="propostas"
    )
    filial = models.ForeignKey(
        Filial,
        on_delete=models.CASCADE,
        related_name="propostas",
        null=True,
        blank=True
    )    
    cliente = models.ForeignKey(
        "clientes.Cliente", 
        on_delete=models.CASCADE, 
        related_name="propostas"
    )
    financeira = models.ForeignKey(
        "financeiras.Financeira", 
        on_delete=models.CASCADE, 
        related_name="propostas"
    )
    modalidade = models.ForeignKey(
        "financeiras.Modalidade",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    segmento = models.ForeignKey(
        "financeiras.Segmento",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    produto = models.ForeignKey(
        "financeiras.Produto",
        on_delete=models.CASCADE, 
        related_name="propostas"
    )
    veiculo = models.ForeignKey(
        "Veiculo", 
        on_delete=models.CASCADE, 
        related_name="propostas"
    )
    status = models.ForeignKey(
        "StatusProposta", 
        on_delete=models.CASCADE, 
        related_name="propostas"
    )
    dt_proposta = models.DateField("Data da Proposta", null=True, blank=True)
    dt_pagamento = models.DateField("Data do Pagamento", null=True, blank=True)
    dt_pagamento_retorno = models.DateField("Data do Pagamento do retorno", null=True, blank=True)

    # Novo campo para percentual financiado
    percentual_financiado = models.DecimalField(
        "Percentual Financiado", max_digits=5, decimal_places=2, null=True, blank=True
    )
    
    def calcular_receita(self):
        """Calcula a receita e retorna o valor arredondado."""
        if self.produto and self.produto.comissao_percentual:
            receita = Decimal(self.vl_financiado) * Decimal(self.produto.comissao_percentual) / Decimal(100)
            return receita.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return Decimal("0.00")    
    
    def save(self, *args, **kwargs):
        # Se a proposta ainda não tem filial, define a filial do operador
        if self.operador and not self.filial:
            self.filial = self.operador.filial  
        # Calcula e armazena a receita
        self.receita = self.calcular_receita()
        
        # Calcular o percentual financiado, se possível.
        # Supondo que o modelo Veiculo possua um campo 'valor' que representa o valor do veículo.
        if self.veiculo and hasattr(self.veiculo, 'vl_veiculo') and self.veiculo.vl_veiculo:
            # Converte para Decimal e calcula: (vl_financiado / valor_veiculo) * 100
            self.percentual_financiado = (
                Decimal(self.vl_financiado) / Decimal(self.veiculo.vl_veiculo)
            ) * Decimal(100)
            self.percentual_financiado = self.percentual_financiado.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        else:
            self.percentual_financiado = None

        super().save(*args, **kwargs)  # Salva no banco de dados       
  
    def __str__(self):
        return f"Proposta {self.nr_proposta} - Cliente: {self.cliente.nm_cliente}"

class Veiculo(models.Model):
    marca = models.CharField("Marca", max_length=45, null=True, blank=True)
    modelo = models.CharField("Modelo", max_length=45, null=True, blank=True)
    ano_fabricacao = models.CharField("Ano de Fabricação", max_length=4, null=True, blank=True)
    ano_modelo = models.CharField("Ano do Modelo", max_length=4, null=True, blank=True)
    placa = models.CharField("Placa", max_length=8,  null=True, blank=True)
    renavam = models.CharField(
        "RENAVAM",
        max_length=11,
        unique=False,
        validators=[
            RegexValidator(
                regex=r"^\d{11}$",
                message="RENAVAM inválido. Deve conter exatamente 11 dígitos."
            )
        ]
    )
    chassi = models.CharField("Chassi", max_length=17,  null=True, blank=True)
    uf = models.CharField("UF", max_length=2, null=True, blank=True, default="MS")
    vl_veiculo = models.FloatField("Valor do Veículo",  null=True, blank=True)



    def __str__(self):
        return f"{self.marca} {self.modelo} ({self.ano_modelo})"


class StatusProposta(models.Model):
    ds_status = models.CharField("Status da Proposta", max_length=45, null=True, blank=True)

    def __str__(self):
        return self.ds_status

class PagamentoComissao(models.Model):
    loja = models.ForeignKey("lojas.Loja", on_delete=models.CASCADE, related_name="pagamentos")
    data_pagamento = models.DateField("Data do Pagamento", default=timezone.now)
    propostas = models.ManyToManyField("Proposta", related_name="pagamentos", blank=True)
    total_financiado = models.DecimalField("Total Financiado", max_digits=12, decimal_places=2, default=Decimal("0.00"))
    total_comissao = models.DecimalField("Total Comissão", max_digits=12, decimal_places=2, default=Decimal("0.00"))
    numero_recibo = models.CharField("Número do Recibo", max_length=20, unique=True)

    def __str__(self):
        return f"Recibo {self.numero_recibo} - Loja: {self.loja.nm_fantasia} - {self.data_pagamento}"