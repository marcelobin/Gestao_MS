from django.urls import path
from . import views
from .views import criar_vendedor


app_name = 'lojas'

urlpatterns = [
    path('', views.listar_lojas, name='listar_lojas'),
    path('pre-cadastro/', views.pre_cadastro_loja, name='pre_cadastro_loja'),
    path('nova/', views.criar_editar_loja, name='criar_editar_loja'),
    path('<int:loja_id>/', views.criar_editar_loja, name='criar_editar_loja'),
    path('<int:loja_id>/deletar/', views.deletar_loja, name='deletar_loja'),
    path('<int:loja_id>/detalhes/', views.loja_detail, name='loja_detail'),
    path('buscar_bancos/', views.buscar_bancos, name='buscar_bancos'),
    path("criar_vendedor/", criar_vendedor, name="criar_vendedor"),
    path('pre-cadastros/', views.listar_pre_cadastros, name='listar_pre_cadastros'),

]
