import json
from datetime import datetime
from config import (
    DB_FILE, DB_USUARIOS, DB_ORGANIZACOES, HISTORICO_BACKUP,
    DB_ACOES, DB_SERVICOS, DB_VANS,
    DEFAULT_DB, PASTA_BACKUP_LOCAL, PASTA_BACKUP_NUVEM,
    APP_DIR, ARQUIVO_ACAO_ATIVA, PASTA_LISTAS, DB_ENTREGAS,
    DB_EXCLUIDOS_CADASTROS, DB_EXCLUIDOS_ACOES, DB_EXCLUIDOS_SERVICOS
)
import os

# Tenta usar SQLite; se não disponível, mantém JSON como fallback
_USO_SQLITE = True
try:
    from database.sqlite_core import (
        ensure_schema, load_usuarios, save_usuarios, load_db, save_db,
        save_cadastros, load_acoes, save_acoes, load_servicos, save_servicos,
        load_vans, save_vans, load_organizacoes, save_organizacoes,
        load_entregas, save_entregas, registrar_entrega, salvar_excluido,
        carregar_historico_backup, salvar_historico_backup,
        load_acao_ativa, save_acao_ativa_internal,
        load_modo_teste, save_modo_teste,
        salvar_lista_tree, carregar_lista_tree, listar_listas_entrega,
        save_sessao, load_sessao, remove_sessao,
    )
except Exception:
    _USO_SQLITE = False

