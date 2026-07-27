import os
import sqlite3
from datetime import datetime
from config import DB_DIR, APP_DIR

DB_PATH = os.path.join(DB_DIR, "sistema_emprel.db")

def _conn():
    conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    return conn

def _migrate(conn):
    conn.executescript("""
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS usuarios (
    cpf TEXT PRIMARY KEY,
    nome TEXT NOT NULL,
    perfil TEXT NOT NULL DEFAULT 'user',
    email TEXT DEFAULT '',
    data_nascimento TEXT DEFAULT '',
    salt TEXT NOT NULL,
    hash TEXT NOT NULL,
    ativo INTEGER NOT NULL DEFAULT 1,
    senha_expirada INTEGER NOT NULL DEFAULT 1,
    ultima_troca_senha TEXT DEFAULT '',
    tentativas_recuperacao INTEGER NOT NULL DEFAULT 0,
    bloqueado_ate TEXT DEFAULT '',
    tentativas_login INTEGER NOT NULL DEFAULT 0,
    vans_permitidas TEXT DEFAULT '',
    van_ativa TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS acoes (
    id TEXT PRIMARY KEY,
    data TEXT DEFAULT '',
    local TEXT DEFAULT '',
    finalizada INTEGER NOT NULL DEFAULT 0,
    endereco TEXT DEFAULT '',
    latitude TEXT DEFAULT '',
    longitude TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS acoes_servicos (
    acao_id TEXT,
    servico_id TEXT,
    PRIMARY KEY (acao_id, servico_id)
);
CREATE TABLE IF NOT EXISTS acoes_organizacoes (
    acao_id TEXT,
    organizacao_nome TEXT,
    PRIMARY KEY (acao_id, organizacao_nome)
);
CREATE TABLE IF NOT EXISTS acoes_vans (
    acao_id TEXT,
    van_id TEXT,
    PRIMARY KEY (acao_id, van_id)
);
CREATE TABLE IF NOT EXISTS servicos (
    id TEXT PRIMARY KEY,
    nome TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS vans (
    id TEXT PRIMARY KEY,
    nome TEXT NOT NULL,
    descricao TEXT DEFAULT '',
    ativa INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS organizacoes (
    id TEXT PRIMARY KEY,
    nome TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS cadastros (
    id TEXT PRIMARY KEY,
    protocolo TEXT DEFAULT '',
    nome TEXT DEFAULT '',
    cpf TEXT DEFAULT '',
    telefone TEXT DEFAULT '',
    data TEXT DEFAULT '',
    acao TEXT DEFAULT '',
    servico_id TEXT DEFAULT '',
    entregue INTEGER NOT NULL DEFAULT 0,
    data_entrega TEXT DEFAULT '',
    operador_entrega TEXT DEFAULT '',
    acao_id TEXT DEFAULT '',
    van_id TEXT DEFAULT '',
    van_nome TEXT DEFAULT '',
    hora TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS cadastros_excluidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT NOT NULL,
    data_exclusao TEXT NOT NULL,
    operador TEXT NOT NULL,
    dados TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS acoes_excluidas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT NOT NULL,
    data_exclusao TEXT NOT NULL,
    operador TEXT NOT NULL,
    dados TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS entregas_confirmadas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data_entrega_registro TEXT NOT NULL,
    operador TEXT NOT NULL,
    protocolo TEXT NOT NULL,
    nome TEXT NOT NULL,
    cpf TEXT NOT NULL,
    telefone TEXT DEFAULT '',
    data_acao TEXT DEFAULT '',
    acao TEXT DEFAULT '',
    acao_id TEXT DEFAULT '',
    servico_id TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS backup_historico (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    ultimo_backup TEXT,
    ultimo_restore TEXT
);
CREATE TABLE IF NOT EXISTS acao_ativa (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    acao TEXT,
    servico TEXT
);
CREATE TABLE IF NOT EXISTS modo_teste (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    ativo INTEGER NOT NULL DEFAULT 0,
    expira_em TEXT DEFAULT '',
    prorrogacoes INTEGER NOT NULL DEFAULT 0,
    max_prorrogacoes INTEGER NOT NULL DEFAULT 5,
    duracao_minutos INTEGER NOT NULL DEFAULT 10,
    admin_ativou TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS perguntas_modo_teste (
    id INTEGER PRIMARY KEY,
    pergunta TEXT NOT NULL,
    resposta TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS listas_entrega (
    nome_arquivo TEXT PRIMARY KEY,
    metadados TEXT NOT NULL DEFAULT '{}',
    itens TEXT NOT NULL DEFAULT '[]'
);
CREATE TABLE IF NOT EXISTS sistema_sessao (
    chave TEXT PRIMARY KEY,
    valor TEXT NOT NULL DEFAULT ''
);
""")

