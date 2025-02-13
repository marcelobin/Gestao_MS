from django.contrib import admin
from .models import Financeira, Departamento, Modalidade, Segmento,  Produto


@admin.register(Financeira)
class FinanceiraAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome_financeira', 'cnpj')  # Campos para exibição no Django Admin
    search_fields = ('nome_financeira', 'cnpj')  # Campos de busca
    ordering = ('nome_financeira',)  # Ordenação padrão por nome


@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome_departamento', 'financeira')  # Exibe o ID, nome e financeira associada
    search_fields = ('nome_departamento', 'financeira__nome_financeira')  # Permite busca por nome e financeira
    ordering = ('nome_departamento',)  # Ordenação padrão por nome do departamento
    list_filter = ('financeira',)  # Filtro lateral por financeira


@admin.register(Modalidade)
class ModalideAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome_modalidade_display')  # Exibe ID e nome do segmento
    search_fields = ('nome_modalidade',)  # Permite busca pelo nome do segmento
    ordering = ('nome_modalidade',)  # Ordenação padrão por nome

    def nome_modalidade_display(self, obj):
        """Exibe 'Sem Nome' se o campo estiver vazio"""
        return obj.nome_modalidade or "Sem Nome"
    nome_modalidade_display.short_description = "Modalidade"


@admin.register(Segmento)
class SegmentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome_segmento_display', 'modalidade')  # Exibe ID, subsegmento e segmento associado
    search_fields = ('nome_segmento', 'modalidade__nome_modalidade')  # Busca por subsegmento e segmento
    ordering = ('modalidade', 'nome_segmento')  # Ordenação por segmento e subsegmento
    list_filter = ('modalidade',)  # Filtro lateral por segmento

    def nome_segmento_display(self, obj):
        """Exibe 'Sem Nome' se o campo estiver vazio"""
        return obj.nome_segmento or "Sem Nome"
    nome_segmento_display.short_description = "Segmento"


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome_produto_display', 'financeira', 'segmento', 'comissao_percentual')  # Exibe informações principais
    search_fields = ('nome_produto', 'financeira__nome_financeira', 'segmento__nome_segmento')  # Permite busca pelos campos
    list_filter = ('financeira', 'segmento')  # Filtros laterais para facilitar a navegação
    ordering = ('nome_produto',)  # Ordenação padrão por nome do produto

    def nome_produto_display(self, obj):
        """Exibe 'Sem Nome' se o campo estiver vazio"""
        return obj.nome_produto or "Sem Nome"
    nome_produto_display.short_description = "Produto"
