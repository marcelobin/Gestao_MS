from django import forms
from django.forms import inlineformset_factory
from .models import Financeira, Departamento, Produto
from financeiras.models import Modalidade, Segmento  # se estiver em outro lugar, ajuste

class FinanceiraForm(forms.ModelForm):
    class Meta:
        model = Financeira
        fields = ['nome_financeira', 'cnpj']
        widgets = {
            'nome_financeira': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ' '}),
            'cnpj': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ' '}),
        }

class DepartamentoForm(forms.ModelForm):
    class Meta:
        model = Departamento
        fields = ['nome_departamento', 'telefone_fixo', 'celular', 'email']
        widgets = {
            'nome_departamento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ' '}),
            'telefone_fixo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ' '}),
            'celular': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ' '}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': ' '}),
        }

# ---- Corrigido: agora tem 'modalidade' e 'segmento' no fields
class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['nome_produto', 'modalidade', 'segmento', 'comissao_percentual']
        widgets = {
            'nome_produto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ' '}),
            'modalidade': forms.Select(attrs={'class': 'form-control', 'placeholder': ' '}),
            'segmento': forms.Select(attrs={'class': 'form-control', 'placeholder': ' '}),
            'comissao_percentual': forms.NumberInput(attrs={'class': 'form-control money', 'placeholder': ' ', 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Se a instância já existe e tem modalidade, filtra Segmentos
        if self.instance.pk and self.instance.modalidade:
            self.fields['segmento'].queryset = Segmento.objects.filter(modalidade=self.instance.modalidade)

        # Se POST, filtra Segmento de acordo com a modalidade selecionada
        data = self.data or {}
        mod_id = data.get(f"{self.prefix}-modalidade")
        if mod_id:
            try:
                self.fields['segmento'].queryset = Segmento.objects.filter(modalidade_id=int(mod_id))
            except ValueError:
                pass

DepartamentoFormSet = inlineformset_factory(
    Financeira,
    Departamento,
    form=DepartamentoForm,
    extra=0,
    can_delete=True
)

# ---- Corrigido: agora fields tem 'modalidade' e 'segmento'
ProdutoFormSet = inlineformset_factory(
    Financeira,
    Produto,
    form=ProdutoForm,
    fields=['nome_produto', 'modalidade', 'segmento', 'comissao_percentual'],
    extra=0,
    can_delete=True
)
