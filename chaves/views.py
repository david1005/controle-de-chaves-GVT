from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from .models import Usuario, Chave, Pessoa, Movimentacao
from django.views.decorators.http import require_POST
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from datetime import datetime

# Autenticação

def login_view(request):
    if request.method == "POST":

        email = request.POST.get("email")
        password = request.POST.get("password")

        usuario = authenticate(request, email=email, password=password)

        if usuario is not None:
            login(request, usuario)
            return redirect("inicio")

        return render(request, "login.html", {"erro": "E-mail ou senha incorretos."})

    return render(request, "login.html")

def logout_view(request):
    logout(request)
    return redirect("login")

# Página principal

@login_required
def inicio(request):
    return render(request, "index.html")


# Retirada

@login_required
def registrar_retirada(request):
    contexto_base = {
        "chaves": Chave.objects.filter(ativa=True),
        "pessoas": Pessoa.objects.all(),
    }

    if request.method == "POST":     
        
        chave_id = request.POST.get("chave")
        pessoa_id = request.POST.get("pessoa")
        data = request.POST.get("data")
        horario = request.POST.get("horario")
        observacoes = request.POST.get("observacoes", "").strip()

        try:
            chave = Chave.objects.get(id=chave_id)
        except Chave.DoesNotExist:
            return render(request, "retirada.html", {**contexto_base,"erro": "Chave não encontrada."})

        try:
            pessoa = Pessoa.objects.get(id=pessoa_id)
        except Pessoa.DoesNotExist:
            return render(request, "retirada.html", {**contexto_base,"erro": "Pessoa não encontrada."})

        if not chave.ativa:
            return render(request, "retirada.html", {**contexto_base, "erro": "Essa chave está inativa."})

        if not chave.esta_disponivel():
            return render(request, "retirada.html", {**contexto_base, "erro": "Essa chave já foi retirada e não foi devolvida."})

        try:
            data_hora_retirada = timezone.make_aware(
                datetime.strptime(f"{data} {horario}", "%Y-%m-%d %H:%M"),
                timezone.get_current_timezone(),
            )
        except (TypeError, ValueError):
            return render(request, "retirada.html", {
                **contexto_base,
                "erro": "Informe uma data e um horário de retirada válidos.",
            })

        Movimentacao.objects.create(
            chave=chave,
            pessoa=pessoa,
            operador=request.user,
            data_hora_retirada=data_hora_retirada,
            observacoes=observacoes or None,
        )

        return redirect("inicio")

    return render(request, "retirada.html", contexto_base)


# Devolução

@login_required
def registrar_devolucao(request):
    movimentacoes_abertas = Movimentacao.objects.filter(data_hora_devolucao__isnull=True)

    if request.method == "POST":
        chave_id = request.POST.get("chave")

        movimentacao = movimentacoes_abertas.filter(chave_id=chave_id).first()

        if movimentacao is None:
            return render(request, "devolucao.html", {
                "movimentacoes": movimentacoes_abertas,
                "erro": "Essa chave não possui uma retirada em aberto."
            })

        movimentacao.data_hora_devolucao = timezone.now()
        movimentacao.save()

        return redirect("inicio")

    return render(request, "devolucao.html", {"movimentacoes": movimentacoes_abertas})


# Chaves abertas

@login_required
def lista_chaves(request):
    return render(request, "lista.html", {"chaves": Chave.objects.all()})


# Chaves

@login_required
def cadastrar_chave(request):
    if not request.user.is_administrador():
        return redirect("inicio")

    if request.method == "POST":
        codigo = request.POST.get("codigo")
        local = request.POST.get("local")
        observacoes = request.POST.get("observacoes")

        if not codigo or not codigo.strip():
            return render(request, "cadastro.html", {
                "erro": "O código da chave é obrigatório!"
            })

        if not local or not local.strip():
            return render(request, "cadastro.html", {
                "erro": "O local é obrigatório!"
            })
            
        codigo = codigo.strip()

        if Chave.objects.filter(codigo=codigo).exists():
            return render(request, "cadastro.html", {
            "erro": "Já existe uma chave cadastrada com este código."
    })


        Chave.objects.create(codigo=codigo, local=local.strip(), observacoes=observacoes)

        return redirect("inicio")
    
    return render(request, "cadastro.html")

@login_required
def editar_chave(request, chave_id):
    if not request.user.is_administrador():
        return redirect("inicio")

    try:
        chave = Chave.objects.get(id=chave_id)
    except Chave.DoesNotExist:
        return redirect("inicio")

    if request.method == "POST":
        chave.codigo = request.POST.get("codigo")
        chave.local = request.POST.get("local")
        chave.observacoes = request.POST.get("observacoes")
        chave.save()

        return redirect("inicio")

    return render(request, "editar_chave.html", {"chave": chave})

@login_required
@require_POST
def inativar_chave(request, chave_id):
    if not request.user.is_administrador():
        return redirect("inicio")
    
    try:
        chave = Chave.objects.get(id=chave_id)
    except Chave.DoesNotExist:
        return redirect("inicio")
    
    chave.ativa = False
    chave.save()

    return redirect("inicio")

# Pessoas