def ensure_schema():
    conn = _conn()
    _migrate(conn)
    conn.commit()
    conn.close()

def _row_to_dict(row):
    if row is None:
        return None
    d = dict(row)
    for k, v in list(d.items()):
        if isinstance(v, bytes):
            d[k] = v.decode("utf-8", errors="ignore")
    return d

def now_str():
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")

# ---------- usuarios ----------
def load_usuarios():
    ensure_schema()
    conn = _conn()
    rows = conn.execute("SELECT * FROM usuarios").fetchall()
    conn.close()
    out = {}
    for r in rows:
        d = _row_to_dict(r)
        out[d["cpf"]] = {
            "nome": d["nome"],
            "perfil": d["perfil"],
            "email": d["email"],
            "data_nascimento": d["data_nascimento"],
            "salt": d["salt"],
            "hash": d["hash"],
            "ativo": bool(d["ativo"]),
            "senha_expirada": bool(d["senha_expirada"]),
            "ultima_troca_senha": d["ultima_troca_senha"],
            "tentativas_recuperacao": d["tentativas_recuperacao"],
            "bloqueado_ate": d["bloqueado_ate"],
            "tentativas_login": d["tentativas_login"],
            "vans_permitidas": d["vans_permitidas"],
            "van_ativa": d["van_ativa"],
        }
    return out

def save_usuarios(usuarios):
    ensure_schema()
    conn = _conn()
    for cpf, dados in usuarios.items():
        conn.execute("""
            INSERT INTO usuarios (cpf, nome, perfil, email, data_nascimento, salt, hash, ativo, senha_expirada, ultima_troca_senha, tentativas_recuperacao, bloqueado_ate, tentativas_login, vans_permitidas, van_ativa)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(cpf) DO UPDATE SET
                nome=excluded.nome, perfil=excluded.perfil, email=excluded.email, data_nascimento=excluded.data_nascimento,
                salt=excluded.salt, hash=excluded.hash, ativo=excluded.ativo, senha_expirada=excluded.senha_expirada,
                ultima_troca_senha=excluded.ultima_troca_senha, tentativas_recuperacao=excluded.tentativas_recuperacao,
                bloqueado_ate=excluded.bloqueado_ate, tentativas_login=excluded.tentativas_login,
                vans_permitidas=excluded.vans_permitidas, van_ativa=excluded.van_ativa
        """, (
            cpf,
            dados.get("nome", ""),
            dados.get("perfil", "user"),
            dados.get("email", ""),
            dados.get("data_nascimento", ""),
            dados.get("salt", ""),
            dados.get("hash", ""),
            1 if dados.get("ativo", True) else 0,
            1 if dados.get("senha_expirada", True) else 0,
            dados.get("ultima_troca_senha", ""),
            dados.get("tentativas_recuperacao", 0),
            dados.get("bloqueado_ate", ""),
            dados.get("tentativas_login", 0),
            dados.get("vans_permitidas", ""),
            dados.get("van_ativa", ""),
        ))
    conn.commit()
    conn.close()

# ---------- db.json equivalent ----------
def load_db():
    ensure_schema()
    conn = _conn()
    row = conn.execute("SELECT * FROM cadastros").fetchall()
    conn.close()
    cadastros = [_row_to_dict(r) for r in row]
    return {
        "cadastros": cadastros,
        "organizacoes": load_organizacoes(),
        "migracao_tel_v2": True,
        "acao_ativa": load_acao_ativa().get("acao") if isinstance(load_acao_ativa(), dict) else None,
    }

def save_db(db):
    save_cadastros(db.get("cadastros", []))
    if "organizacoes" in db:
        save_organizacoes(db["organizacoes"])
    if "acao_ativa" in db:
        save_acao_ativa_internal(db["acao_ativa"])

