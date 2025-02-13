from django import forms
from django.core.exceptions import ValidationError
from .models import Cliente, EnderecoCliente, ProfissaoCliente, ContatoCliente


# ---------------------- FORMULÁRIO DE CLIENTE ---------------------- #
class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = [
            'nm_cliente',
            'nr_cpf',
            'dt_nascimento',
            'sexo',
            'nm_mae',
            'rg_cliente',
        ]
        widgets = {
            'nm_cliente': forms.TextInput(attrs={'class': 'form-control'}),
            'nr_cpf': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '11'}),
            'dt_nascimento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'sexo': forms.Select(attrs={'class': 'form-select'}),
            'nm_mae': forms.TextInput(attrs={'class': 'form-control'}),
            'rg_cliente': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_nr_cpf(self):
        cpf = self.cleaned_data.get('nr_cpf', '').replace('.', '').replace('-', '')
        if not cpf.isdigit() or len(cpf) != 11:
            raise ValidationError("CPF inválido. Deve conter 11 dígitos.")

        cliente = Cliente.objects.filter(nr_cpf=cpf).exclude(id=self.instance.id).first()
        if cliente:
            raise ValidationError("Já existe um cliente com este CPF.")
        return cpf


# ---------------------- FORMULÁRIO DE ENDEREÇO ---------------------- #
class EnderecoClienteForm(forms.ModelForm):
    class Meta:
        model = EnderecoCliente
        fields = ['cep', 'endereco', 'nro', 'complemento', 'bairro', 'cidade', 'uf']
        widgets = {
            'cep': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '9'}),
            'endereco': forms.TextInput(attrs={'class': 'form-control'}),
            'nro': forms.TextInput(attrs={'class': 'form-control'}),
            'complemento': forms.TextInput(attrs={'class': 'form-control'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control'}),
            'uf': forms.TextInput(attrs={'class': 'form-control', 'maxlength': '2'}),
        }


# ---------------------- FORMULÁRIO DE PROFISSÃO ---------------------- #
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
        ]
        widgets = {
            'profissao': forms.Select(attrs={'class': 'form-select'}),
            'cargo': forms.TextInput(attrs={'class': 'form-control'}),
            'local_trabalho': forms.TextInput(attrs={'class': 'form-control'}),
            'data_admissao': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'renda': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'outras_rendas': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'fone_lt': forms.TextInput(attrs={'class': 'form-control'}),
        }


# ---------------------- FORMULÁRIO DE CONTATO ---------------------- #
class ContatoClienteForm(forms.ModelForm):
    class Meta:
        model = ContatoCliente
        fields = ['telefone_fixo', 'celular', 'email']
        widgets = {
            'telefone_fixo': forms.TextInput(attrs={'class': 'form-control'}),
            'celular': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
