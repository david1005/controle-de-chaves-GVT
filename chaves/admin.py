from django.contrib import admin
from .models import Chave, Pessoa, Operador, Movimentacao

# Register your models here.
admin.site.register(Chave)
admin.site.register(Pessoa)
admin.site.register(Operador)
admin.site.register(Movimentacao)