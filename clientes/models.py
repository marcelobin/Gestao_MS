from django.db import models
from django.core.exceptions import ValidationError

# ===================== Função de Validação de CPF ===================== #
def validate_cpf(value):
    """Valida se o CPF contém apenas dígitos e possui 11 caracteres."""
    if not value.isdigit() or len(value) != 11:
        raise ValidationError("CPF inválido. Deve conter apenas 11 dígitos.")

# ===================== Model Cliente ===================== #
class Cliente(models.Model):
    SEXO_CHOICES = (
        ('M','Masculino'),
        ('F','Feminino'),
    )

    nm_cliente = models.CharField("Nome", max_length=100)
    nr_cpf = models.CharField(
        "CPF",
        max_length=14,
        unique=True,
        validators=[validate_cpf]
    )
    dt_nascimento = models.DateField("Data de Nascimento")
    sexo = models.CharField("Sexo", max_length=15, choices=SEXO_CHOICES, blank=True, null=True)
    nm_mae = models.CharField("Nome da Mãe", max_length=100, default="", blank=True)
    rg_cliente = models.CharField("RG", max_length=20, null=True, blank=True)

    def __str__(self):
        return f"{self.nm_cliente} (CPF: {self.nr_cpf})"

# ===================== Model Contato (Telefones/Emails) ===================== #
class ContatoCliente(models.Model):
    """Armazena vários tipos de contato para um cliente:
       Ex.: telefone fixo, celular, e-mail, etc."""
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name="contatos"
    )
    loja = models.ForeignKey("lojas.Loja", on_delete=models.CASCADE, null=True, blank=True)
    operador = models.ForeignKey("usuarios.Operador", on_delete=models.SET_NULL, null=True, blank=True)    
    telefone_fixo = models.CharField("Telefone Fixo", max_length=15, null=True, blank=True)
    celular = models.CharField("Celular", max_length=15, null=True, blank=True)
    email = models.EmailField("E-mail", null=True, blank=True)

    class Meta:
        unique_together = ('cliente', 'loja', 'operador', 'celular')

# ===================== Model Endereço ===================== #
class EnderecoCliente(models.Model):
    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name="enderecos"
    )
    loja = models.ForeignKey("lojas.Loja", on_delete=models.CASCADE, null=True, blank=True)
    operador = models.ForeignKey("usuarios.Operador", on_delete=models.SET_NULL, null=True, blank=True)    
    cep = models.CharField("CEP", max_length=9, null=True, blank=True)
    endereco = models.CharField("Endereço", max_length=60, null=True, blank=True)
    nro = models.CharField("Número", max_length=5, null=True, blank=True)
    complemento = models.CharField("Complemento", max_length=45, null=True, blank=True, default="")
    bairro = models.CharField("Bairro", max_length=45, null=True, blank=True)
    cidade = models.CharField("Cidade", max_length=45, null=True, blank=True)
    uf = models.CharField("UF", max_length=2, null=True, blank=True)

    def __str__(self):
        if self.endereco:
            return f"{self.endereco}, {self.cidade or ''} - {self.uf or ''}"
        return f"Endereço #{self.pk} do cliente {self.cliente.nm_cliente}"

    class Meta:
        unique_together = ('cliente', 'loja', 'operador', 'cep')

# ===================== Model Profissão ===================== #
class ProfissaoCliente(models.Model):
    TIPO_TRABALHO_CHOICES = [
        ('Aposentado', 'Aposentado'),
        ('Assalariado', 'Assalariado'),
        ('Autônomo', 'Autônomo'),
        ('Empresário', 'Empresário'),
        ('Profissional Liberal', 'Profissional Liberal'),
        ('Servidor Público', 'Servidor Público'),
    ]

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name="profissoes"
    )
    loja = models.ForeignKey("lojas.Loja", on_delete=models.CASCADE, null=True, blank=True)
    operador = models.ForeignKey("usuarios.Operador", on_delete=models.SET_NULL, null=True, blank=True)    
    profissao = models.CharField(
        "Profissão",
        max_length=45,
        choices=TIPO_TRABALHO_CHOICES,
        null=True, blank=True
    )
    cargo = models.CharField("Cargo", max_length=45, null=True, blank=True)
    local_trabalho = models.CharField("Local de Trabalho", max_length=45, null=True, blank=True)
    data_admissao = models.DateField("Data de Admissão", null=True, blank=True)
    renda = models.DecimalField("Renda", max_digits=10, decimal_places=2, null=True, blank=True)
    fone_lt = models.CharField("Telefone do Trabalho", max_length=15, null=True, blank=True)
    outras_rendas = models.DecimalField("Outras Rendas", max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        if self.local_trabalho:
            return f"{self.profissao} em {self.local_trabalho}"
        return f"{self.profissao} (Cliente: {self.cliente.nm_cliente})"

    class Meta:
        unique_together = ('cliente', 'loja', 'operador', 'profissao')