# ---------- fallback JSON legado ----------
def _json_core_legacy():
    import json
    from config import DB_FILE, DB_USUARIOS, DB_ORGANIZACOES, DB_ACOES, DB_SERVICOS, DB_VANS, DEFAULT_DB, DB_ENTREGAS
    def ensure_db():
        if not os.path.exists(DB_FILE):
            with open(DB_FILE, "w", encoding="utf-8") as f:
                json.dump(DEFAULT_DB, f, indent=4, ensure_ascii=False)

    def load_db():
        ensure_db()
        with open(DB_FILE, "r", encoding="utf-8") as f:
            db = json.load(f)
        db["acoes"] = _load_acoes()
        db["servicos"] = _load_servicos()
        db["organizacoes"] = _load_organizacoes()
        db["vans"] = _load_vans()
        return db

    def save_db(db):
        core = {k: v for k, v in db.items() if k not in ("acoes", "servicos", "organizacoes", "vans")}
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(core, f, indent=4, ensure_ascii=False)
        if "acoes" in db:
            _save_acoes(db["acoes"])
        if "servicos" in db:
            _save_servicos(db["servicos"])
        if "organizacoes" in db:
            _save_organizacoes(db["organizacoes"])
        if "vans" in db:
            _save_vans(db["vans"])

    def _load_usuarios():
        if not os.path.exists(DB_USUARIOS):
            return {}
        with open(DB_USUARIOS, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_usuarios(usuarios):
        with open(DB_USUARIOS, "w", encoding="utf-8") as f:
            json.dump(usuarios, f, indent=4, ensure_ascii=False)

    def _load_acoes():
        if not os.path.exists(DB_ACOES):
            return []
        with open(DB_ACOES, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_acoes(acoes):
        with open(DB_ACOES, "w", encoding="utf-8") as f:
            json.dump(acoes, f, indent=4, ensure_ascii=False)

    def _load_servicos():
        if not os.path.exists(DB_SERVICOS):
            return []
        with open(DB_SERVICOS, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_servicos(servicos):
        with open(DB_SERVICOS, "w", encoding="utf-8") as f:
            json.dump(servicos, f, indent=4, ensure_ascii=False)

    def _load_vans():
        if not os.path.exists(DB_VANS):
            return []
        with open(DB_VANS, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_vans(vans):
        with open(DB_VANS, "w", encoding="utf-8") as f:
            json.dump(vans, f, indent=4, ensure_ascii=False)

    def _load_organizacoes():
        if not os.path.exists(DB_ORGANIZACOES):
            return []
        with open(DB_ORGANIZACOES, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_organizacoes(organizacoes):
        with open(DB_ORGANIZACOES, "w", encoding="utf-8") as f:
            json.dump(organizacoes, f, indent=4, ensure_ascii=False)

    def _load_entregas():
        if not os.path.exists(DB_ENTREGAS):
            return []
        with open(DB_ENTREGAS, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_entregas(entregas):
        with open(DB_ENTREGAS, "w", encoding="utf-8") as f:
            json.dump(entregas, f, indent=4, ensure_ascii=False)

    def _registrar_entrega(lista_dados, usuario_logado):
        entregas = _load_entregas()
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        for item in lista_dados:
            registro = {
                "data_entrega_registro": item.get("data_entrega") or timestamp,
                "operador": usuario_logado,
                "protocolo": item.get("protocolo", ""),
                "nome": item.get("nome", ""),
                "cpf": item.get("cpf", ""),
                "telefone": item.get("telefone", ""),
                "data_acao": item.get("data", ""),
                "acao": item.get("acao", ""),
                "acao_id": item.get("acao_id", ""),
                "servico_id": item.get("servico_id", ""),
            }
            entregas.append(registro)
        _save_entregas(entregas)

    return {
        "ensure_schema": lambda: None,
        "load_usuarios": _load_usuarios,
        "save_usuarios": _save_usuarios,
        "load_db": load_db,
        "save_db": save_db,
        "save_cadastros": lambda xs: save_db({"cadastros": xs, "organizacoes": _load_organizacoes()}),
        "load_acoes": _load_acoes,
        "save_acoes": _save_acoes,
        "load_servicos": _load_servicos,
        "save_servicos": _save_servicos,
        "load_vans": _load_vans,
        "save_vans": _save_vans,
        "load_organizacoes": _load_organizacoes,
        "save_organizacoes": _save_organizacoes,
        "load_entregas": _load_entregas,
        "save_entregas": _save_entregas,
        "registrar_entrega": _registrar_entrega,
        "salvar_excluido": lambda nome, tipo, item, usuario: None,
        "carregar_historico_backup": lambda: {"ultimo_backup": None, "ultimo_restore": None},
        "salvar_historico_backup": lambda h: None,
        "load_acao_ativa": lambda: None,
        "save_acao_ativa_internal": lambda a: None,
        "load_modo_teste": lambda: {},
        "save_modo_teste": lambda d: None,
        "salvar_lista_tree": lambda *a, **k: None,
        "carregar_lista_tree": lambda *a, **k: [],
        "listar_listas_entrega": lambda: [],
        "save_sessao": lambda k, v: None,
        "load_sessao": lambda k: "",
        "remove_sessao": lambda k: None,
    }

if not _USO_SQLITE:
    _CORE = _json_core_legacy()
else:
    ensure_schema()
    _CORE = {
        "ensure_schema": ensure_schema,
        "load_usuarios": load_usuarios,
        "save_usuarios": save_usuarios,
        "load_db": load_db,
        "save_db": save_db,
        "save_cadastros": save_cadastros,
        "load_acoes": load_acoes,
        "save_acoes": save_acoes,
        "load_servicos": load_servicos,
        "save_servicos": save_servicos,
        "load_vans": load_vans,
        "save_vans": save_vans,
        "load_organizacoes": load_organizacoes,
        "save_organizacoes": save_organizacoes,
        "load_entregas": load_entregas,
        "save_entregas": save_entregas,
        "registrar_entrega": registrar_entrega,
        "salvar_excluido": salvar_excluido,
        "carregar_historico_backup": carregar_historico_backup,
        "salvar_historico_backup": salvar_historico_backup,
        "load_acao_ativa": load_acao_ativa,
        "save_acao_ativa_internal": save_acao_ativa_internal,
        "load_modo_teste": load_modo_teste,
        "save_modo_teste": save_modo_teste,
        "salvar_lista_tree": salvar_lista_tree,
        "carregar_lista_tree": carregar_lista_tree,
        "listar_listas_entrega": listar_listas_entrega,
        "save_sessao": save_sessao,
        "load_sessao": load_sessao,
        "remove_sessao": remove_sessao,
    }

# Keep aliases so existing code continues working
def ensure_db(): return _CORE["ensure_schema"]()
def load_usuarios(): return _CORE["load_usuarios"]()
def save_usuarios(usuarios): return _CORE["save_usuarios"](usuarios)
def load_acoes(): return _CORE["load_acoes"]()
def save_acoes(acoes): return _CORE["save_acoes"](acoes)
def load_servicos(): return _CORE["load_servicos"]()
def save_servicos(servicos): return _CORE["save_servicos"](servicos)
def load_vans(): return _CORE["load_vans"]()
def save_vans(vans): return _CORE["save_vans"](vans)
def load_organizacoes(): return _CORE["load_organizacoes"]()
def save_organizacoes(organizacoes): return _CORE["save_organizacoes"](organizacoes)
def load_db(): return _CORE["load_db"]()
def save_db(db): return _CORE["save_db"](db)
def registrar_entrega_json_separado(lista_dados, usuario_logado):
    return _CORE["registrar_entrega"](lista_dados, usuario_logado)
def salvar_excluido(nome_arquivo, tipo, item, usuario_logado):
    return _CORE["salvar_excluido"](nome_arquivo, tipo, item, usuario_logado)
def carregar_historico_backup(): return _CORE["carregar_historico_backup"]()
def salvar_historico_backup(historico): return _CORE["salvar_historico_backup"](historico)
def load_acao_ativa(): return _CORE["load_acao_ativa"]()
def save_acao_ativa_interna(dados): return _CORE["save_acao_ativa_internal"](dados)
def load_modo_teste(): return _CORE["load_modo_teste"]()
def save_modo_teste(dados): return _CORE["save_modo_teste"](dados)
def salvar_lista_tree(tree, nome_arquivo=None, metadados=None):
    if not nome_arquivo:
        nome_arquivo = "lista_final_atual.json"
    itens = valores_lista_tree(tree)
    return _CORE["salvar_lista_tree"](nome_arquivo, metadados, itens)

def carregar_lista_tree(tree, nome_arquivo=None):
    if not nome_arquivo:
        nome_arquivo = "lista_final_atual.json"
    itens = _CORE["carregar_lista_tree"](nome_arquivo)
    for linha in itens:
        tree.insert("", "end", values=linha[:4])
def valores_lista_tree(tree):
    dados = []
    for item in tree.get_children():
        valores = tree.item(item)["values"]
        if valores:
            dados.append(list(valores))
    return dados
