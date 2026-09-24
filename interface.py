"""Telas do aplicativo: login e gerenciador de tarefas."""
import tkinter as tk
import webbrowser
from datetime import date
from pathlib import Path
from tkinter import messagebox, ttk
from urllib.parse import quote_plus

from dados import carregar_dados, proximo_id, salvar_dados
from validacoes import (
    PRIORIDADES,
    SITUACOES,
    texto_para_data,
    validar_login,
    validar_tarefa,
)

# O Pillow só é usado para a logo. Se não estiver instalado, o app funciona sem ela.
try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None

ARQUIVO_LOGO = Path(__file__).with_name("logo.png")

# Credenciais de demonstração (ver "Limitações" no README).
EMAIL_TESTE = "admin@gmail.com"
SENHA_TESTE = "1234"

COR_FUNDO = "#eef2f6"
COR_CARTAO = "#ffffff"
COR_DESTAQUE = "#007ACC"
COR_DESTAQUE_ESCURA = "#005f9e"
COR_TEXTO = "#1f2933"
COR_SUAVE = "#5f6b7a"
COR_ERRO = "#c0392b"
FONTE = "Segoe UI"


def montar_url_google(termo):
    """Cria a URL de busca no Google para o termo informado."""
    termo = (termo or "").strip()
    if not termo:
        return "https://www.google.com/"
    return f"https://www.google.com/search?q={quote_plus(termo)}"


def configurar_estilos(root):
    """Define a aparência dos widgets ttk em um só lugar."""
    estilo = ttk.Style(root)
    estilo.theme_use("clam")  # tema que aceita cores personalizadas em todos os sistemas
    root.configure(bg=COR_FUNDO)

    estilo.configure(".", background=COR_FUNDO, foreground=COR_TEXTO, font=(FONTE, 10))
    estilo.configure("Cartao.TFrame", background=COR_CARTAO)
    estilo.configure("Cartao.TLabel", background=COR_CARTAO)
    estilo.configure("Cartao.TCheckbutton", background=COR_CARTAO)
    estilo.configure("CartaoTitulo.TLabel", background=COR_CARTAO, font=(FONTE, 16, "bold"))
    estilo.configure("CartaoErro.TLabel", background=COR_CARTAO, foreground=COR_ERRO)
    estilo.configure("Titulo.TLabel", font=(FONTE, 16, "bold"))
    estilo.configure("Suave.TLabel", foreground=COR_SUAVE)
    estilo.configure("Dica.TLabel", foreground=COR_SUAVE, font=(FONTE, 8))

    estilo.configure("TButton", padding=(10, 6))
    estilo.configure("Primario.TButton", background=COR_DESTAQUE, foreground="white",
                     font=(FONTE, 10, "bold"), padding=(10, 6))
    estilo.map("Primario.TButton",
               background=[("disabled", "#9cc9e8"), ("active", COR_DESTAQUE_ESCURA)])
    estilo.configure("Perigo.TButton", foreground=COR_ERRO, padding=(10, 6))

    estilo.configure("Treeview", rowheight=26)
    estilo.configure("Treeview.Heading", font=(FONTE, 10, "bold"))


