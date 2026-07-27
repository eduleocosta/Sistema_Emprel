import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    DB_FILE, DB_USUARIOS, DB_ORGANIZACOES,
    DB_ACOES, DB_SERVICOS, DB_VANS, DEFAULT_DB,
    DB_ENTREGAS, DB_EXCLUIDOS_CADASTROS, DB_EXCLUIDOS_ACOES, HISTORICO_BACKUP,
    ARQUIVO_ACAO_ATIVA, APP_DIR, PASTA_LISTAS
)

from database.sqlite_core import (
    ensure_schema, save_usuarios, save_acoes, save_servicos, save_vans,
    save_organizacoes, save_cadastros, save_entregas, salvar_excluido,
    salvar_historico_backup, save_acao_ativa_internal, save_modo_teste,
    salvar_lista_tree, carregar_lista_tree
)

def _read_json(path, default=None):
    if not os.path.exists(path):
        return default if default is not None else []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default if default is not None else []

def _load_db_json():
    db_path = DB_FILE.replace(".db", ".json")
    return _read_json(db_path, DEFAULT_DB)

def _load_acao_ativa_json():
    return _read_json(ARQUIVO_ACAO_ATIVA)

def migrate():
    ensure_schema()
    print("Schema SQLite pronto.")

    # usuarios
    usuarios = _read_json(DB_USUARIOS, {})
    if usuarios:
        save_usuarios(usuarios)
    print("Usuarios migrados:", len(usuarios))

    # cadastros + organizacoes
    db = _load_db_json()
    save_cadastros(db.get("cadastros", []))
    save_organizacoes(db.get("organizacoes", []))
    print("Cadastros migrados:", len(db.get("cadastros", [])))
    print("Organizacoes migradas:", len(db.get("organizacoes", [])))

    # extras
    save_acoes(_read_json(DB_ACOES, []))
    save_servicos(_read_json(DB_SERVICOS, []))
    save_vans(_read_json(DB_VANS, []))
    save_entregas(_read_json(DB_ENTREGAS, []))

    # excluidos
    if os.path.exists(DB_EXCLUIDOS_CADASTROS):
        try:
            with open(DB_EXCLUIDOS_CADASTROS, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                for item in data:
                    salvar_excluido("cadastros_excluidos", item.get("tipo", "cadastro"), item, item.get("operador", ""))
        except Exception:
            pass
    if os.path.exists(DB_EXCLUIDOS_ACOES):
        try:
            with open(DB_EXCLUIDOS_ACOES, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                for item in data:
                    salvar_excluido("acoes_excluidas", item.get("tipo", "acao"), item, item.get("operador", ""))
        except Exception:
            pass

    # historico backup
    historico = _read_json(HISTORICO_BACKUP, {})
    if not historico:
        historico = {"ultimo_backup": None, "ultimo_restore": None}
    salvar_historico_backup(historico)

    # acao ativa
    acao_ativa = _read_json(ARQUIVO_ACAO_ATIVA)
    save_acao_ativa_internal(acao_ativa)

    # modo_teste
    modo_teste_path = os.path.join(APP_DIR, "modo_teste.json")
    save_modo_teste(_read_json(modo_teste_path, {
        "ativo": False, "expira_em": "", "prorrogacoes": 0,
        "max_prorrogacoes": 5, "duracao_minutos": 10, "admin_ativou": ""
    }))

    # perguntas_modo_teste
    perguntas = _read_json(os.path.join(APP_DIR, "perguntas_modo_teste.json"), [])
    if perguntas:
        ensure_schema()
        import sqlite3
        conn = sqlite3.connect(DB_FILE)
        conn.execute("DELETE FROM perguntas_modo_teste")
        for p in perguntas:
            conn.execute("INSERT INTO perguntas_modo_teste (id, pergunta, resposta) VALUES (?, ?, ?)",
                         (p.get("id"), p.get("pergunta", ""), p.get("resposta", "")))
        conn.commit()
        conn.close()

    # listas_entrega
    if os.path.isdir(PASTA_LISTAS):
        for nome in os.listdir(PASTA_LISTAS):
            if nome.endswith(".json"):
                caminho = os.path.join(PASTA_LISTAS, nome)
                with open(caminho, "r", encoding="utf-8") as f:
                    try:
                        payload = json.load(f)
                    except Exception:
                        continue
                itens = payload.get("itens", []) if isinstance(payload, dict) else payload
                metadados = payload.get("metadados", {}) if isinstance(payload, dict) else {}
                salvar_lista_tree(nome, metadados, itens)
    print("Listas de entrega migradas.")

    print("Migracao concluida.")

if __name__ == "__main__":
    migrate()
