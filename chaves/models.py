from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager

# Create your models here.


class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("O usuário deve possuir um e-mail.")

        email = self.normalize_email(email)

        usuario = self.model(
            email=email,
            **extra_fields
        )

        usuario.set_password(password)
        usuario.save(using=self._db)

        return usuario

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        return self.create_user(
            email=email,
            password=password,
            **extra_fields
        )


class Usuario(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    nome = models.CharField(max_length=100)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nome"]

    def __str__(self):
        return self.email


class Chave(models.Model):
    id = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=100, unique=True)
    local = models.CharField(max_length=100)
    ativa = models.BooleanField(default=True)
    observacoes = models.TextField(blank=True, null=True)


    class Meta:
        ordering = ['codigo']
        verbose_name = "Chave"
        verbose_name_plural = "Chaves"

    def __str__(self):
        return f"Chave {self.codigo} - Local: {self.local} - Ativa: {'Sim' if self.ativa else 'Não'}"
    
    def esta_disponivel(self):
        movimentacoes_ativas = Movimentacao.objects.filter(chave=self, data_hora_devolucao__isnull=True)
        return not movimentacoes_ativas.exists()
    
    
class Pessoa(models.Model):
    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100)
    matricula = models.CharField(max_length=100, unique=True)
    cargo = models.CharField(max_length=100, blank=True, null=True)
    foto = models.ImageField(upload_to='fotos_pessoas/', blank=True, null=True)

    class Meta:
        ordering = ['nome']
        verbose_name = "Pessoa"
        verbose_name_plural = "Pessoas" 

    def __str__(self):
        return f"Pessoa {self.nome} - Matrícula: {self.matricula} - Cargo: {self.cargo if self.cargo else 'N/A'}"

class Operador(models.Model):
    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100)

    class Meta:
        ordering = ['nome']
        verbose_name = "Operador"
        verbose_name_plural = "Operadores"

    def __str__(self):
        return f"Operador {self.nome}"

class Movimentacao(models.Model):
    id = models.AutoField(primary_key=True)
    chave = models.ForeignKey(Chave, on_delete=models.CASCADE)
    pessoa = models.ForeignKey(Pessoa, on_delete=models.CASCADE)
    data_hora_retirada = models.DateTimeField(auto_now_add=True)
    data_hora_devolucao = models.DateTimeField(blank=True, null=True)
    operador = models.ForeignKey(Operador, on_delete=models.SET_NULL, related_name='movimentacoes', blank=True, null=True)

    class Meta:
        ordering = ['-data_hora_retirada']
        verbose_name = "Movimentação"
        verbose_name_plural = "Movimentações"

    def __str__(self):
        return f"Movimentação - Chave: {self.chave.codigo} - Pessoa: {self.pessoa.nome} - Retirada: {self.data_hora_retirada} - Devolução: {self.data_hora_devolucao if self.data_hora_devolucao else 'Não devolvida'}"

    def clean(self):
        if not self.chave.esta_disponivel() and self.data_hora_devolucao is None:
            movimentacao_existente = Movimentacao.objects.filter(
                chave = self.chave, data_hora_devolucao__isnull = True
            ).exclude(pk = self.pk)
            if movimentacao_existente.exists():
                raise ValidationError('Essa chave já foi retirada e não foi devolvida!')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)