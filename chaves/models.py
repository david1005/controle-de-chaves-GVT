from django.db import models

# Create your models here.
class Chave(models.Model):
    id = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=100, unique=True)
    local = models.CharField(max_length=100)
    ativa = models.BooleanField(default=True)
    observacoes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Chave {self.codigo} - Local: {self.local} - Ativa: {'Sim' if self.ativa else 'Não'}"
    
class Pessoa(models.Model):
    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100)
    matricula = models.CharField(max_length=100, unique=True)
    cargo = models.CharField(max_length=100, blank=True, null=True)
    foto = models.ImageField(upload_to='fotos_pessoas/', blank=True, null=True)

    def __str__(self):
        return f"Pessoa {self.nome} - Matrícula: {self.matricula} - Cargo: {self.cargo if self.cargo else 'N/A'}"

class Operador(models.Model):
    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100)

    def __str__(self):
        return f"Operador {self.nome}"

class Movimentacao(models.Model):
    id = models.AutoField(primary_key=True)
    chave = models.ForeignKey(Chave, on_delete=models.CASCADE)
    pessoa = models.ForeignKey(Pessoa, on_delete=models.CASCADE)
    data_hora_retirada = models.DateTimeField(auto_now_add=True)
    data_hora_devolucao = models.DateTimeField(blank=True, null=True)
    operador = models.ForeignKey(Operador, on_delete=models.SET_NULL, related_name='movimentacoes', blank=True, null=True)

    def __str__(self):
        return f"Movimentação - Chave: {self.chave.codigo} - Pessoa: {self.pessoa.nome} - Retirada: {self.data_hora_retirada} - Devolução: {self.data_hora_devolucao if self.data_hora_devolucao else 'Não devolvida'}"

