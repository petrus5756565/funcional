import tkinter as tk

from interface import AppTarefas, TelaLogin, configurar_estilos


def main():
    janela = tk.Tk()
    configurar_estilos(janela)

    def abrir_aplicativo():
        # Remove a tela de login e monta o gerenciador na mesma janela.
        for widget in janela.winfo_children():
            widget.destroy()
        AppTarefas(janela)

    # O login é a primeira tela: só depois dele as tarefas aparecem.
    TelaLogin(janela, ao_entrar=abrir_aplicativo)
    janela.mainloop()


if __name__ == "__main__":
    main()
