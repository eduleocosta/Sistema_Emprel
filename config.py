import os
import sys

APP_TITLE = "RG SOLICITADOS"
THEME = "flatly"

APP_DIR = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))
os.chdir(APP_DIR)

DB_DIR = APP_DIR
os.makedirs(DB_DIR, exist_ok=True)

PASTA_LISTAS = os.path.join(APP_DIR, "listas_entrega")
if not os.path.exists(PASTA_LISTAS):
    os.makedirs(PASTA_LISTAS)

PASTA_DOC = os.path.join(APP_DIR, "doc")
PASTA_IMG = os.path.join(APP_DIR, "img")

ARQUIVO_ACAO_ATIVA = os.path.join(APP_DIR, "acao_ativa.json")
PASTA_BACKUP_LOCAL = r"C:\Projetos\backup_sistema_emprel"
PASTA_BACKUP_NUVEM = os.path.join(APP_DIR, "backup_sistema_emprel")

DB_FILE = os.path.join(DB_DIR, "sistema_emprel.db")
DB_USUARIOS = os.path.join(DB_DIR, "usuarios.json")
DB_ACOES = os.path.join(DB_DIR, "acoes.json")
DB_SERVICOS = os.path.join(DB_DIR, "servicos.json")
DB_VANS = os.path.join(DB_DIR, "vans.json")
DB_ENTREGAS = os.path.join(DB_DIR, "entregas_confirmadas.json")
DB_EXCLUIDOS_CADASTROS = os.path.join(DB_DIR, "cadastros_excluidos.json")
DB_EXCLUIDOS_ACOES = os.path.join(DB_DIR, "acoes_excluidas.json")
DB_EXCLUIDOS_SERVICOS = os.path.join(DB_DIR, "servicos_excluidos.json")
DB_ORGANIZACOES = os.path.join(DB_DIR, "organizacoes.json")
HISTORICO_BACKUP = os.path.join(DB_DIR, "backup_historico.json")

DEFAULT_DB = {
    "cadastros": [],
    "organizacoes": []
}

# Resource path
def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)