from django.urls import path
from . import views

app_name = 'financeiras'

urlpatterns = [
    path('', views.financeira_list, name='financeira_list'),  # Lista de financeiras
    path('nova/', views.financeira_create, name='financeira_create'),  # Criar nova financeira
    path('<int:pk>/', views.financeira_detail, name='financeira_detail'),  # Detalhes da financeira
    path('<int:pk>/editar/', views.financeira_update, name='financeira_update'),  # Editar financeira
    path('api/segmentos_por_modalidade/', views.get_segmentos_por_modalidade, name='api_segmentos_por_modalidade'),
    
]
