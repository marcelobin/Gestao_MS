from django.urls import path
from . import views

app_name = 'propostas'

urlpatterns = [
    path('', views.listar_propostas, name='listar_propostas'),
    path('nova/', views.proposta_form_view, name='criar_proposta'),
    path('<int:pk>/', views.proposta_form_view, name='editar_proposta'),
    path('detalhes/<int:pk>/', views.detalhe_proposta, name='detalhe_proposta'),
    
    # Rotas para a funcionalidade de comissão:
    path('lojas-elegiveis/', views.lojas_elegiveis, name='lojas_elegiveis'),
    path('gerar-recibo/', views.gerar_recibo_pagamento, name='gerar_recibo_pagamento'),
    path('recibo/<int:pk>/', views.detalhe_recibo, name='detalhe_recibo'),
    path('pagamentos/', views.pagamentos_list, name='pagamentos_list'),
    path('recibo/pdf/<int:pk>/', views.gerar_recibo_pdf, name='gerar_recibo_pdf'),

    
    # APIs auxiliares:
    path('api/subsegmentos/', views.get_segmentos, name='api_segmentos'),
    path('api/produtos/', views.get_produtos, name='api_produtos'),
    path('api/lojas/', views.get_lojas, name='api_lojas'),
    path('api/verificar-cliente/', views.verificar_cliente_api, name='verificar_cliente_api'),
    path('atualizar_status/<int:pk>/', views.atualizar_status_proposta, name='atualizar_status'),
    
    # Rotas API para financeira, segmentos e produtos:
    path('api/financeira/modalidades/', views.get_modalidades_por_financeira, name='api_modalidades_por_financeira'),
    path('api/financeira/segmentos/', views.get_segmentos_por_financeira_modalidade, name='api_segmentos_por_financeira'),
    path('api/financeira/produtos/', views.get_produtos_por_financeira_modalidade_segmento, name='api_produtos_por_financeira'),
    path('api/vendedores_por_loja/', views.get_vendedores_por_loja, name='get_vendedores_por_loja'),
]
