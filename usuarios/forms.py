from django import forms
from django.contrib.auth import get_user_model
from .models import Operador
import re  # Biblioteca para regex

User = get_user_model()

# -------------- Widgets Úteis -------------- #
class DateInput(forms.DateInput):
    input_type = 'date'
    format = '%Y-%m-%d'

    def __init__(self, *args, **kwargs):
        kwargs['format'] = self.format
        super().__init__(*args, **kwargs)

# Formulário para o modelo CustomUser
class UserForm(forms.ModelForm):
    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False
    )
    password_confirmation = forms.CharField(
        label="Confirmação de Senha",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirmation = cleaned_data.get('password_confirmation')

        if password and password != password_confirmation:
            raise forms.ValidationError("As senhas não coincidem.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')

        if password:
            user.set_password(password)
        else:
            user.password = User.objects.get(pk=user.pk).password

        if commit:
            user.save()
        return user

# Formulário para o modelo Operador
class OperadorForm(forms.ModelForm):
    class Meta:
        model = Operador
        fields = ['nm_operador', 'cpf_operador', 'dt_nascimento', 'cel_operador', 'email_operador', 'filial', 'perfil']
        widgets = {
            'nm_operador': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf_operador': forms.TextInput(attrs={'class': 'form-control'}),
            'dt_nascimento': DateInput(attrs={'class': 'form-control'}),
            'cel_operador': forms.TextInput(attrs={'class': 'form-control'}),
            'email_operador': forms.EmailInput(attrs={'class': 'form-control'}),
            'filial': forms.Select(attrs={'class': 'form-select'}),
            'perfil': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean_cpf_operador(self):
        """Remove caracteres não numéricos do CPF antes de salvar."""
        cpf = self.cleaned_data.get('cpf_operador')
        if cpf:
            cpf = re.sub(r'\D', '', cpf)  # Remove tudo que não for número
        return cpf

    def clean_cel_operador(self):
        """Remove caracteres não numéricos do celular antes de salvar."""
        celular = self.cleaned_data.get('cel_operador')
        if celular:
            celular = re.sub(r'\D', '', celular)  # Remove tudo que não for número
        return celular
