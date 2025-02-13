from django.contrib import admin
from .models import StatusProposta

@admin.register(StatusProposta)
class StatusPropostaAdmin(admin.ModelAdmin):
    list_display = ('id', 'ds_status')  # Campos exibidos no Django Admin
    search_fields = ('ds_status',)  # Permite busca pelo campo "Status da Proposta"
    ordering = ('ds_status',)  # Ordenação padrão por "Status da Proposta"
