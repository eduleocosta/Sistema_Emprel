import sys
import subprocess
import importlib

def verificar_dependencia(nome_pacote, nome_import=None):
    if nome_import is None:
        nome_import = nome_pacote
    try:
        importlib.import_module(nome_import)
        return True
    except ImportError:
        return False

def instalar_dependencia(pacote):
    print(f"Instalando {pacote}...")
    subprocess.check_call([
        sys.executable,
        "-m",
        "pip",
        "install",
        pacote,
        "--quiet"
    ])

def main():
    dependencias = [
        ("Pillow", "PIL"),
        ("ttkbootstrap", "ttkbootstrap"),
        ("customtkinter", "customtkinter"),
        ("reportlab", "reportlab"),
        ("pyautogui", "pyautogui"),
        ("pywin32", "win32gui"),
        ("pandas", "pandas"),
        ("openpyxl", "openpyxl"),
    ]

    faltando = []
    for pacote, nome_import in dependencias:
        if not verificar_dependencia(nome_import):
            faltando.append(pacote)

    if faltando:
        print("Dependências faltantes detectadas:")
        for pacote in faltando:
            print(f"  - {pacote}")
        print("\nInstalando automaticamente...")
        for pacote in faltando:
            instalar_dependencia(pacote)
        print("\nTodas as dependências foram instaladas.")
        print("Reiniciando o sistema...\n")
        subprocess.call([sys.executable, "sistema.py"])
        sys.exit(0)
    else:
        from sistema import App
        app = App()
        app.mainloop()

if __name__ == "__main__":
    main()
