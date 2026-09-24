"""Testes automáticos das regras de validação e da persistência.

Rodar com:  python -m unittest -v
"""
import json
import tempfile
import unittest
from pathlib import Path

import dados
from interface import montar_url_google
from validacoes import validar_email, validar_login, validar_prazo, validar_tarefa


def tarefa_valida(**mudancas):
    tarefa = {"titulo": "Estudar Tkinter", "descricao": "", "prioridade": "Alta",
              "prazo": "30/10/2026", "situacao": "Pendente"}
    tarefa.update(mudancas)
    return tarefa


class TestValidacoes(unittest.TestCase):
    def test_tarefa_valida_passa(self):
        self.assertTrue(validar_tarefa(tarefa_valida())[0])

    def test_titulo_vazio_e_recusado(self):
        ok, _, campo = validar_tarefa(tarefa_valida(titulo="   "))
        self.assertFalse(ok)
        self.assertEqual(campo, "titulo")

    def test_titulo_no_limite(self):
        self.assertTrue(validar_tarefa(tarefa_valida(titulo="abc"))[0])      # 3 = mínimo
        self.assertTrue(validar_tarefa(tarefa_valida(titulo="a" * 60))[0])   # 60 = máximo

    def test_titulo_fora_do_limite(self):
        self.assertFalse(validar_tarefa(tarefa_valida(titulo="ab"))[0])
        self.assertFalse(validar_tarefa(tarefa_valida(titulo="a" * 61))[0])

    def test_prazo_formato_errado(self):
        for texto in ["2026-10-30", "31/02/2026", "abc", ""]:
            self.assertFalse(validar_prazo(texto)[0], texto)

    def test_prazo_ano_fora_do_limite(self):
        self.assertFalse(validar_prazo("01/01/2019")[0])
        self.assertTrue(validar_prazo("01/01/2020")[0])

    def test_opcao_invalida(self):
        ok, _, campo = validar_tarefa(tarefa_valida(prioridade="Urgente"))
        self.assertFalse(ok)
        self.assertEqual(campo, "prioridade")

    def test_emails(self):
        self.assertTrue(validar_email("admin@gmail.com")[0])
        for email in ["a@.com", "a@b.", "a@gmail", "x@@y.com", "sem arroba.com", ""]:
            self.assertFalse(validar_email(email)[0], email)

    def test_login_sem_senha(self):
        ok, _, campo = validar_login("admin@gmail.com", "")
        self.assertFalse(ok)
        self.assertEqual(campo, "senha")

    def test_login_com_senha_em_branco_ou_com_espacos(self):
        self.assertFalse(validar_login("admin@gmail.com", "   ")[0])
        self.assertTrue(validar_login(" admin@gmail.com ", " 1234 ")[0])

    def test_opcao_com_espacos_ao_redor(self):
        ok, _, campo = validar_tarefa(tarefa_valida(prioridade=" Alta "))
        self.assertTrue(ok)
        self.assertEqual(campo, None)

    def test_url_google_para_busca(self):
        url = montar_url_google("tarefas python para pesquisar as suas duvidas.")
        self.assertTrue(url.startswith("https://www.google.com/search?q="))
        self.assertIn("tarefas+python", url)


class TestPersistencia(unittest.TestCase):
    def setUp(self):
        # Usa uma pasta temporária para não mexer no tarefas.json de verdade.
        self.pasta = tempfile.TemporaryDirectory()
        self.original = dados.ARQUIVO_DADOS
        dados.ARQUIVO_DADOS = Path(self.pasta.name) / "tarefas.json"

    def tearDown(self):
        dados.ARQUIVO_DADOS = self.original
        self.pasta.cleanup()

    def test_salvar_e_carregar(self):
        lista = [dict(tarefa_valida(), id=1)]
        self.assertTrue(dados.salvar_dados(lista)[0])
        carregado, aviso = dados.carregar_dados()
        self.assertEqual(carregado, lista)
        self.assertIsNone(aviso)

    def test_arquivo_inexistente_comeca_vazio(self):
        self.assertEqual(dados.carregar_dados(), ([], None))

    def test_arquivo_corrompido_gera_aviso_e_copia(self):
        dados.ARQUIVO_DADOS.write_text("{isso não é json", encoding="utf-8")
        lista, aviso = dados.carregar_dados()
        self.assertEqual(lista, [])
        self.assertIsNotNone(aviso)
        self.assertTrue(dados.ARQUIVO_DADOS.with_name("tarefas.json.bak").exists())

    def test_proximo_id(self):
        self.assertEqual(dados.proximo_id([]), 1)
        self.assertEqual(dados.proximo_id([{"id": 3}, {"id": 7}]), 8)


if __name__ == "__main__":
    unittest.main()
