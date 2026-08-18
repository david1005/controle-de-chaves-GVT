from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from chaves import views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Autenticação
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Página principal
    path('', views.inicio, name='inicio'),

    # Movimentações
    path('retirada/', views.registrar_retirada, name='retirada'),
    path('devolucao/', views.registrar_devolucao, name='registrar_devolucao'),

    # Chaves, Pessoas, Local — listagem/painel
    path('chaves/', views.lista_chaves, name='lista_chaves'),
    path('chaves-abertas/', views.lista_chaves, name='chaves_abertas'),
    path('pessoas/', views.lista_pessoas, name='lista_pessoas'),

    # Chaves, Locais — cadastro/edição
    path('chaves/cadastrar/', views.cadastrar_chave, name='cadastrar_chave'),
    path('chaves/<int:chave_id>/editar/', views.editar_chave, name='editar_chave'),
    path('chaves/<int:chave_id>/inativar/', views.inativar_chave, name='inativar_chave'),
    path('chaves/<int:chave_id>/reativar/', views.reativar_chave, name='reativar_chave'),
    path('locais/cadastrar/', views.cadastrar_local, name='cadastrar_local'),

    # Pessoas
    path('pessoas/cadastrar/', views.cadastrar_pessoa, name='cadastrar_pessoa'),
    path('pessoas/<int:pessoa_id>/editar/', views.editar_pessoa, name='editar_pessoa'),

    # Usuários
    path('usuarios/', views.cadastrar_usuario, name='cadastrar_usuario'),
    path('usuarios/lista/', views.lista_usuarios, name='lista_usuarios'),

    # Consultas
    path('relatorios/', views.relatorio, name='relatorio'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)