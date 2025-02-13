from django import forms
from django.forms import inlineformset_factory
from .models import Proposta, Veiculo
from clientes.models import (
    Cliente,
    EnderecoCliente,
    ProfissaoCliente,
    ContatoCliente  # <--- Importamos também o model de Contato
)
from financeiras.models import Financeira, Modalidade, Segmento, Produto

# -------------- Widgets Úteis -------------- #
class DateInput(forms.DateInput):
    input_type = 'date'
    format = '%Y-%m-%d'
    def __init__(self, *args, **kwargs):
        kwargs['format'] = self.format
        super().__init__(*args, **kwargs)

# ------------------------------------------------------------------
# -------------- Forms de Cliente e seus inlines -------------------
# ------------------------------------------------------------------

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [
            'nr_cpf',
            'nm_cliente',
            'dt_nascimento',
            'sexo',
            'nm_mae',
            'rg_cliente',
        ]
        widgets = {
            'nr_cpf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ' '}),
            'nm_cliente': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ' '}),
            'dt_nascimento': DateInput(format='%Y-%m-%d',
                                            attrs={'class': 'form-control', 'placeholder': ' '}),
            'sexo': forms.Select(attrs={'class': 'form-control', 'placeholder': ' '}),
            'nm_mae': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ' '}),
            'rg_cliente': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': ' '}),
        }

    def clean_nr_cpf(self):
        cpf = self.cleaned_data.get('nr_cpf', '')
        return cpf.replace('.', '').replace('-', '')


class EnderecoClienteForm(forms.ModelForm):
    class Meta:
        model = EnderecoCliente
        fields = ['cep', 'endereco', 'nro', 'complemento', 'bairro', 'cidade', 'uf', 'loja', 'operador']
        widgets = {
            'cep': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ' '}),
            'endereco': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ' '}),
            'nro': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': ' '}),
            'complemento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ' '}),
            'bairro': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ' '}),
            'cidade': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ' '}),
            'uf': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ' '}),
            'loja': forms.HiddenInput(),  # Campo escondido
            'operador': forms.HiddenInput(),  # Campo escondido            
        }


class ProfissaoClienteForm(forms.ModelForm):
    class Meta:
        model = ProfissaoCliente
        fields = [
            'profissao',
            'cargo',
            'local_trabalho',
            'data_admissao',
            'renda',
            'outras_rendas',
            'fone_lt',
            'loja',
            'operador',
        ]
        widgets = {
            'profissao': forms.Select(attrs={'class': 'form-control', 'placeholder': ' '}),
            'cargo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ' '}),
            'local_trabalho': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ' '}),
            'data_admissao': DateInput(format='%Y-%m-%d',
                                            attrs={'class': 'form-control', 'placeholder': ' '}),
            'renda': forms.TextInput(
                attrs={'class': 'form-control money', 'placeholder': ''}
            ),
            'fone_lt': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ' '}),
            'outras_rendas': forms.TextInput(
                attrs={'class': 'form-control money', 'placeholder': ''}
            ),
            'loja': forms.HiddenInput(),  # Campo escondido
            'operador': forms.HiddenInput(),  # Campo escondido
        }


class ContatoClienteForm(forms.ModelForm):
    class Meta:
        model = ContatoCliente
        fields = ['telefone_fixo', 'celular', 'email', 'loja', 'operador']
        widgets = {
            'telefone_fixo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ' '}),
            'celular': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ' '}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': ' '}),
            'loja': forms.HiddenInput(),  # Campo escondido
            'operador': forms.HiddenInput(),  # Campo escondido           
        }


# ---------------- InlineFormSets ----------------
EnderecoClienteFormSet = inlineformset_factory(
    Cliente,
    EnderecoCliente,
    form=EnderecoClienteForm,
    fields=['cep', 'endereco', 'nro', 'complemento', 'bairro', 'cidade', 'uf'],
    extra=1,
    can_delete=False,
    max_num=1
)

ProfissaoClienteFormSet = inlineformset_factory(
    Cliente,
    ProfissaoCliente,
    form=ProfissaoClienteForm,
    fields=['profissao', 'cargo', 'local_trabalho', 'data_admissao', 'renda', 'outras_rendas', 'fone_lt'],
    extra=1,
    can_delete=False,
    max_num=1
)

