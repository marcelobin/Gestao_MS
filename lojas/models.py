# lojas/models.py
import os
from django.db import models
from usuarios.models import Operador, Filial
from django.utils.text import slugify
from PIL import Image
from PyPDF2 import PdfMerger
from io import BytesIO
from django.core.files.base import ContentFile


class Loja(models.Model):
    nr_cnpj = models.CharField("CNPJ", max_length=20, unique=True)
    razao_social = models.CharField("Razão Social",max_length=60)
    nm_fantasia = models.CharField("Nome Fantasia",max_length=60)
    dt_constituicao = models.DateField("Data de Constituição")
    cep = models.CharField("CEP",max_length=9)
    endereco = models.CharField("Endereço", max_length=60, null=True, blank=True)
    nro = models.CharField("Número", max_length=5, null=True, blank=True)
    complemento = models.CharField("Complemento", max_length=45, null=True, blank=True)
    bairro = models.CharField("Bairro",max_length=45, null=True, blank=True)
    cidade = models.CharField("Cidade",max_length=45, null=True, blank=True)
    uf = models.CharField("UF",max_length=2, null=True, blank=True)
    operador = models.ForeignKey(Operador, on_delete=models.CASCADE, related_name="lojas")
    filial = models.ForeignKey(Filial, on_delete=models.CASCADE)
    fone_fixo = models.CharField('Telefone Fixo', max_length=15, null=True, blank=True)
    celular = models.CharField('Celular', max_length=15, null=True, blank=True)
    email = models.EmailField("E-mail",max_length=50, null=True, blank=True)
    STATUS_CHOICES = (
        ('P', 'Pré-Cadastro'),
        ('A', 'Ativa'),
        ('I', 'Inativa'),
        ('B', 'Bloqueada'),
    )
    status = models.CharField("Status", max_length=1, choices=STATUS_CHOICES, default='P', blank=True)    


    def __str__(self):
        return self.nm_fantasia


class Socio(models.Model):
    nome_socio = models.CharField("Nome",max_length=60, null=True, blank=True)
    cpf_socio = models.CharField("CPF", max_length=15, null=True, blank=True)
    dt_nascimento_socio = models.DateField("Data de Nascimento", null=True, blank=True)
    celular = models.CharField("Celular",max_length=15, null=True, blank=True)
    email = models.EmailField("E-mail",max_length=50, null=True, blank=True)
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE, related_name="socios")

    def __str__(self):
        return self.nome_socio

class Vendedor(models.Model):
    nome_vendedor = models.CharField("Nome",max_length=60, null=True, blank=True)
    cpf_vendedor = models.CharField("CPF", max_length=15, null=True, blank=True)
    celular_vendedor = models.CharField("Celular",max_length=15, null=True, blank=True)
    email_vendedor = models.EmailField("E-mail",max_length=50, null=True, blank=True)
    chave_pix = models.CharField("Pix", max_length=60, null=True, blank=True)
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE, related_name="vendedores")

    def __str__(self):
        return self.nome_vendedor

class DadosBancarios(models.Model):
    codigo = models.CharField("Código Banco",max_length=3, null=True, blank=True)
    agencia = models.CharField("Agência",max_length=5, null=True, blank=True)
    conta = models.CharField("Conta",max_length=11, null=True, blank=True)
    loja = models.ForeignKey(Loja, on_delete=models.CASCADE, related_name="dadosbancarios", null=True, blank=True)


    def __str__(self):
        return f"Banco: {self.codigo}  | Ag: {self.agencia} | Conta: {self.conta}"

class LojaFinanceiraAcesso(models.Model):
    loja = models.ForeignKey(
        Loja,
        on_delete=models.CASCADE,
        related_name="acessos_financeiras"
    )
    financeira = models.ForeignKey(
        "financeiras.Financeira",  # ou importe e use direto
        on_delete=models.CASCADE,
        related_name="lojas_com_acesso"
    )
    codigo_acesso = models.CharField("Código de Acesso", max_length=20, blank=True, null=True)
    nm_cadastro_fin = models.CharField("Nome Cadastrado na Financeira", max_length=60, blank=True, null=True)

    class Meta:
        # Caso queira impedir duplicação de loja-financeira
        # e permitir somente um registro de acesso por dupla (loja, financeira)
        unique_together = ("loja", "financeira")

    def __str__(self):
        return f"{self.loja.nm_fantasia} - {self.financeira.nome_financeira}: {self.codigo_acesso}"


class LojaAnexo(models.Model):
    loja = models.ForeignKey('Loja', on_delete=models.CASCADE, related_name="anexos")
    arquivo = models.FileField(blank=True, null=True)
    TIPO_DOCUMENTO_CHOICES = (
    ('CNPJ', 'CNPJ'),
    ('CONTRATO', 'Contrato Social'),
    ('IDENTIFICACAO', 'Identificação dos Sócios'),
    ('COMPROVANTE_END', 'Comprovante de Endereço'),
    ('COMPROVANTE_CONTA', 'Comprovante de Conta Corrente'),
    ('CERTIFICADOS', 'Certificados'),
    ('DECLARACOES', 'Declarações'),
    ('FOTOS', 'Fotos'),
    ('OUTROS', 'Outros'),
    )
    tipo_documento = models.CharField("Tipo de Documento", max_length=20, choices=TIPO_DOCUMENTO_CHOICES)

    def save(self, *args, **kwargs):
        if self.arquivo:
            ext = os.path.splitext(self.arquivo.name)[-1].lower()
            pasta_loja = slugify(self.loja.nm_fantasia)  # ex: "loja-super"
            nome_formatado = f"{slugify(self.loja.nm_fantasia)}_{slugify(self.tipo_documento.upper())}{ext}"
            caminho_completo = f"anexos/{pasta_loja}/{nome_formatado}"
           
            self.arquivo.name = caminho_completo

            # Converter JPG para PDF
            if ext in ['.jpg', '.jpeg', '.png']:
                image = Image.open(self.arquivo)
                pdf_buffer = BytesIO()
                image.convert('RGB').save(pdf_buffer, format='PDF')
                pdf_buffer.seek(0)
                self.arquivo.save(caminho_completo.replace(ext, '.pdf'), ContentFile(pdf_buffer.read()), save=False)

        super().save(*args, **kwargs)
        