@login_required
def cadastrar_pessoa(request):
    if not request.user.is_administrador():
        return redirect("inicio")

    if request.method == "POST":
        nome = request.POST.get("nome")
        matricula = request.POST.get("matricula")
        cargo = request.POST.get("cargo")
        foto = request.FILES.get("foto")

        if not nome or not nome.strip():
            return render(request, "cadastro.html", {"erro": "O nome da pessoa é obrigatório!"})

        if not matricula or not matricula.strip():
            return render(request, "cadastro.html", {"erro": "A matrícula é obrigatória!"})

        if not cargo or not cargo.strip():
            return render(request, "cadastro.html", {"erro": "O cargo é obrigatório!"})

        nova_pessoa = Pessoa(nome=nome.strip(), matricula=matricula.strip(), cargo=cargo.strip(), foto=foto)

        try:
            nova_pessoa.full_clean()
        except ValidationError as erro:
            return render(request, "cadastro.html", {"erro": " ".join(erro.messages)})

        nova_pessoa.save()

        return redirect("inicio")

    return render(request, "cadastro.html")


@login_required
def editar_pessoa(request, pessoa_id):
    if not request.user.is_administrador():
        return redirect("inicio")
    
    try:
        pessoa = Pessoa.objects.get(id=pessoa_id)
    except Pessoa.DoesNotExist:
        return redirect("inicio")

    if request.method == "POST":
        nome = request.POST.get("nome")
        matricula = request.POST.get("matricula")
        cargo = request.POST.get("cargo")
        foto = request.FILES.get("foto")

        if not nome or not nome.strip():
            return render(request, "editar_pessoa.html", {"pessoa": pessoa, "erro": "O nome da pessoa é obrigatório!"})

        if not matricula or not matricula.strip():
            return render(request, "editar_pessoa.html", {"pessoa": pessoa, "erro": "A matrícula é obrigatória!"})

        if not cargo or not cargo.strip():
            return render(request, "editar_pessoa.html", {"pessoa": pessoa, "erro": "O cargo é obrigatório!"})

        pessoa.nome = nome.strip()
        pessoa.matricula = matricula.strip()
        pessoa.cargo = cargo.strip()

        if foto:
            pessoa.foto = foto

        try:
            pessoa.full_clean()
        except ValidationError as erro:
            return render(request, "editar_pessoa.html", {"pessoa": pessoa, "erro": " ".join(erro.messages)})

        pessoa.save()

        return redirect("inicio")
    
    return render(request, "editar_pessoa.html", {"pessoa": pessoa})
        

# Usuários

@login_required
def cadastrar_usuario(request):
    if not request.user.is_administrador():
        return redirect("inicio")

    contexto_base = {"usuarios": Usuario.objects.all()}

    if request.method == "POST":
        nome = request.POST.get("nome")
        email = request.POST.get("email")
        password = request.POST.get("password")
        # Cadastro pela interface sempre cria operador. Administradores são criados via `createsuperuser` ou pelo Django admin.
        tipo = "operador"

        if not nome or not nome.strip():
            return render(request, "usuarios.html", {**contexto_base, "erro": "O nome do operador é obrigatório!"})

        if not email or not email.strip():
            return render(request, "usuarios.html", {**contexto_base, "erro": "O e-mail é obrigatório!"})

        if not password:
            return render(request, "usuarios.html", {
                **contexto_base,
                "erro": "A senha é obrigatória!"
            })
            
        try:
            validate_password(password)
        except ValidationError as erro:
            return render(request, "usuarios.html", {
            **contexto_base,
            "erro": " ".join(erro.messages),
        })

        if tipo not in ("operador", "administrador"):
            tipo = "operador"

        if Usuario.objects.filter(email=email.strip()).exists():
            return render(request, "usuarios.html", {
                **contexto_base, "erro": "Já existe um usuário com esse e-mail."
            })

        novo_usuario = Usuario(email=email.strip(), nome=nome.strip(), tipo=tipo)
        novo_usuario.set_password(password)

        try:
            novo_usuario.full_clean()
        except ValidationError as erro:
            return render(request, "usuarios.html", {
                **contexto_base, "erro": " ".join(erro.messages)
            })

        novo_usuario.save()

        return redirect("inicio")

    
    return render(request, "usuarios.html", contexto_base)

# Consultas

def buscar_movimentacoes(chave = None, pessoa = None, data_inicio = None, data_fim = None):
    movimentacoes = Movimentacao.objects.all()

    if chave:
        movimentacoes = movimentacoes.filter(chave=chave)

    if pessoa:
            movimentacoes = movimentacoes.filter(pessoa=pessoa)

    if data_inicio:
        movimentacoes = movimentacoes.filter(data_hora_retirada__gte=data_inicio)

    if data_fim:
        movimentacoes = movimentacoes.filter(data_hora_retirada__lte=data_fim)

    return movimentacoes

def _filtros_relatorio(request):
    chave_id = request.GET.get("chave")
    pessoa_id = request.GET.get("pessoa")
    chave = Chave.objects.filter(id=chave_id).first() if chave_id else None
    pessoa = Pessoa.objects.filter(id=pessoa_id).first() if pessoa_id else None

    return buscar_movimentacoes(
        chave=chave,
        pessoa=pessoa,
        data_inicio=request.GET.get("data_inicio"),
        data_fim=request.GET.get("data_fim"),
    )

@login_required
def relatorio(request):
    if not request.user.is_administrador():
        return redirect("inicio")

    return render(request, "relatorios.html", {
        "movimentacoes": _filtros_relatorio(request),
        "chaves": Chave.objects.all(),
        "pessoas": Pessoa.objects.all(),
    })
