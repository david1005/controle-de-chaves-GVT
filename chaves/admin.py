from django.contrib import admin
from .models import Chave, Pessoa, Usuario, Movimentacao

admin.site.register(Chave)
admin.site.register(Pessoa)
admin.site.register(Usuario)
admin.site.register(Movimentacao)