class TelaLogin:
    def __init__(self, root, ao_entrar):
        self.root = root
        self.ao_entrar = ao_entrar  # função chamada quando o login é aprovado
        self.logo = None  # guarda a imagem para ela não sumir da tela

        self.root.title("Gerenciador de Tarefas - Entrar")
        self.root.geometry("400x470")
        self.root.minsize(360, 440)

        self.email_var = tk.StringVar()
        self.senha_var = tk.StringVar()
        self.mostrar_senha_var = tk.BooleanVar(value=False)
        self.erro_var = tk.StringVar()

        self.criar_interface()
        # Enter faz login, igual clicar no botão.
        self.root.bind("<Return>", self.autenticar)

    def criar_interface(self):
        cartao = ttk.Frame(self.root, style="Cartao.TFrame", padding=28)
        cartao.place(relx=0.5, rely=0.5, anchor="center")

        if Image is not None and ARQUIVO_LOGO.exists():
            try:
                imagem = Image.open(ARQUIVO_LOGO)
                imagem.thumbnail((88, 88))
                self.logo = ImageTk.PhotoImage(imagem)
                ttk.Label(cartao, image=self.logo, style="Cartao.TLabel").pack(pady=(0, 12))
            except OSError:
                pass  # logo com problema: segue sem ela

        ttk.Label(cartao, text="Entrar", style="CartaoTitulo.TLabel").pack(anchor="w")
        ttk.Label(cartao, text="Use sua conta para ver suas tarefas.",
                  style="Cartao.TLabel", foreground=COR_SUAVE).pack(anchor="w", pady=(0, 16))

        ttk.Label(cartao, text="E-mail", style="Cartao.TLabel").pack(anchor="w")
        self.entrada_email = ttk.Entry(cartao, textvariable=self.email_var, width=32)
        self.entrada_email.pack(fill="x", pady=(2, 12))

        ttk.Label(cartao, text="Senha", style="Cartao.TLabel").pack(anchor="w")
        self.entrada_senha = ttk.Entry(cartao, textvariable=self.senha_var, show="•", width=32)
        self.entrada_senha.pack(fill="x", pady=(2, 4))

        ttk.Checkbutton(cartao, text="Mostrar senha", variable=self.mostrar_senha_var,
                        command=self.alternar_senha, style="Cartao.TCheckbutton").pack(anchor="w")

        # Mensagem de erro aparece dentro da tela, sem janela extra.
        ttk.Label(cartao, textvariable=self.erro_var, style="CartaoErro.TLabel",
                  wraplength=280).pack(anchor="w", pady=(10, 6))

        ttk.Button(cartao, text="Entrar", style="Primario.TButton",
                   command=self.autenticar).pack(fill="x")

        self.entrada_email.focus()

    def alternar_senha(self):
        self.entrada_senha.configure(show="" if self.mostrar_senha_var.get() else "•")

    def autenticar(self, _evento=None):
        email = self.email_var.get().strip().lower()
        senha = self.senha_var.get().strip()

        ok, mensagem, campo = validar_login(email, senha)
        if not ok:
            self.mostrar_erro(mensagem, campo)
            return

        if email != EMAIL_TESTE or senha != SENHA_TESTE:

            self.senha_var.set("")
            self.mostrar_erro("E-mail ou senha incorretos.", "senha")
            return("senha")
            return0

        self.root.unbind("<Return>")
        self.ao_entrar()

    def mostrar_erro(self, mensagem, campo):
        self.erro_var.set(mensagem)
        (self.entrada_email if campo == "email" else self.entrada_senha).focus()


