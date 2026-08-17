from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from django.core.validators import FileExtensionValidator


class UsuarioManager(BaseUserManager):
    def create_user(self, email, nome, password=None, tipo="operador"):
        if not email:
            raise ValueError("O usuário deve possuir um e-mail.")

        email = self.normalize_email(email)
        usuario = self.model(email=email, nome=nome, tipo=tipo)
        usuario.set_password(password)
        usuario.save(using=self._db)
        return usuario

    def create_superuser(self, email, nome, password=None):
        usuario = self.create_user(email, nome, password, tipo="administrador")
        usuario.is_staff = True
        usuario.is_superuser = True
        usuario.save(using=self._db)
        return usuario


class Usuario(AbstractBaseUser, PermissionsMixin):
    TIPO_CHOICES = [
        ("operador", "operador"),
        ("administrador", "Administrador"),
    ]

    email = models.EmailField(unique=True)
    nome = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default="operador")

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    data_criacao = models.DateTimeField(default=timezone.now)

    objects = UsuarioManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nome"]

    def __str__(self):
        return f"{self.email} ({self.tipo})"

    def is_administrador(self):
        return self.tipo == "administrador"


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
    

class Local(models.Model):
    nome = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["nome"]
        verbose_name = "Local"
        verbose_name_plural = "Locais"

    def __str__(self):
        return self.nome

    
class Pessoa(models.Model):
    id = models.AutoField(primary_key=True)
    nome = models.CharField(max_length=100)
    matricula = models.CharField(max_length=100, unique=True)
    cargo = models.CharField(max_length=100, blank=True, null=True)
    foto = models.ImageField(upload_to='fotos_pessoas/', blank=True, null=True, validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])])

    class Meta:
        ordering = ['nome']
        verbose_name = "Pessoa"
        verbose_name_plural = "Pessoas" 

    def __str__(self):
        return f"Pessoa {self.nome} - Matrícula: {self.matricula} - Cargo: {self.cargo if self.cargo else 'N/A'}"


class Movimentacao(models.Model):
    id = models.AutoField(primary_key=True)
    chave = models.ForeignKey(
        Chave,
        on_delete=models.PROTECT,
        related_name="movimentacoes"
    )
    pessoa = models.ForeignKey(
        Pessoa,
        on_delete=models.PROTECT,
        related_name="movimentacoes"
    )
    operador = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        related_name='movimentacoes',
        blank=True,
        null=True
    )
    data_hora_retirada = models.DateTimeField(default=timezone.now)
    data_hora_devolucao = models.DateTimeField(blank=True, null=True)
    observacoes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-data_hora_retirada']
        verbose_name = "Movimentação"
        verbose_name_plural = "Movimentações"

    class Meta:
        ordering = ['-data_hora_retirada']
        verbose_name = "Movimentação"
        verbose_name_plural = "Movimentações"

    def __str__(self):
        return f"Movimentação - Chave: {self.chave.codigo} - Pessoa: {self.pessoa.nome} - Retirada: {self.data_hora_retirada} - Devolução: {self.data_hora_devolucao if self.data_hora_devolucao else 'Não devolvida'}"

    @property
    def status(self):
        return "devolvida" if self.data_hora_devolucao else "retirada"

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
