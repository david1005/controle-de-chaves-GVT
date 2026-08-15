from datetime import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Chave, Movimentacao, Pessoa, Usuario

class RegistrarRetiradaTests(TestCase):
    def setUp(self):
        self.operador = Usuario.objects.create_user(
            email="operador@example.com",
            nome="Operador",
            password="senha-segura-123",
        )
        self.chave = Chave.objects.create(codigo="LAB-01", local="Laboratório 1")
        self.pessoa = Pessoa.objects.create(
            nome="Pessoa Autorizada",
            matricula="12345",
            cargo="Técnico",
        )
        self.client.force_login(self.operador)

    def test_retirada_persiste_data_hora_e_observacoes_informadas(self):
        resposta = self.client.post(reverse("retirada"), {
            "chave": self.chave.id,
            "pessoa": self.pessoa.id,
            "data": "2026-08-15",
            "horario": "14:30",
            "observacoes": "Uso em aula prática.",
        })

        self.assertRedirects(resposta, reverse("inicio"))
        movimentacao = Movimentacao.objects.get()
        esperado = timezone.make_aware(
            datetime(2026, 8, 15, 14, 30),
            timezone.get_current_timezone(),
        )
        self.assertEqual(movimentacao.data_hora_retirada, esperado)
        self.assertEqual(movimentacao.observacoes, "Uso em aula prática.")
        self.assertEqual(movimentacao.status, "retirada")


class RegistrarDevolucaoTests(TestCase):
    def setUp(self):
        self.operador = Usuario.objects.create_user(
            email="operador@example.com",
            nome="Operador",
            password="senha-segura-123",
        )
        self.chave = Chave.objects.create(codigo="LAB-01", local="Laboratório 1")
        self.pessoa = Pessoa.objects.create(
            nome="Pessoa Autorizada",
            matricula="12345",
            cargo="Técnico",
        )
        self.client.force_login(self.operador)

    def test_devolucao_bem_sucedida_atualiza_status(self):
        movimentacao = Movimentacao.objects.create(
            chave=self.chave,
            pessoa=self.pessoa,
            operador=self.operador,
        )

        resposta = self.client.post(reverse("registrar_devolucao"), {
            "chave": self.chave.id,
        })

        self.assertRedirects(resposta, reverse("inicio"))
        movimentacao.refresh_from_db()
        self.assertIsNotNone(movimentacao.data_hora_devolucao)
        self.assertEqual(movimentacao.status, "devolvida")

    def test_devolucao_sem_retirada_aberta_mostra_erro(self):
        resposta = self.client.post(reverse("registrar_devolucao"), {
            "chave": self.chave.id,
        })

        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "Essa chave não possui uma retirada em aberto.")
        self.assertFalse(
            Movimentacao.objects.filter(chave=self.chave, data_hora_devolucao__isnull=False).exists()
        )


class PermissoesAdministradorTests(TestCase):
    def setUp(self):
        self.operador = Usuario.objects.create_user(
            email="operador@example.com",
            nome="Operador",
            password="senha-segura-123",
            tipo="operador",
        )
        self.administrador = Usuario.objects.create_user(
            email="admin@example.com",
            nome="Administradora",
            password="senha-segura-123",
            tipo="administrador",
        )
        self.chave = Chave.objects.create(codigo="LAB-01", local="Laboratório 1")
        self.pessoa = Pessoa.objects.create(
            nome="Pessoa Autorizada",
            matricula="12345",
            cargo="Técnico",
        )

    def test_operador_e_redirecionado_das_telas_administrativas(self):
        self.client.force_login(self.operador)

        rotas_get = [
            reverse("cadastrar_chave"),
            reverse("editar_chave", args=[self.chave.id]),
            reverse("cadastrar_pessoa"),
            reverse("editar_pessoa", args=[self.pessoa.id]),
            reverse("cadastrar_usuario"),
            reverse("historico"),
            reverse("relatorio"),
        ]

        for rota in rotas_get:
            resposta = self.client.get(rota)
            self.assertRedirects(resposta, reverse("inicio"))

    def test_operador_nao_consegue_inativar_chave(self):
        self.client.force_login(self.operador)

        resposta = self.client.post(reverse("inativar_chave", args=[self.chave.id]))

        self.assertRedirects(resposta, reverse("inicio"))
        self.chave.refresh_from_db()
        self.assertTrue(self.chave.ativa)

    def test_administrador_acessa_telas_administrativas(self):
        self.client.force_login(self.administrador)

        rotas_get = [
            reverse("cadastrar_chave"),
            reverse("editar_chave", args=[self.chave.id]),
            reverse("cadastrar_pessoa"),
            reverse("editar_pessoa", args=[self.pessoa.id]),
            reverse("cadastrar_usuario"),
            reverse("historico"),
            reverse("relatorio"),
        ]

        for rota in rotas_get:
            resposta = self.client.get(rota)
            self.assertEqual(resposta.status_code, 200)


class CadastrarUsuarioTests(TestCase):
    def setUp(self):
        self.administrador = Usuario.objects.create_user(
            email="admin@example.com",
            nome="Administradora",
            password="senha-segura-123",
            tipo="administrador",
        )
        self.client.force_login(self.administrador)

    def test_lista_de_usuarios_aparece_na_tabela(self):
        Usuario.objects.create_user(
            email="operador@example.com",
            nome="Operador Cadastrado",
            password="senha-segura-123",
            tipo="operador",
        )

        resposta = self.client.get(reverse("cadastrar_usuario"))

        self.assertContains(resposta, "Operador Cadastrado")
        self.assertNotContains(resposta, "Nenhum usuário cadastrado")

    def test_erro_de_nome_vazio_renderiza_usuarios_html(self):
        resposta = self.client.post(reverse("cadastrar_usuario"), {
            "nome": "",
            "email": "novo@example.com",
            "password": "senha-segura-123",
        })

        self.assertTemplateUsed(resposta, "usuarios.html")
        self.assertContains(resposta, "O nome do operador é obrigatório!")

    def test_cadastro_via_ui_sempre_cria_operador_mesmo_forcando_tipo(self):
        resposta = self.client.post(reverse("cadastrar_usuario"), {
            "nome": "Novo Usuário",
            "email": "novo@example.com",
            "password": "senha-segura-123",
            "tipo": "administrador",  # campo não existe mais no form, mas simula POST manipulado
        })

        self.assertRedirects(resposta, reverse("inicio"))
        novo_usuario = Usuario.objects.get(email="novo@example.com")
        self.assertEqual(novo_usuario.tipo, "operador")
        self.assertFalse(novo_usuario.is_staff)

    def test_badge_administrador_aparece_uma_unica_vez(self):
        resposta = self.client.get(reverse("cadastrar_usuario"))

        self.assertContains(resposta, "Administrador", count=1)

    def test_badge_operador_para_usuario_comum(self):
        Usuario.objects.create_user(
            email="operador2@example.com",
            nome="Operador Dois",
            password="senha-segura-123",
            tipo="operador",
        )

        resposta = self.client.get(reverse("cadastrar_usuario"))

        self.assertContains(resposta, "Operador")
        self.assertNotContains(resposta, "Usuário comum")