def save_cadastros(cadastros):
    ensure_schema()
    conn = _conn()
    conn.execute("DELETE FROM cadastros")
    for item in cadastros:
        conn.execute("""
            INSERT INTO cadastros (id, protocolo, nome, cpf, telefone, data, acao, servico_id, entregue, data_entrega, operador_entrega, acao_id, van_id, van_nome, hora)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            str(item.get("id")),
            item.get("protocolo", ""),
            item.get("nome", ""),
            item.get("cpf", ""),
            item.get("telefone", ""),
            item.get("data", ""),
            item.get("acao", ""),
            item.get("servico_id", ""),
            1 if item.get("entregue") else 0,
            item.get("data_entrega", ""),
            item.get("operador_entrega", ""),
            item.get("acao_id", ""),
            item.get("van_id", ""),
            item.get("van_nome", ""),
            item.get("hora", ""),
        ))
    conn.commit()
    conn.close()

# ---------- acoes ----------
def load_acoes():
    ensure_schema()
    conn = _conn()
    rows = conn.execute("SELECT * FROM acoes ORDER BY rowid").fetchall()
    conn.close()
    out = []
    for r in rows:
        d = _row_to_dict(r)
        item = {
            "id": d["id"],
            "data": d["data"],
            "local": d.get("local", ""),
            "finalizada": bool(d["finalizada"]),
            "endereco": d.get("endereco", ""),
            "latitude": d.get("latitude", ""),
            "longitude": d.get("longitude", ""),
        }
        conn2 = _conn()
        servs = [row["servico_id"] for row in conn2.execute("SELECT servico_id FROM acoes_servicos WHERE acao_id=?", (d["id"],)).fetchall()]
        orgs = [row["organizacao_nome"] for row in conn2.execute("SELECT organizacao_nome FROM acoes_organizacoes WHERE acao_id=?", (d["id"],)).fetchall()]
        vans = [row["van_id"] for row in conn2.execute("SELECT van_id FROM acoes_vans WHERE acao_id=?", (d["id"],)).fetchall()]
        conn2.close()
        item["servicos"] = servs
        item["organizacoes"] = orgs
        item["vans"] = vans
        out.append(item)
    return out

def save_acoes(acoes):
    ensure_schema()
    conn = _conn()
    conn.execute("DELETE FROM acoes")
    conn.execute("DELETE FROM acoes_servicos")
    conn.execute("DELETE FROM acoes_organizacoes")
    conn.execute("DELETE FROM acoes_vans")
    for item in acoes:
        conn.execute("""
            INSERT INTO acoes (id, data, local, finalizada, endereco, latitude, longitude)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            str(item.get("id")),
            item.get("data", ""),
            item.get("local", ""),
            1 if item.get("finalizada") else 0,
            item.get("endereco", ""),
            item.get("latitude", ""),
            item.get("longitude", ""),
        ))
        for sid in item.get("servicos", []) or []:
            conn.execute("INSERT OR IGNORE INTO acoes_servicos (acao_id, servico_id) VALUES (?, ?)", (str(item.get("id")), str(sid)))
        for oname in item.get("organizacoes", []) or []:
            conn.execute("INSERT OR IGNORE INTO acoes_organizacoes (acao_id, organizacao_nome) VALUES (?, ?)", (str(item.get("id")), oname))
        for vid in item.get("vans", []) or []:
            conn.execute("INSERT OR IGNORE INTO acoes_vans (acao_id, van_id) VALUES (?, ?)", (str(item.get("id")), str(vid)))
    conn.commit()
    conn.close()

# ---------- servicos ----------
def load_servicos():
    ensure_schema()
    conn = _conn()
    rows = conn.execute("SELECT * FROM servicos ORDER BY rowid").fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]

def save_servicos(servicos):
    ensure_schema()
    conn = _conn()
    conn.execute("DELETE FROM servicos")
    for item in servicos:
        conn.execute("INSERT INTO servicos (id, nome) VALUES (?, ?)", (str(item.get("id")), item.get("nome", "")))
    conn.commit()
    conn.close()

# ---------- vans ----------
def load_vans():
    ensure_schema()
    conn = _conn()
    rows = conn.execute("SELECT * FROM vans ORDER BY rowid").fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]

def save_vans(vans):
    ensure_schema()
    conn = _conn()
    conn.execute("DELETE FROM vans")
    for item in vans:
        conn.execute("INSERT INTO vans (id, nome, descricao, ativa) VALUES (?, ?, ?, ?)", (
            str(item.get("id")), item.get("nome", ""), item.get("descricao", ""), 1 if item.get("ativa") else 0))
    conn.commit()
    conn.close()