ContatoClienteFormSet = inlineformset_factory(
    Cliente,
    ContatoCliente,
    form=ContatoClienteForm,
    fields=['telefone_fixo', 'celular', 'email'],
    extra=1,
    can_delete=True
)
# ------------------------------------------------------------------
# -------------- Form de Veículo -----------------------------------
# ------------------------------------------------------------------
class VeiculoForm(forms.ModelForm):
    class Meta:
        model = Veiculo
        fields = [
            'marca',
            'modelo',
            'ano_fabricacao',
            'ano_modelo',
            'placa',
            'renavam',
            'chassi',
            'uf',
            'vl_veiculo',
        ]
        widgets = {
            'marca': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': ' '}
            ),
            'modelo': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': ' '}
            ),
            'ano_fabricacao': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': ' '}
            ),
            'ano_modelo': forms.NumberInput(
                attrs={'class': 'form-control', 'placeholder': ' '}
            ),            
            'placa': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': ' '}
            ),
            'renavam': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': ' '}
            ),
            'chassi': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': ' '}
            ),
            'uf': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': ' '}
            ),            
            'vl_veiculo': forms.TextInput(attrs={'class': 'form-control money', 'placeholder': ' '}),  # Mantém o TextInput

        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['vl_veiculo'].initial = f"{self.instance.vl_veiculo:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")        


class PropostaForm(forms.ModelForm):
    class Meta:
        model = Proposta
        fields = [
            'nr_proposta',
            'vl_financiado',
            'prazo',
            'vl_parcela',
            'loja',
            'vendedor',
            'operador',
            'financeira',
            'modalidade',
            'segmento',
            'produto',
            'status',
            'dt_proposta',
            'dt_pagamento',
        ]
        widgets = {
            'nr_proposta': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ' '}),
            'vl_financiado': forms.TextInput(attrs={'class': 'form-control money', 'placeholder': ' '}),
            'prazo': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': ' '}),
            'vl_parcela': forms.TextInput(attrs={'class': 'form-control money', 'placeholder': ' '}),
            'dt_proposta': DateInput(attrs={'class': 'form-control', 'placeholder': ' '}),
            'dt_pagamento': DateInput(attrs={'class': 'form-control', 'placeholder': ' '}),
            'operador': forms.Select(attrs={'class': 'form-select'}),
            'financeira': forms.Select(attrs={'class': 'form-select'}),
            'modalidade': forms.Select(attrs={'class': 'form-select', 'id': 'id_modalidade'}),
            'segmento': forms.Select(attrs={'class': 'form-select', 'id': 'id_segmento'}),
            'produto': forms.Select(attrs={'class': 'form-select', 'id': 'id_produto'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'loja': forms.Select(attrs={'class': 'form-select'}),
            'vendedor': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Edição: carrega valores e ajusta QuerySets
        if self.instance and self.instance.pk:
            if self.instance.modalidade:
                self.fields['modalidade'].initial = self.instance.modalidade.id
                self.fields['segmento'].queryset = Segmento.objects.filter(modalidade=self.instance.modalidade)
            if self.instance.segmento:
                self.fields['segmento'].initial = self.instance.segmento.id

            if self.instance.financeira and self.instance.segmento:
                self.fields['produto'].queryset = Produto.objects.filter(
                    financeira=self.instance.financeira,
                    segmento=self.instance.segmento
                )
            if self.instance.produto:
                self.fields['produto'].initial = self.instance.produto.id

        # Se for POST, ajusta QuerySets dinamicamente
        data = self.data or {}
        modalidade_id = data.get('modalidade') or data.get('id_modalidade')
        segmento_id = data.get('segmento') or data.get('id_segmento')
        financeira_id = data.get('financeira') or data.get('id_financeira')

        if modalidade_id:
            try:
                modalidade_id = int(modalidade_id)
                self.fields['segmento'].queryset = Segmento.objects.filter(modalidade_id=modalidade_id)
            except (ValueError, TypeError):
                self.fields['segmento'].queryset = Segmento.objects.none()
        else:
            self.fields['segmento'].queryset = Segmento.objects.none()

        if financeira_id and segmento_id:
            try:
                financeira_id = int(financeira_id)
                segmento_id = int(segmento_id)
                self.fields['produto'].queryset = Produto.objects.filter(
                    financeira_id=financeira_id,
                    segmento_id=segmento_id
                )
            except (ValueError, TypeError):
                self.fields['produto'].queryset = Produto.objects.none()
        else:
            self.fields['produto'].queryset = Produto.objects.none()

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Preencher automaticamente a filial com base no operador
        if instance.operador and not instance.filial:
            instance.filial = instance.operador.filial

        if commit:
            instance.save()
        return instance