class AppTarefas:
    """Cadastro, listagem, pesquisa, edição, exclusão e resumo de tarefas."""

    def __init__(self, root):
        self.root = root
        self.root.title("Gerenciador de Tarefas")
        self.root.geometry("980x600")
        self.root.minsize(840, 520)

        self.tarefas, aviso = carregar_dados()
        self.id_selecionado = None  # id da tarefa em edição (None = nenhuma)

        self.criar_variaveis()
        self.criar_interface()
        self.criar_atalhos()
        self.limpar_campos()
        self.atualizar_tabela()

        if aviso:
            messagebox.showwarning("Aviso sobre os dados", aviso)

    # ------------------------------------------------------------------ tela
    def criar_variaveis(self):
        self.titulo_var = tk.StringVar()
        self.descricao_var = tk.StringVar()
        self.prioridade_var = tk.StringVar()
        self.prazo_var = tk.StringVar()
        self.situacao_var = tk.StringVar()
        self.pesquisa_var = tk.StringVar()
        self.filtro_var = tk.StringVar(value="Todas")
        self.resumo_var = tk.StringVar()
        self.vazio_var = tk.StringVar()
        self.status_var = tk.StringVar()

        # A lista é refeita a cada letra digitada na pesquisa.
        self.pesquisa_var.trace_add("write", lambda *_: self.atualizar_tabela())

    def criar_interface(self):
        principal = ttk.Frame(self.root, padding=16)
        principal.pack(fill="both", expand=True)

        cabecalho = ttk.Frame(principal)
        cabecalho.pack(fill="x")
        ttk.Label(cabecalho, text="Minhas tarefas", style="Titulo.TLabel").pack(side="left")
        ttk.Label(cabecalho, textvariable=self.resumo_var, style="Suave.TLabel").pack(side="right")

        corpo = ttk.Frame(principal)
        corpo.pack(fill="both", expand=True, pady=(12, 0))
        corpo.columnconfigure(1, weight=1)
        corpo.rowconfigure(0, weight=1)

        self.criar_formulario(corpo)
        self.criar_lista(corpo)

        ttk.Label(principal, textvariable=self.status_var,
                  style="Suave.TLabel").pack(fill="x", pady=(10, 0))

    def criar_formulario(self, pai):
        form = ttk.LabelFrame(pai, text="Tarefa", padding=12)
        form.grid(row=0, column=0, sticky="ns", padx=(0, 14))

        ttk.Label(form, text="Título *").grid(row=0, column=0, sticky="w")
        self.entrada_titulo = ttk.Entry(form, textvariable=self.titulo_var, width=34)
        self.entrada_titulo.grid(row=1, column=0, sticky="ew", pady=(2, 10))

        ttk.Label(form, text="Descrição").grid(row=2, column=0, sticky="w")
        self.entrada_descricao = ttk.Entry(form, textvariable=self.descricao_var, width=34)
        self.entrada_descricao.grid(row=3, column=0, sticky="ew", pady=(2, 10))

        ttk.Label(form, text="Prioridade *").grid(row=4, column=0, sticky="w")
        self.combo_prioridade = ttk.Combobox(form, textvariable=self.prioridade_var,
                                             values=PRIORIDADES, state="readonly")
        self.combo_prioridade.grid(row=5, column=0, sticky="ew", pady=(2, 10))

        ttk.Label(form, text="Prazo *").grid(row=6, column=0, sticky="w")
        self.entrada_prazo = ttk.Entry(form, textvariable=self.prazo_var)
        self.entrada_prazo.grid(row=7, column=0, sticky="ew", pady=(2, 0))
        ttk.Label(form, text="Formato DD/MM/AAAA", style="Dica.TLabel").grid(
            row=8, column=0, sticky="w", pady=(0, 10))

        ttk.Label(form, text="Situação *").grid(row=9, column=0, sticky="w")
        self.combo_situacao = ttk.Combobox(form, textvariable=self.situacao_var,
                                           values=SITUACOES, state="readonly")
        self.combo_situacao.grid(row=10, column=0, sticky="ew", pady=(2, 16))

        botoes = ttk.Frame(form)
        botoes.grid(row=11, column=0, sticky="ew")
        botoes.columnconfigure((0, 1), weight=1)

        ttk.Button(botoes, text="Adicionar", style="Primario.TButton",
                   command=self.adicionar).grid(row=0, column=0, sticky="ew", padx=(0, 4), pady=(0, 6))
        self.botao_salvar = ttk.Button(botoes, text="Salvar alterações", command=self.salvar_edicao)
        self.botao_salvar.grid(row=0, column=1, sticky="ew", padx=(4, 0), pady=(0, 6))
        self.botao_excluir = ttk.Button(botoes, text="Excluir", style="Perigo.TButton",
                                        command=self.excluir)
        self.botao_excluir.grid(row=1, column=0, sticky="ew", padx=(0, 4))
        ttk.Button(botoes, text="Limpar campos",
                   command=self.limpar_campos).grid(row=1, column=1, sticky="ew", padx=(4, 0))

        ttk.Label(form, text="* campos obrigatórios", style="Dica.TLabel").grid(
            row=12, column=0, sticky="w", pady=(12, 0))

        # Usado para colocar o foco no campo que tem erro.
        self.campos = {
            "titulo": self.entrada_titulo,
            "descricao": self.entrada_descricao,
            "prioridade": self.combo_prioridade,
            "prazo": self.entrada_prazo,
            "situacao": self.combo_situacao,
        }

    def criar_lista(self, pai):
        lista = ttk.Frame(pai)
        lista.grid(row=0, column=1, sticky="nsew")

        barra = ttk.Frame(lista)
        barra.pack(fill="x", pady=(0, 8))
        ttk.Label(barra, text="Pesquisar").pack(side="left")
        self.entrada_pesquisa = ttk.Entry(barra, textvariable=self.pesquisa_var)
        self.entrada_pesquisa.pack(side="left", fill="x", expand=True, padx=(6, 12))
        ttk.Button(barra, text="Google", command=self.pesquisar_no_google).pack(side="left")
        ttk.Label(barra, text="Situação").pack(side="left", padx=(12, 0))
        filtro = ttk.Combobox(barra, textvariable=self.filtro_var, state="readonly", width=14,
                              values=("Todas",) + SITUACOES)
        filtro.pack(side="left", padx=(6, 0))
        filtro.bind("<<ComboboxSelected>>", lambda _e: self.atualizar_tabela())

        ttk.Label(lista, textvariable=self.vazio_var, style="Suave.TLabel").pack(anchor="w")

        container = ttk.Frame(lista)
        container.pack(fill="both", expand=True)

        colunas = ("titulo", "prioridade", "prazo", "situacao")
        self.tabela = ttk.Treeview(container, columns=colunas, show="headings", selectmode="browse")
        self.tabela.heading("titulo", text="Título")
        self.tabela.heading("prioridade", text="Prioridade")
        self.tabela.heading("prazo", text="Prazo")
        self.tabela.heading("situacao", text="Situação")
        self.tabela.column("titulo", width=260, anchor="w")
        self.tabela.column("prioridade", width=90, anchor="center")
        self.tabela.column("prazo", width=100, anchor="center")
        self.tabela.column("situacao", width=120, anchor="center")
        self.tabela.tag_configure("atrasada", foreground=COR_ERRO)
        self.tabela.tag_configure("concluida", foreground=COR_SUAVE)
        self.tabela.pack(side="left", fill="both", expand=True)

        rolagem = ttk.Scrollbar(container, orient="vertical", command=self.tabela.yview)
        rolagem.pack(side="right", fill="y")
        self.tabela.configure(yscrollcommand=rolagem.set)

        self.tabela.bind("<<TreeviewSelect>>", self.ao_selecionar)
        ttk.Label(lista, text="Vermelho = prazo vencido. Clique numa tarefa para editar.",
                  style="Dica.TLabel").pack(anchor="w", pady=(6, 0))

    def criar_atalhos(self):
        self.root.bind("<Escape>", lambda _e: self.limpar_campos())
        self.root.bind("<Control-f>", lambda _e: self.entrada_pesquisa.focus())
        self.tabela.bind("<Delete>", lambda _e: self.excluir())

    # ------------------------------------------------------------- ações
    def ler_formulario(self):
        return {
            "titulo": self.titulo_var.get().strip(),
            "descricao": self.descricao_var.get().strip(),
            "prioridade": self.prioridade_var.get(),
            "prazo": self.prazo_var.get().strip(),
            "situacao": self.situacao_var.get(),
        }

    def validar_formulario(self, dados, id_ignorado=None):
        ok, mensagem, campo = validar_tarefa(dados)
        if ok and self.titulo_repetido(dados["titulo"], id_ignorado):
            ok, mensagem, campo = False, "Já existe uma tarefa com esse título.", "titulo"
        if not ok:
            messagebox.showwarning("Verifique os campos", mensagem)
            self.campos[campo].focus()
        return ok

    def titulo_repetido(self, titulo, id_ignorado):
        return any(t["titulo"].lower() == titulo.lower() and t["id"] != id_ignorado
                   for t in self.tarefas)

    def adicionar(self):
        dados = self.ler_formulario()
        if not self.validar_formulario(dados):
            return

        dados["id"] = proximo_id(self.tarefas)
        self.tarefas.append(dados)
        if not self.gravar():
            self.tarefas.remove(dados)  # desfaz, porque não foi salvo
            return

        self.limpar_campos()
        self.atualizar_tabela()
        self.status_var.set(f"Tarefa \"{dados['titulo']}\" adicionada.")

    def salvar_edicao(self):
        tarefa = self.buscar_tarefa(self.id_selecionado)
        if tarefa is None:
            messagebox.showinfo("Editar", "Selecione uma tarefa na lista para editar.")
            return

        dados = self.ler_formulario()
        if not self.validar_formulario(dados, id_ignorado=tarefa["id"]):
            return

        copia = dict(tarefa)
        tarefa.update(dados)
        if not self.gravar():
            tarefa.clear()
            tarefa.update(copia)  # volta ao que era antes
            return

        self.limpar_campos()
        self.atualizar_tabela()
        self.status_var.set(f"Alterações em \"{tarefa['titulo']}\" salvas.")

    def excluir(self):
        tarefa = self.buscar_tarefa(self.id_selecionado)
        if tarefa is None:
            messagebox.showinfo("Excluir", "Selecione uma tarefa na lista para excluir.")
            return

        confirmou = messagebox.askyesno(
            "Excluir tarefa",
            f"Excluir \"{tarefa['titulo']}\"?\nEssa ação não pode ser desfeita.",
            icon="warning",
        )
        if not confirmou:
            self.status_var.set("Exclusão cancelada.")
            return

        posicao = self.tarefas.index(tarefa)
        self.tarefas.remove(tarefa)
        if not self.gravar():
            self.tarefas.insert(posicao, tarefa)
            return

        self.limpar_campos()
        self.atualizar_tabela()
        self.status_var.set(f"Tarefa \"{tarefa['titulo']}\" excluída.")

    def gravar(self):
        ok, erro = salvar_dados(self.tarefas)
        if not ok:
            messagebox.showerror("Erro ao salvar",
                                 f"Não foi possível salvar as tarefas.\n\nDetalhe: {erro}")
        return ok

    def limpar_campos(self):
        self.titulo_var.set("")
        self.descricao_var.set("")
        self.prioridade_var.set("Média")
        self.prazo_var.set(date.today().strftime("%d/%m/%Y"))
        self.situacao_var.set("Pendente")

        self.id_selecionado = None
        if self.tabela.selection():
            self.tabela.selection_remove(self.tabela.selection())
        self.botao_salvar.state(["disabled"])
        self.botao_excluir.state(["disabled"])
        self.status_var.set("Preencha os campos e clique em Adicionar.")
        self.entrada_titulo.focus()

    def ao_selecionar(self, _evento=None):
        selecao = self.tabela.selection()
        if not selecao:
            return

        tarefa = self.buscar_tarefa(int(selecao[0]))
        if tarefa is None:
            return

        self.id_selecionado = tarefa["id"]
        self.titulo_var.set(tarefa["titulo"])
        self.descricao_var.set(tarefa.get("descricao", ""))
        self.prioridade_var.set(tarefa["prioridade"])
        self.prazo_var.set(tarefa["prazo"])
        self.situacao_var.set(tarefa["situacao"])

        self.botao_salvar.state(["!disabled"])
        self.botao_excluir.state(["!disabled"])
        self.status_var.set(f"Editando \"{tarefa['titulo']}\". Altere os campos e clique em "
                            "Salvar alterações, ou pressione Esc para cancelar.")

    def buscar_tarefa(self, id_tarefa):
        for tarefa in self.tarefas:
            if tarefa["id"] == id_tarefa:
                return tarefa
        return None

    # ----------------------------------------------------- listagem e resumo
    @staticmethod
    def esta_atrasada(tarefa):
        try:
            prazo = texto_para_data(tarefa["prazo"])
        except (ValueError, KeyError):
            return False
        return tarefa.get("situacao") != "Concluída" and prazo < date.today()

    @staticmethod
    def chave_ordenacao(tarefa):
        """Ordena por prazo e, no mesmo dia, pela prioridade (Alta primeiro)."""
        try:
            prazo = texto_para_data(tarefa["prazo"])
        except (ValueError, KeyError):
            prazo = date.max
        ordem = PRIORIDADES.index(tarefa["prioridade"]) if tarefa.get("prioridade") in PRIORIDADES else 9
        return prazo, ordem

    def pesquisar_no_google(self):
        termo = self.pesquisa_var.get().strip()
        url = montar_url_google(termo)
        if not webbrowser.open(url):
            messagebox.showwarning("Pesquisa no Google", "Não foi possível abrir o navegador.")

    def atualizar_tabela(self):
        for linha in self.tabela.get_children():
            self.tabela.delete(linha)

        termo = self.pesquisa_var.get().strip().lower()
        filtro = self.filtro_var.get()

        visiveis = [
            t for t in self.tarefas
            if (termo in t["titulo"].lower() or termo in t.get("descricao", "").lower())
            and (filtro == "Todas" or t["situacao"] == filtro)
        ]

        for tarefa in sorted(visiveis, key=self.chave_ordenacao):
            if tarefa["situacao"] == "Concluída":
                tags = ("concluida",)
            elif self.esta_atrasada(tarefa):
                tags = ("atrasada",)
            else:
                tags = ()
            # O id da tarefa vira o id da linha. Assim a busca/filtro não
            # atrapalha a edição e a exclusão.
            self.tabela.insert("", tk.END, iid=str(tarefa["id"]), tags=tags,
                               values=(tarefa["titulo"], tarefa["prioridade"],
                                       tarefa["prazo"], tarefa["situacao"]))

        if not self.tarefas:
            self.vazio_var.set("Nenhuma tarefa ainda. Preencha o formulário ao lado para começar.")
        elif not visiveis:
            self.vazio_var.set("Nenhuma tarefa encontrada com essa pesquisa ou filtro.")
        else:
            self.vazio_var.set("")

        self.atualizar_resumo()

    def atualizar_resumo(self):
        total = len(self.tarefas)
        contagem = {s: sum(1 for t in self.tarefas if t["situacao"] == s) for s in SITUACOES}
        atrasadas = sum(1 for t in self.tarefas if self.esta_atrasada(t))
        self.resumo_var.set(
            f"Total: {total}   |   Pendentes: {contagem['Pendente']}   |   "
            f"Em andamento: {contagem['Em andamento']}   |   "
            f"Concluídas: {contagem['Concluída']}   |   Atrasadas: {atrasadas}"
        )
