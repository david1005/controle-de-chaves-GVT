"""
URL configuration for controle_chaves project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from chaves import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Autenticação
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Página principal
    path('', views.inicio, name='inicio'),

    # Movimentações
    path('retirada/', views.retirada, name='retirada'),
    path('devolucao/', views.registrar_devolucao, name='registrar_devolucao'),

    # Chaves — listagem/painel
    path('chaves/', views.lista_chaves, name='lista_chaves'),
    path('chaves-abertas/', views.lista_chaves, name='chaves_abertas'),

    # Chaves — cadastro/edição
    path('chaves/cadastrar/', views.cadastrar_chave, name='cadastrar_chave'),
    path('chaves/<int:chave_id>/editar/', views.editar_chave, name='editar_chave'),
    path('chaves/<int:chave_id>/inativar/', views.inativar_chave, name='inativar_chave'),

    # Pessoas
    path('pessoas/cadastrar/', views.cadastrar_pessoa, name='cadastrar_pessoa'),
    path('pessoas/<int:pessoa_id>/editar/', views.editar_pessoa, name='editar_pessoa'),

    # Usuários
    path('usuarios/', views.cadastrar_usuario, name='cadastrar_usuario'),

    # Consultas
    path('historico/', views.historico, name='historico'),
    path('relatorios/', views.relatorio, name='relatorio'),
]