# ---------- organizacoes ----------
def load_organizacoes():
    ensure_schema()
    conn = _conn()
    rows = conn.execute("SELECT * FROM organizacoes ORDER BY rowid").fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]

def save_organizacoes(organizacoes):
    ensure_schema()
    conn = _conn()
    conn.execute("DELETE FROM organizacoes")
    for item in organizacoes:
        conn.execute("INSERT INTO organizacoes (id, nome) VALUES (?, ?)", (str(item.get("id")), item.get("nome", "")))
    conn.commit()
    conn.close()

# ---------- entregas ----------
def load_entregas():
    ensure_schema()
    conn = _conn()
    rows = conn.execute("SELECT * FROM entregas_confirmadas ORDER BY rowid").fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]

def save_entregas(entregas):
    ensure_schema()
    conn = _conn()
    conn.execute("DELETE FROM entregas_confirmadas")
    for item in entregas:
        conn.execute("""
            INSERT INTO entregas_confirmadas (data_entrega_registro, operador, protocolo, nome, cpf, telefone, data_acao, acao, acao_id, servico_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item.get("data_entrega_registro", ""),
            item.get("operador", ""),
            item.get("protocolo", ""),
            item.get("nome", ""),
            item.get("cpf", ""),
            item.get("telefone", ""),
            item.get("data_acao", ""),
            item.get("acao", ""),
            item.get("acao_id", ""),
            item.get("servico_id", ""),
        ))
    conn.commit()
    conn.close()

def registrar_entrega(lista_dados, usuario_logado):
    ensure_schema()
    conn = _conn()
    timestamp = now_str()
    for item in lista_dados:
        data_entrega = item.get("data_entrega") or timestamp
        conn.execute("""
            INSERT INTO entregas_confirmadas (data_entrega_registro, operador, protocolo, nome, cpf, telefone, data_acao, acao, acao_id, servico_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data_entrega,
            usuario_logado,
            item.get("protocolo", ""),
            item.get("nome", ""),
            item.get("cpf", ""),
            item.get("telefone", ""),
            item.get("data", ""),
            item.get("acao", ""),
            item.get("acao_id", ""),
            item.get("servico_id", ""),
        ))
    conn.commit()
    conn.close()

# ---------- excluidos ----------
def salvar_excluido(tabela, tipo, item, usuario_logado):
    ensure_schema()
    conn = _conn()
    conn.execute("""
        INSERT INTO %s (tipo, data_exclusao, operador, dados) VALUES (?, ?, ?, ?)
    """ % tabela, (tipo, now_str(), usuario_logado, json.dumps(item, ensure_ascii=False)))
    conn.commit()
    conn.close()

# ---------- backup historico ----------
def carregar_historico_backup():
    ensure_schema()
    conn = _conn()
    row = conn.execute("SELECT * FROM backup_historico WHERE id=1").fetchone()
    conn.close()
    if not row:
        return {"ultimo_backup": None, "ultimo_restore": None}
    return {"ultimo_backup": row["ultimo_backup"], "ultimo_restore": row["ultimo_restore"]}

def salvar_historico_backup(historico):
    ensure_schema()
    conn = _conn()
    conn.execute("""
        INSERT INTO backup_historico (id, ultimo_backup, ultimo_restore) VALUES (1, ?, ?)
        ON CONFLICT(id) DO UPDATE SET ultimo_backup=excluded.ultimo_backup, ultimo_restore=excluded.ultimo_restore
    """, (historico.get("ultimo_backup"), historico.get("ultimo_restore")))
    conn.commit()
    conn.close()

# ---------- acao ativa ----------
def load_acao_ativa():
    ensure_schema()
    conn = _conn()
    row = conn.execute("SELECT * FROM acao_ativa WHERE id=1").fetchone()
    conn.close()
    if not row or not row["acao"]:
        return None
    try:
        acao = json.loads(row["acao"] or "{}") if row["acao"] else None
    except Exception:
        acao = None
    servico = None
    try:
        servico = json.loads(row["servico"] or "{}") if row["servico"] else None
    except Exception:
        servico = None
    return {"acao": acao, "servico": servico}

