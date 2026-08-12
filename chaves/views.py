from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from .models import Chave, Pessoa, Operador, Movimentacao

# Autenticação

def login_view(request):
    if request.method == "POST":

        email = request.POST.get("email")
        password = request.POST.get("password")

        usuario = authenticate(
            request,
            email=email,
            password=password
        )

        if usuario is not None:
            login(request, usuario)
            return redirect("inicio")

        return render(request, "login.html", {
            "erro": "E-mail ou senha incorretos."
        })


    return render(request, "login.html")

def logout_view(request):
    logout(request)
    return redirect("login")

# Página principal

def inicio(request):
    return render(request, "index.html")


# Retirada

def registrar_retirada(request):
    if request.method == "POST":
        
        chave_id = request.POST.get("chave")
        pessoa_id = request.POST.get("pessoa")

        chave = Chave.objects.get(id=chave_id)
        pessoa = Pessoa.objects.get(id=pessoa_id)

        if not chave.ativa:
            return render(request, "index.html", {
                "erro": "Essa chave está inativa."
            })

        if not chave.esta_disponivel():
            return render(request, "index.html", {
                "erro": "Essa chave já foi retirada e não foi devolvida."
            })

        movimentacao = Movimentacao(
            chave=chave,
            pessoa=pessoa,
            operador=request.user.operador
        )

        movimentacao.save()

        return redirect("inicio")

    return redirect("inicio")


# Devolução

def registrar_devolucao(request):
    if request.method == "POST":
        
        chave_id = request.POST.get("chave")

        movimentacao = Movimentacao.objects.filter(
            chave_id=chave_id,
            data_hora_devolucao__isnull=True
        ).first()

        if movimentacao is None:
            return render(request, "index.html", {
                "erro": "Essa chave não possui uma retirada em aberto."
            })

        movimentacao.data_hora_devolucao = timezone.now()
        movimentacao.save()

        return redirect("inicio")

    return redirect("inicio")


# Chaves abertas

def chaves_abertas(request):
    movimentacoes = Movimentacao.objects.filter(
        data_hora_devolucao__isnull=True
    )

    return render(request, "index.html", {
        "movimentacoes": movimentacoes
    })

# Chaves

def cadastrar_chave(request):
    if request.method == "POST":
        codigo = request.POST.get("codigo")
        local = request.POST.get("local")
        observacoes = request.POST.get("observacoes")

        chave = Chave(codigo=codigo, local=local, observacoes=observacoes)
        chave.save()

        return redirect("inicio")
    
    return render(request, "cadastro_chave.html")

def editar_chave(request, chave_id):
    chave = Chave.objects.get(id=chave_id)
    
    if request.method == "POST":
        chave.codigo = request.POST.get("codigo")
        chave.local = request.POST.get("local")
        chave.observacoes = request.POST.get("observacoes")

        chave.save()

        return redirect("inicio")

    return render(request, "editar_chave.html", {"chave": chave})

def inativar_chave(request, chave_id):
    chave = Chave.objects.get(id=chave_id)

    chave.ativa = False
    chave.save()

    return redirect("inicio")

# Pessoas

def cadastrar_pessoa(request):
    if request.method == "POST":
        nome = request.POST.get("nome")
        matricula = request.POST.get("matricula")
        cargo = request.POST.get("cargo")
        foto = request.FILES.get("foto")

        if not nome or not nome.strip():
            return render(request, "Cadastro_pessoa.html", {
                "erro": "O nome da pessoa é obrigatório!"
        })

        if not matricula or not matricula.strip():
            return render(request, "Cadastro_pessoa.html", {
                "erro": "A matrícula é obrigatória!"
        })

        if not cargo or not cargo.strip():
            return render(request, "Cadastro_pessoa.html", {
                "erro": "O cargo é obrigatório!"
        })

    nome = nome.strip()
    matricula = matricula.strip()
    cargo = cargo.strip()

    pessoa = Pessoa(
    nome=nome,
    matricula=matricula,
    cargo=cargo,
    foto=foto
    )

    pessoa.save()

    return redirect("inicio")

def editar_pessoa(request, pessoa_id):
    pessoa = Pessoa.objects.get(id=pessoa_id)

    if request.method == "POST":
        nome = request.POST.get("nome")
        matricula = request.POST.get("matricula")
        cargo = request.POST.get("cargo")
        foto = request.FILES.get("foto")

        if not nome or not nome.strip():
            return render(request, "Editar_pessoa.html", {
                "erro": "O nome da pessoa é obrigatório!"
            })

        if not matricula or not matricula.strip():
            return render(request, "Editar_pessoa.html", {
                "erro": "A matrícula é obrigatória!"
            })

        if not cargo or not cargo.strip():
            return render(request, "Editar_pessoa.html", {
                "erro": "O cargo é obrigatório!"
            })

        pessoa.nome = nome.strip()
        pessoa.matricula = matricula.strip()
        pessoa.cargo = cargo.strip()

        if foto:
            pessoa.foto = foto

        pessoa.save()

        return redirect("inicio")

    return render(request, "Editar_pessoa.html", {
        "pessoa": pessoa
    })
        

# Operadores

def cadastrar_operador(request):
    if request.method == "POST":
        nome = request.POST.get("nome")

        if not nome or not nome.strip():
            return render(request, "Cadastro_operador.html", {
                "erro": "O nome do operador é obrigatório!"
            })

        operador = Operador(nome=nome.strip())
        operador.save()

        return redirect("inicio")

# Consultas

def buscar_movimentacoes(
        chave = None, 
        pessoa = None, 
        data_inicio = None, 
        data_fim = None
        ):
    
    movimentacoes = Movimentacao.objects.all()

    if chave:
        movimentacoes = movimentacoes.filter(chave=chave)

    if pessoa:
            movimentacoes = movimentacoes.filter(pessoa=pessoa)

    if data_inicio:
        movimentacoes = movimentacoes.filter(
            data_hora_retirada__gte=data_inicio
        )

    if data_fim:
        movimentacoes = movimentacoes.filter(
            data_hora_retirada__lte=data_fim
        )

    return movimentacoes

def relatorio(request):
    chave_id = request.GET.get("chave")
    pessoa_id = request.GET.get("pessoa")
    data_inicio = request.GET.get("data_inicio")
    data_fim = request.GET.get("data_fim")

    chave = None
    pessoa = None

    if chave_id:
        chave = get_object_or_404(id=chave_id)

    if pessoa_id: 
        pessoa = get_object_or_404(id=pessoa_id)

    movimentacoes = buscar_movimentacoes(
        chave=chave,
        pessoa=pessoa,
        data_inicio=data_inicio,
        data_fim=data_fim,
    )

    return render(request, "relatorio.html", {
        "movimentacoes": movimentacoes
    })
