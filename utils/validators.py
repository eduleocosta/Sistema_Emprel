import re
from datetime import datetime
import unicodedata
import tkinter as tk

# Somente digs
def somente_digs(s: str) -> str:
    return re.sub(r"\D", "", (s or ""))

# Normaliza texto ordenação
def normalizar_texto_ordenacao(valor) -> str:
    texto = str(valor or "").strip()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(ch for ch in texto if not unicodedata.combining(ch))
    return texto.casefold()

# Valida e-mail
def validar_email(email: str) -> bool:
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}", email or ""))

# Valida data nascimento
def validar_data_nascimento(data: str) -> bool:
    try:
        datetime.strptime(data, "%d/%m/%Y")
        return True
    except Exception:
        return False

# Valida CPF
def validar_cpf(cpf_raw: str) -> bool:
    cpf = somente_digs(cpf_raw)
    if len(cpf) != 11:
        return False
    if cpf == cpf[0] * 11:
        return False
    for i in range(9, 11):
        soma = sum(int(cpf[num]) * ((i + 1) - num) for num in range(0, i))
        dig = ((soma * 10) % 11) % 10
        if dig != int(cpf[i]):
            return False
    return True

# Formata telefone novo
def formatar_telefone_novo(numero: str) -> str:
    digitos = re.sub(r"\D", "", numero)

    if len(digitos) == 10:
        digitos = digitos[:2] + "9" + digitos[2:]
    elif len(digitos) != 11:
        return numero

    return f"({digitos[:2]}) {digitos[2]}.{digitos[3:7]}-{digitos[7:]}"

# Mascara CPF entrada
def mascara_cpf_entrada(entry: tk.Entry):
    txt = somente_digs(entry.get())[:11]
    out = ""
    if len(txt) > 0:
        out += txt[:3]
    if len(txt) >= 4:
        out = f"{txt[:3]}.{txt[3:6]}" if len(txt) >= 6 else f"{txt[:3]}.{txt[3:]}"
    if len(txt) >= 7:
        out = f"{out}.{txt[6:9]}" if len(txt) >= 9 else f"{out}.{txt[6:]}"
    if len(txt) >= 10:
        out = f"{out}-{txt[9:11]}"
    if entry.get() != out:
        entry.delete(0, tk.END)
        entry.insert(0, out)