def save_acao_ativa_internal(acao_ativa):
    ensure_schema()
    acao = None
    servico = None
    if isinstance(acao_ativa, dict):
        acao = json.dumps(acao_ativa.get("acao", {}), ensure_ascii=False) if acao_ativa.get("acao") else None
        servico = json.dumps(acao_ativa.get("servico", {}), ensure_ascii=False) if acao_ativa.get("servico") else None
    conn = _conn()
    conn.execute("""
        INSERT INTO acao_ativa (id, acao, servico) VALUES (1, ?, ?)
        ON CONFLICT(id) DO UPDATE SET acao=excluded.acao, servico=excluded.servico
    """, (acao, servico))
    conn.commit()
    conn.close()

# ---------- modo_teste ----------
def load_modo_teste():
    ensure_schema()
    conn = _conn()
    row = conn.execute("SELECT * FROM modo_teste WHERE id=1").fetchone()
    conn.close()
    if not row:
        return {
            "ativo": False, "expira_em": "", "prorrogacoes": 0,
            "max_prorrogacoes": 5, "duracao_minutos": 10, "admin_ativou": ""
        }
    d = _row_to_dict(row)
    return {
        "ativo": bool(d["ativo"]),
        "expira_em": d["expira_em"],
        "prorrogacoes": d["prorrogacoes"],
        "max_prorrogacoes": d["max_prorrogacoes"],
        "duracao_minutos": d["duracao_minutos"],
        "admin_ativou": d["admin_ativou"],
    }

def save_modo_teste(dados):
    ensure_schema()
    conn = _conn()
    conn.execute("""
        INSERT INTO modo_teste (id, ativo, expira_em, prorrogacoes, max_prorrogacoes, duracao_minutos, admin_ativou)
        VALUES (1, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET ativo=excluded.ativo, expira_em=excluded.expira_em, prorrogacoes=excluded.prorrogacoes, max_prorrogacoes=excluded.max_prorrogacoes, duracao_minutos=excluded.duracao_minutos, admin_ativou=excluded.admin_ativou
    """, (
        1 if dados.get("ativo") else 0,
        dados.get("expira_em", ""),
        dados.get("prorrogacoes", 0),
        dados.get("max_prorrogacoes", 5),
        dados.get("duracao_minutos", 10),
        dados.get("admin_ativou", ""),
    ))
    conn.commit()
    conn.close()

# ---------- listas entregas ----------
def salvar_lista_tree(nome_arquivo, metadados, itens):
    ensure_schema()
    conn = _conn()
    conn.execute("""
        INSERT INTO listas_entrega (nome_arquivo, metadados, itens)
        VALUES (?, ?, ?)
        ON CONFLICT(nome_arquivo) DO UPDATE SET metadados=excluded.metadados, itens=excluded.itens
    """, (nome_arquivo, json.dumps(metadados or {}, ensure_ascii=False), json.dumps(itens or [], ensure_ascii=False)))
    conn.commit()
    conn.close()

def carregar_lista_tree(nome_arquivo):
    ensure_schema()
    conn = _conn()
    row = conn.execute("SELECT * FROM listas_entrega WHERE nome_arquivo=?", (nome_arquivo,)).fetchone()
    conn.close()
    if not row:
        return []
    return json.loads(row["itens"] or "[]")

def listar_listas_entrega():
    ensure_schema()
    conn = _conn()
    rows = conn.execute("SELECT nome_arquivo, metadados FROM listas_entrega").fetchall()
    conn.close()
    return [_row_to_dict(r) for r in rows]

# ---------- sessao ----------
def save_sessao(chave, valor):
    ensure_schema()
    conn = _conn()
    conn.execute("""
        INSERT INTO sistema_sessao (chave, valor) VALUES (?, ?)
        ON CONFLICT(chave) DO UPDATE SET valor=excluded.valor
    """, (chave, valor))
    conn.commit()
    conn.close()

def load_sessao(chave):
    ensure_schema()
    conn = _conn()
    row = conn.execute("SELECT valor FROM sistema_sessao WHERE chave=?", (chave,)).fetchone()
    conn.close()
    return row["valor"] if row else ""

def remove_sessao(chave):
    ensure_schema()
    conn = _conn()
    conn.execute("DELETE FROM sistema_sessao WHERE chave=?", (chave,))
    conn.commit()
    conn.close()
