"""Regras de validação do aplicativo.

Cada função devolve uma tupla (ok, mensagem). Assim a interface só precisa
mostrar a mensagem quando ok for False, sem saber os detalhes da regra.
"""
from datetime import datetime

PRIORIDADES = ("Alta", "Média", "Baixa")
SITUACOES = ("Pendente", "Em andamento", "Concluída")

# Limites usados nos testes de "valor no limite" e "valor fora do limite".
TITULO_MIN = 3
TITULO_MAX = 60
DESCRICAO_MAX = 200
ANO_MIN = 2020
ANO_MAX = 2100


def texto_para_data(texto):
    """Converte 'DD/MM/AAAA' em data. Lança ValueError se o texto for inválido."""
    return datetime.strptime(texto.strip(), "%d/%m/%Y").date()


def validar_email(email):
    email = (email or "").strip()

    if not email:
        return False, "Informe o e-mail."
    if " " in email:
        return False, "O e-mail não pode ter espaços."
    if email.count("@") != 1:
        return False, "Informe um e-mail com exatamente um @."

    usuario, dominio = email.split("@")
    partes_dominio = dominio.split(".")

    # Recusa casos como "a@.com", "a@b." e "a@gmail" (sem ponto).
    if not usuario or len(partes_dominio) < 2 or any(not parte for parte in partes_dominio):
        return False, "O e-mail precisa ter usuário e domínio válidos, como nome@gmail.com."

    return True, ""


def validar_login(email, senha):
    """Devolve (ok, mensagem, campo) para a interface saber onde colocar o foco."""
    email = (email or "").strip().lower()
    senha = (senha or "").strip()

    ok, mensagem = validar_email(email)
    if not ok:
        return False, mensagem, "email"
    if not senha:
        return False, "Informe a senha.", "senha"
    return True, "", None


def validar_titulo(titulo):
    titulo = (titulo or "").strip()
    if not titulo:
        return False, "O título é obrigatório."
    if len(titulo) < TITULO_MIN:
        return False, f"O título deve ter pelo menos {TITULO_MIN} caracteres."
    if len(titulo) > TITULO_MAX:
        return False, f"O título pode ter no máximo {TITULO_MAX} caracteres (tem {len(titulo)})."
    return True, ""


def validar_descricao(descricao):
    descricao = (descricao or "").strip()
    if len(descricao) > DESCRICAO_MAX:
        return False, f"A descrição pode ter no máximo {DESCRICAO_MAX} caracteres (tem {len(descricao)})."
    return True, ""


def validar_prazo(texto):
    texto = (texto or "").strip()
    if not texto:
        return False, "Informe o prazo no formato DD/MM/AAAA."
    try:
        data = texto_para_data(texto)
    except ValueError:
        return False, "Prazo inválido. Use o formato DD/MM/AAAA, por exemplo 30/10/2026."
    if not ANO_MIN <= data.year <= ANO_MAX:
        return False, f"O ano do prazo deve estar entre {ANO_MIN} e {ANO_MAX}."
    return True, ""


def validar_opcao(valor, opcoes, nome_campo):
    valor = (valor or "").strip()
    if valor not in opcoes:
        return False, f"Escolha uma opção válida para {nome_campo}."
    return True, ""


def validar_tarefa(tarefa):
    """Valida todos os campos em ordem e para no primeiro erro.

    Devolve (ok, mensagem, campo_com_erro).
    """
    verificacoes = [
        ("titulo", validar_titulo(tarefa.get("titulo"))),
        ("descricao", validar_descricao(tarefa.get("descricao"))),
        ("prioridade", validar_opcao(tarefa.get("prioridade"), PRIORIDADES, "prioridade")),
        ("prazo", validar_prazo(tarefa.get("prazo"))),
        ("situacao", validar_opcao(tarefa.get("situacao"), SITUACOES, "situação")),
    ]
    for campo, (ok, mensagem) in verificacoes:
        if not ok:
            return False, mensagem, campo
    return True, "", None
