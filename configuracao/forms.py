from django import forms
from financeiras.models import Modalidade, Segmento
from usuarios.models import Perfil, Filial

class ModalidadeForm(forms.ModelForm):
    class Meta:
        model = Modalidade
        fields = '__all__'

class SegmentoForm(forms.ModelForm):
    class Meta:
        model = Segmento
        fields = '__all__'

class PerfilForm(forms.ModelForm):
    class Meta:
        model = Perfil
        fields = '__all__'

class FilialForm(forms.ModelForm):
    class Meta:
        model = Filial
        fields = '__all__'
