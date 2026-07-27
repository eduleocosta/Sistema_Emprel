import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from config import APP_TITLE, THEME
from database.core import load_db, load_usuarios
from database.models import migrar_usuarios_novos_campos, migrar_telefones_antigos, migrar_servicos_antigos, migrar_cadastros_acoes_orfas, migrar_organizacoes
from utils.validators import validar_cpf, validar_data_nascimento, validar_email, mascara_cpf_entrada, mask_cpf_from_clean, senha_expirada_60_dias

# Constrói a tela login tela
def build_login_screen(self):
    self._clear_screen()
    self._clear()

    container = tb.Frame(self, padding=24)
    container.pack(fill="both", expand=True)

    from views.home_view import criar_cabecalho_login
    criar_cabecalho_login(self, container)

    card = self._criar_card(container, padding=22, bootstyle="light")
    tb.Label(
        card,
        text="Faça login para acessar o sistema",
        font=("Segoe UI", 14, "bold")
    ).pack(pady=(0, 12))

    tb.Label(card, text="Login (CPF):", font=("Segoe UI", 10, "bold")).pack(anchor="w")
    self.login_user = tb.Entry(card, width=30)
    self.login_user.pack(fill="x", pady=(5, 10))
    self.login_user.bind("<KeyRelease>", lambda e: mascara_cpf_entrada(self.login_user))

    tb.Label(card, text="Senha:", font=("Segoe UI", 10, "bold")).pack(anchor="w")
    self.login_pass = tb.Entry(card, width=30, show="*")
    self.login_pass.pack(fill="x", pady=(5, 8))

    tb.Button(
        card,
        text="Recuperar senha",
        bootstyle="link",
        command=self._recuperar_senha_offline
    ).pack(anchor="w", pady=(0, 12))

    botoes = tb.Frame(card)
    botoes.pack(fill="x")
    botoes.columnconfigure(0, weight=1)

    tb.Button(
        botoes,
        text="Entrar",
        bootstyle="success",
        width=14,
        command=self._entrar
    ).grid(row=0, column=0, sticky="ew")

    self.update_idletasks()
    req_w = self.winfo_reqwidth()
    req_h = self.winfo_reqheight()
    screen_w = self.winfo_screenwidth()
    screen_h = self.winfo_screenheight()
    largura = min(req_w + 40, max(420, screen_w - 80))
    altura = min(req_h + 40, max(360, screen_h - 120))
    x = max(0, (screen_w // 2) - (largura // 2))
    y = max(0, (screen_h // 2) - (altura // 2))
    self.geometry(f"{largura}x{altura}+{x}+{y}")
    self.minsize(420, 360)