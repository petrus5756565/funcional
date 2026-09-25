# Gerenciador de Tarefas (Python + Tkinter)

## Objetivo

Aplicativo desktop para organizar compromissos por prioridade e prazo. O usuário
entra com login e pode cadastrar, listar, pesquisar, editar e excluir tarefas é um aplicativo voltado para marcar taréfas que está pendente.
ou marcar as taréfas concluidas.
As tarefas ficam salvas no computador e continuam lá depois de fechar o programa.

**Público:** estudantes e pessoas que querem controlar tarefas como empresarios tambem, do dia a dia sem
depender de internet.

## Requisitos

- Python 3.9 ou mais novo (o Tkinter já vem  e serve para ou Windows e, mac;
  no Linux instale com `sudo apt install python3-tk`)
- Pillow (opcional, só para exibir `logo.png` na tela de login)

## Instalação e execução

```bash
pip install -r requirements.txt
python main.py
```

Login de demonstração: `admin@gmail.com` / `1234`

## Como usar

1. Faça login (Enter também funciona).
2. Preencha título, prioridade, prazo (DD/MM/AAAA) e situação, e clique em **Adicionar**.
3. Clique em uma tarefa da lista para carregar os dados no formulário. Altere e clique
   em **Salvar alterações**, ou clique em **Excluir** (pede confirmação).
4. Use **Pesquisar** (título ou descrição) e o filtro **Situação** para encontrar tarefas.
5. O resumo no topo mostra total, pendentes, em andamento, concluídas e atrasadas.
   Tarefas com prazo vencido aparecem em vermelho.

Atalhos: `Esc` limpa o formulário, `Ctrl+F` vai para a pesquisa, `Delete` exclui a
tarefa selecionada.

## Estrutura

| Arquivo | Função |
|---|---|
| `main.py` | Ponto de entrada: abre o login e, depois, o gerenciador |
| `interface.py` | Telas (`TelaLogin` e `AppTarefas`) e estilos |
| `validacoes.py` | Regras de validação (título, descrição, prazo, opções, e-mail) |
| `dados.py` | Salva e carrega as tarefas em `tarefas.json` |
| `test_app.py` | Testes automáticos (`python -m unittest -v`) |

## Dicionário de dados (`tarefas.json`)

| Campo | Tipo | Regra |
|---|---|---|
| `id` | inteiro | Gerado automaticamente (maior id + 1) |
| `titulo` | texto | Obrigatório, 3 a 60 caracteres, sem repetir |
| `descricao` | texto | Opcional, até 200 caracteres |
| `prioridade` | texto | Alta, Média ou Baixa |
| `prazo` | texto | Data válida DD/MM/AAAA, ano entre 2020 e 2100 |
| `situacao` | texto | Pendente, Em andamento ou Concluída |

## Decisões de projeto

- **JSON** para persistência: simples de ler e de explicar, suficiente para poucas
  centenas de tarefas. O salvamento grava primeiro em um arquivo temporário e depois
  troca, para não corromper os dados se o programa fechar no meio.
- Se o `tarefas.json` estiver danificado, o app avisa e guarda uma cópia em
  `tarefas.json.bak` em vez de apagar os dados.
- Cada linha da tabela usa o `id` da tarefa. Assim, editar e excluir funcionam
  mesmo com a lista filtrada pela pesquisa.
- Validação separada da interface (`validacoes.py`), o que permite testá-la
  automaticamente.

## Plano de testes

| ID | Tipo | Cenário e dados | Resultado esperado |
|---|---|---|---|
| CT01 | Positivo | Cadastrar "Estudar Tkinter", Alta, 30/10/2026, Pendente | Aparece na lista e no resumo |
| CT02 | Positivo | Selecionar uma tarefa, mudar situação para Concluída e salvar | Lista e resumo atualizados |
| CT03 | Negativo | Adicionar com título vazio | Aviso "O título é obrigatório." e foco no título |
| CT04 | Negativo | Prazo "2026-10-30" ou "31/02/2026" | Aviso de prazo inválido |
| CT05 | Limite | Título com 3 e com 60 caracteres | Aceito |
| CT06 | Limite | Título com 2 e com 61 caracteres | Recusado com mensagem |
| CT07 | Persistência | Cadastrar, fechar e reabrir o programa | Tarefas continuam na lista |
| CT08 | Usabilidade | Pesquisar um termo que não existe | Lista vazia com a mensagem "Nenhuma tarefa encontrada..." |
| CT09 | Exclusão | Excluir e clicar em "Não"; depois excluir e clicar em "Sim" | Cancela; depois remove |

Preencha a coluna "Resultado obtido" do plano impresso depois de executar cada caso.

## Limitações

- O login usa um e-mail e uma senha fixos no código, só para demonstração. Não há
  cadastro de usuários nem senha criptografada.
- Os dados ficam em um único arquivo local; não há sincronização entre computadores.
- Não há lembretes ou notificações de prazo.
