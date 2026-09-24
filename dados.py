"""Persistência: salva e carrega as tarefas em um arquivo JSON."""
import json
import shutil
from pathlib import Path

ARQUIVO_DADOS = Path(__file__).with_name("tarefas.json")


def carregar_dados():
    """Carrega as tarefas salvas.

    Devolve (lista, aviso). O aviso é None quando tudo deu certo; caso contrário
    é um texto para a interface mostrar ao usuário.
    """
    if not ARQUIVO_DADOS.exists():
        return [], None

    try:
        with ARQUIVO_DADOS.open("r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
        if not isinstance(dados, list):
            raise ValueError("o arquivo não contém uma lista")
        # Ignora itens estranhos (ex.: editados à mão) em vez de travar o programa.
        tarefas = [item for item in dados if isinstance(item, dict) and "id" in item]
        return tarefas, None

    except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
        # Guarda uma cópia do arquivo com problema antes que um novo salvamento
        # o sobrescreva. Assim nenhum dado é perdido sem aviso.
        copia = ARQUIVO_DADOS.with_name(ARQUIVO_DADOS.name + ".bak")
        try:
            shutil.copyfile(ARQUIVO_DADOS, copia)
        except OSError:
            pass
        return [], (
            f"O arquivo {ARQUIVO_DADOS.name} estava danificado e não pôde ser lido. "
            f"Uma cópia foi guardada em {copia.name} e a lista começou vazia."
        )

    except OSError as erro:
        return [], f"Não foi possível ler {ARQUIVO_DADOS.name}: {erro}"


def salvar_dados(lista):
    """Salva as tarefas. Devolve (ok, erro).

    Grava primeiro em um arquivo temporário e só depois troca pelo definitivo.
    Se o programa fechar no meio da gravação, o arquivo antigo continua inteiro.
    """
    temporario = ARQUIVO_DADOS.with_name(ARQUIVO_DADOS.name + ".tmp")
    try:
        with temporario.open("w", encoding="utf-8") as arquivo:
            json.dump(lista, arquivo, ensure_ascii=False, indent=2)
        temporario.replace(ARQUIVO_DADOS)
        return True, None
    except OSError as erro:
        return False, str(erro)


def proximo_id(lista):
    """Gera um id novo: maior id existente + 1."""
    return max((item["id"] for item in lista), default=0) + 1
