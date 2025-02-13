from django.contrib import admin
from django.contrib.auth.models import User
from .models import Filial, Perfil, Operador


# Registro do modelo Filial no Admin
@admin.register(Filial)
class FilialAdmin(admin.ModelAdmin):
    list_display = ('id', 'ds_filial')  # Exibe o ID e a descrição da filial na lista
    search_fields = ('ds_filial',)  # Permite pesquisar por descrição da filial
    ordering = ('ds_filial',)  # Ordena por descrição da filial

# Registro do modelo Perfil no Admin
@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('id', 'ds_perfil')  # Exibe o ID e o perfil na lista
    search_fields = ('ds_perfil',)  # Permite pesquisar por perfil
    ordering = ('ds_perfil',)  # Ordena por perfil
