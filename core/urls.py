from django.contrib import admin
from django.urls import path, include
from .views import index, login_view, logout_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),  # URL para o logout
       path('', index, name='index'),  # Define a página inicial
    path('clientes/', include('clientes.urls')),  # Inclui as URLs do app clientes
    path('usuarios/', include('usuarios.urls')),
    path('lojas/', include('lojas.urls')),
    path('financeiras/', include('financeiras.urls')),
    path('propostas/', include('propostas.urls')),
    path('django_plotly_dash/', include('django_plotly_dash.urls')),
    path('dashboard/', include('dashboard.urls')),  # Adiciona o dashboard às rotas
    path('configuracao/', include('configuracao.urls')),
    

]
