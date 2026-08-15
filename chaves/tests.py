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
