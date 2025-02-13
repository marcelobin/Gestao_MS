from django.urls import path, include
from . import views
from .views import ClienteViewSet
from rest_framework.routers import DefaultRouter

app_name = 'clientes'

router = DefaultRouter()
router.register(r'clientes', ClienteViewSet)

urlpatterns = [
    path('novo/', views.cliente_create, name='cliente_create'),  # Rota para criar um cliente
    path('<int:pk>/editar/', views.cliente_update, name='cliente_update'),  # Rota para editar um cliente
    path('', views.cliente_list, name='cliente_list'),  # Rota para listar clientes
    path('<int:pk>/', views.cliente_detail, name='cliente_detail'),  # Rota para detalhes de um cliente
    path('api/', include(router.urls)),
    
]
