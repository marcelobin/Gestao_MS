#lojas/forms.py

from django import forms
from django.forms import inlineformset_factory
from .models import Loja, Socio, Vendedor, DadosBancarios, LojaFinanceiraAcesso, LojaAnexo
from usuarios.models import Operador, Filial
from financeiras.models import Financeira
from django.forms.widgets import DateInput
from django.conf import settings
from datetime import datetime, date
import os
import json


# Formulário Loja
class LojaForm(forms.ModelForm):
    class Meta:
        model = Loja
        fields = [
            'nr_cnpj', 'razao_social', 'nm_fantasia', 'dt_constituicao', 'cep', 'endereco',
            'nro', 'complemento', 'bairro', 'cidade', 'uf', 'fone_fixo', 'celular', 'email',
            'operador', 'filial', 'status'
        ]
        widgets = {
            'dt_constituicao': forms.DateInput(attrs={'type': 'text', 'placeholder': 'dd/mm/aaaa'}),
        }

    def clean_dt_constituicao(self):
        data = self.cleaned_data.get('dt_constituicao')
        if isinstance(data, date):  # Corrige o uso de isinstance para datetime.date
            return data
        if isinstance(data, str):  # Caso o valor seja string, converte para datetime.date
            try:
                return datetime.strptime(data, '%d/%m/%Y').date()
            except ValueError:
                raise forms.ValidationError("A data deve estar no formato dd/mm/aaaa.")
        raise forms.ValidationError("Data inválida.")

class SocioForm(forms.ModelForm):
    class Meta:
        model = Socio
        fields = ['nome_socio', 'cpf_socio', 'dt_nascimento_socio', 'celular', 'email']
        widgets = {
            'dt_nascimento_socio': forms.DateInput(attrs={'type': 'text', 'placeholder': 'dd/mm/aaaa'}),
        }


    def clean_dt_nascimento_socio(self):
        data = self.cleaned_data.get('dt_nascimento_socio')
        if isinstance(data, date):  # Corrige o uso de isinstance para datetime.date
            return data
        if isinstance(data, str):  # Caso o valor seja string, converte para datetime.date
            try:
                return datetime.strptime(data, '%d/%m/%Y').date()
            except ValueError:
                raise forms.ValidationError("A data deve estar no formato dd/mm/aaaa.")
        raise forms.ValidationError("Data inválida.")
    
    
# Formulário Vendedor
class VendedorForm(forms.ModelForm):
    class Meta:
        model = Vendedor
        fields = ['nome_vendedor', 'cpf_vendedor', 'celular_vendedor', 'email_vendedor', 'chave_pix']


# Formulário Dados Bancários
class DadosBancariosForm(forms.ModelForm):
    class Meta:
        model = DadosBancarios
        fields = ['codigo',  'agencia', 'conta']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Lê o JSON do arquivo bancos.json
        json_file_path = os.path.join(settings.BASE_DIR, 'static', 'data', 'banco_codigo.json')
        with open(json_file_path, 'r', encoding='utf-8') as f:
            bancos_data = json.load(f)

        # Configura as opções do campo Select
        self.fields['codigo'].widget = forms.Select(
            attrs={'class': 'form-control select2-banco'},
            choices=[('', 'Selecione um banco')] + [(b['value'], f"{b['value']} - {b['label']}") for b in bancos_data]
        )
        

# InlineFormSet para Sócios
SocioLojaFormSet = inlineformset_factory(
    Loja,
    Socio,
    form=SocioForm,
    fields=['nome_socio', 'cpf_socio', 'dt_nascimento_socio', 'celular', 'email'],
    extra=0,  # Nenhum formulário extra inicial
    can_delete=True
)

# InlineFormSet para Vendedores
VendedorLojaFormSet = inlineformset_factory(
    Loja,
    Vendedor,
    form=VendedorForm,
    fields=['nome_vendedor', 'cpf_vendedor', 'celular_vendedor', 'email_vendedor', 'chave_pix'],
    extra=0,  # Nenhum formulário extra inicial
    min_num=0,
    can_delete=True
)

# InlineFormSet para Dados Bancários
DadosBancariosFormSet = inlineformset_factory(
    Loja,
    DadosBancarios,
    form=DadosBancariosForm,
    fields=['codigo','agencia', 'conta'],
    extra=0,
    max_num=4,
    can_delete=True
)

# Formulário LojaFinanceiraAcesso
class LojaFinanceiraAcessoForm(forms.ModelForm):
    class Meta:
        model = LojaFinanceiraAcesso
        fields = ['financeira', 'codigo_acesso']


# InlineFormSet para Acessos às Financeiras
LojaFinanceiraAcessoFormSet = inlineformset_factory(
    Loja,
    LojaFinanceiraAcesso,
    form=LojaFinanceiraAcessoForm,
    fields=['financeira', 'codigo_acesso','nm_cadastro_fin'],
    extra=0,
    can_delete=True
)

class LojaAnexoForm(forms.ModelForm):
    class Meta:
        model = LojaAnexo
        fields = ['tipo_documento', 'arquivo']

# Crie o inline formset para anexos
LojaAnexoFormSet = inlineformset_factory(
    Loja,
    LojaAnexo,
    form=LojaAnexoForm,
    fields=['tipo_documento', 'arquivo'],
    extra=0,  # Quantos formulários extras deseja que apareçam inicialmente
    can_delete=True
)
