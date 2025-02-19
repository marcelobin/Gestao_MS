from django.urls import path
from .views import (
    # Modalidade
    ModalidadeListView, ModalidadeCreateView, ModalidadeUpdateView, ModalidadeDeleteView,
    # Segmento
    SegmentoListView, SegmentoCreateView, SegmentoUpdateView, SegmentoDeleteView,
    # Perfil
    PerfilListView, PerfilCreateView, PerfilUpdateView, PerfilDeleteView,
    # Filial
    FilialListView, FilialCreateView, FilialUpdateView, FilialDeleteView, ConfiguracaoView,
    # StatusProposta
    StatusPropostaListView, StatusPropostaCreateView, StatusPropostaUpdateView, StatusPropostaDeleteView
)
from . import views

app_name = 'configuracao'


urlpatterns = [
    path('', ConfiguracaoView.as_view(), name='index'),
    # Modalidade
    path('modalidade/', ModalidadeListView.as_view(), name='modalidade_list'),
    path('modalidade/novo/', ModalidadeCreateView.as_view(), name='modalidade_create'),
    path('modalidade/editar/<int:pk>/', ModalidadeUpdateView.as_view(), name='modalidade_update'),
    path('modalidade/excluir/<int:pk>/', ModalidadeDeleteView.as_view(), name='modalidade_delete'),

    # Segmento
    path('segmento/', SegmentoListView.as_view(), name='segmento_list'),
    path('segmento/novo/', SegmentoCreateView.as_view(), name='segmento_create'),
    path('segmento/editar/<int:pk>/', SegmentoUpdateView.as_view(), name='segmento_update'),
    path('segmento/excluir/<int:pk>/', SegmentoDeleteView.as_view(), name='segmento_delete'),

    # Perfil
    path('perfil/', PerfilListView.as_view(), name='perfil_list'),
    path('perfil/novo/', PerfilCreateView.as_view(), name='perfil_create'),
    path('perfil/editar/<int:pk>/', PerfilUpdateView.as_view(), name='perfil_update'),
    path('perfil/excluir/<int:pk>/', PerfilDeleteView.as_view(), name='perfil_delete'),

    # Filial
    path('filial/', FilialListView.as_view(), name='filial_list'),
    path('filial/novo/', FilialCreateView.as_view(), name='filial_create'),
    path('filial/editar/<int:pk>/', FilialUpdateView.as_view(), name='filial_update'),
    path('filial/excluir/<int:pk>/', FilialDeleteView.as_view(), name='filial_delete'),
    
    # StatusProposta
    path('status-proposta/', StatusPropostaListView.as_view(), name='statusproposta_list'),
    path('status-proposta/novo/', StatusPropostaCreateView.as_view(), name='statusproposta_create'),
    path('status-proposta/editar/<int:pk>/', StatusPropostaUpdateView.as_view(), name='statusproposta_update'),
    path('status-proposta/excluir/<int:pk>/', StatusPropostaDeleteView.as_view(), name='statusproposta_delete'),
    
]
