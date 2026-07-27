import sys
import os
import json
import hashlib
import secrets
import re

APP_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(APP_DIR)
sys.path.insert(0, PARENT_DIR)

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

app = FastAPI(title="RG Solicitados")

app.add_middleware(SessionMiddleware, secret_key="rg-solicitados-secret-key-2026")


class NoCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        if response.headers.get("content-type", "").startswith("text/html"):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response


app.add_middleware(NoCacheMiddleware)

templates = Jinja2Templates(directory=os.path.join(APP_DIR, "templates"))

app.mount("/static", StaticFiles(directory=os.path.join(APP_DIR, "static")), name="static")

db_path = os.path.join(PARENT_DIR, "db.json")
usuarios_path = os.path.join(PARENT_DIR, "usuarios.json")
acoes_path = os.path.join(PARENT_DIR, "acoes.json")
servicos_path = os.path.join(PARENT_DIR, "servicos.json")
vans_path = os.path.join(PARENT_DIR, "vans.json")
organizacoes_path = os.path.join(PARENT_DIR, "organizacoes.json")


def somente_digs(value: str) -> str:
    return re.sub(r"\D", "", value or "")


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


def load_json(path, default=None):
    if not os.path.exists(path):
        return default if default is not None else []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default if default is not None else []


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        f.flush()
        try:
            os.fsync(f.fileno())
        except Exception:
            pass


def get_current_user(request: Request):
    return request.session.get("user")


def require_login(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login", status_code=302)
    return None


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    if get_current_user(request):
        return RedirectResponse("/home", status_code=302)
    db = load_json(db_path, {"cadastros": [], "organizacoes": []})
    acoes = load_json(acoes_path, [])
    vans = load_json(vans_path, [])
    return templates.TemplateResponse("index.html", {
        "request": request,
        "acoes": acoes,
        "vans": vans,
    })


@app.get("/home", response_class=HTMLResponse)
async def home(request: Request):
    redirect = require_login(request)
    if redirect:
        return redirect
    response = templates.TemplateResponse("home.html", {"request": request})
    response.headers["Cache-Control"] = "no-store"
    return response


@app.get("/login", response_class=HTMLResponse)
async def tela_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/acesso", response_class=HTMLResponse)
async def tela_acesso(request: Request):
    redirect = require_login(request)
    if redirect:
        return redirect
    return templates.TemplateResponse("acesso.html", {"request": request})


@app.post("/api/login")
async def login(request: Request):
    data = await request.json()
    usuarios = load_json(usuarios_path, {})
    cpf = somente_digs(data.get("cpf", ""))
    senha = data.get("senha", "")
    if cpf in usuarios:
        user = usuarios[cpf]
        salt_hex = user.get("salt", "")
        hash_hex = user.get("hash", "")
        if not salt_hex or not hash_hex:
            return JSONResponse({"status": "error", "message": "Credenciais inválidas"})
        salt = bytes.fromhex(salt_hex)
        attempt = hashlib.pbkdf2_hmac("sha256", senha.encode("utf-8"), salt, 120_000).hex()
        if secrets.compare_digest(attempt, hash_hex):
            request.session["user"] = {
                "cpf": cpf,
                "nome": user.get("nome", ""),
                "perfil": user.get("perfil", "user"),
            }
            return JSONResponse({"status": "ok", "nome": user.get("nome", ""), "perfil": user.get("perfil", "user")})
    return JSONResponse({"status": "error", "message": "Credenciais inválidas"})


@app.post("/api/logout")
async def logout(request: Request):
    request.session.pop("user", None)
    return JSONResponse({"status": "ok"})


@app.get("/api/session")
async def get_session(request: Request):
    user = get_current_user(request)
    if user:
        return JSONResponse({"logged": True, "user": user})
    return JSONResponse({"logged": False})


@app.get("/api/usuarios")
async def listar_usuarios(request: Request):
    redirect = require_login(request)
    if redirect:
        return redirect
    usuarios = load_json(usuarios_path, {})
    termo = (request.query_params.get("pesquisa") or "").strip().lower()
    resultado = []
    for cpf, dados in usuarios.items():
        if termo:
            nome = dados.get("nome", "").lower()
            if termo not in nome and termo not in cpf:
                continue
        resultado.append({
            "cpf": cpf,
            "nome": dados.get("nome", ""),
            "perfil": dados.get("perfil", "user"),
            "email": dados.get("email", ""),
            "data_nascimento": dados.get("data_nascimento", ""),
            "ativo": dados.get("ativo", True),
        })
    return resultado


@app.post("/api/usuarios")
async def salvar_usuario(request: Request):
    redirect = require_login(request)
    if redirect:
        return redirect
    data = await request.json()
    cpf = somente_digs(data.get("cpf", ""))
    if not validar_cpf(cpf):
        return JSONResponse({"status": "error", "message": "CPF inválido"})
    nome = (data.get("nome") or "").strip().upper()
    if not nome:
        return JSONResponse({"status": "error", "message": "Informe o nome"})
    dn = (data.get("data_nascimento") or "").strip()
    email = (data.get("email") or "").strip()
    senha = (data.get("senha") or "").strip()
    perfil = data.get("perfil") or "user"
    usuarios = load_json(usuarios_path, {})
    if cpf in usuarios:
        return JSONResponse({"status": "error", "message": "Usuário já existe"})
    if not senha or len(senha) < 4:
        return JSONResponse({"status": "error", "message": "Senha deve ter ao menos 4 caracteres"})
    salt = secrets.token_bytes(16)
    hash_pw = hashlib.pbkdf2_hmac("sha256", senha.encode("utf-8"), salt, 120_000).hex()
    usuarios[cpf] = {
        "nome": nome,
        "cpf": cpf,
        "perfil": perfil,
        "email": email,
        "data_nascimento": dn,
        "salt": salt.hex(),
        "hash": hash_pw,
        "ativo": True,
        "senha_expirada": True,
        "ultima_troca_senha": datetime.now().strftime("%d/%m/%Y"),
        "tentativas_login": 0,
        "tentativas_recuperacao": 0,
        "bloqueado_ate": "",
    }
    save_json(usuarios_path, usuarios)
    return JSONResponse({"status": "ok"})


@app.put("/api/usuarios/{cpf}")
async def atualizar_usuario(cpf: str, request: Request):
    redirect = require_login(request)
    if redirect:
        return redirect
    data = await request.json()
    cpf = somente_digs(cpf)
    usuarios = load_json(usuarios_path, {})
    if cpf not in usuarios:
        return JSONResponse({"status": "error", "message": "Usuário não encontrado"})
    nome = (data.get("nome") or "").strip().upper()
    email = (data.get("email") or "").strip()
    dn = (data.get("data_nascimento") or "").strip()
    perfil = data.get("perfil") or usuarios[cpf].get("perfil", "user")
    ativo = data.get("ativo")
    if ativo is None:
        ativo = usuarios[cpf].get("ativo", True)
    if not nome:
        return JSONResponse({"status": "error", "message": "Nome é obrigatório"})
    usuarios[cpf]["nome"] = nome
    usuarios[cpf]["email"] = email
    usuarios[cpf]["data_nascimento"] = dn
    usuarios[cpf]["perfil"] = perfil
    usuarios[cpf]["ativo"] = bool(ativo)
    save_json(usuarios_path, usuarios)
    return JSONResponse({"status": "ok"})


@app.delete("/api/usuarios/{cpf}")
async def excluir_usuario(cpf: str, request: Request):
    redirect = require_login(request)
    if redirect:
        return redirect
    cpf = somente_digs(cpf)
    usuarios = load_json(usuarios_path, {})
    if cpf not in usuarios:
        return JSONResponse({"status": "error", "message": "Usuário não encontrado"})
    usuarios.pop(cpf, None)
    save_json(usuarios_path, usuarios)
    return JSONResponse({"status": "ok"})


@app.post("/api/usuarios/{cpf}/senha")
async def redefinir_senha_usuario(cpf: str, request: Request):
    redirect = require_login(request)
    if redirect:
        return redirect
    data = await request.json()
    cpf = somente_digs(cpf)
    nova = (data.get("senha") or "").strip()
    if not nova or len(nova) < 4:
        return JSONResponse({"status": "error", "message": "Senha deve ter ao menos 4 caracteres"})
    usuarios = load_json(usuarios_path, {})
    if cpf not in usuarios:
        return JSONResponse({"status": "error", "message": "Usuário não encontrado"})
    salt = secrets.token_bytes(16)
    usuarios[cpf]["salt"] = salt.hex()
    usuarios[cpf]["hash"] = hashlib.pbkdf2_hmac("sha256", nova.encode("utf-8"), salt, 120_000).hex()
    usuarios[cpf]["senha_expirada"] = True
    usuarios[cpf]["ultima_troca_senha"] = datetime.now().strftime("%d/%m/%Y")
    save_json(usuarios_path, usuarios)
    return JSONResponse({"status": "ok"})


@app.get("/cadastro", response_class=HTMLResponse)
async def cadastro(request: Request):
    redirect = require_login(request)
    if redirect:
        return redirect
    db = load_json(db_path, {"cadastros": [], "organizacoes": []})
    acoes = load_json(acoes_path, [])
    vans = load_json(vans_path, [])
    return templates.TemplateResponse("cadastro.html", {
        "request": request,
        "acoes": acoes,
        "vans": vans,
    })


@app.get("/relatorios", response_class=HTMLResponse)
async def relatorios(request: Request):
    redirect = require_login(request)
    if redirect:
        return redirect
    return templates.TemplateResponse("relatorios.html", {"request": request})


@app.get("/entrega", response_class=HTMLResponse)
async def entrega(request: Request):
    redirect = require_login(request)
    if redirect:
        return redirect
    return templates.TemplateResponse("entrega.html", {"request": request})


@app.get("/acoes", response_class=HTMLResponse)
async def tela_acoes(request: Request):
    redirect = require_login(request)
    if redirect:
        return redirect
    acoes = load_json(acoes_path, [])
    return templates.TemplateResponse("acoes.html", {"request": request, "acoes": acoes})


@app.get("/servicos", response_class=HTMLResponse)
async def tela_servicos(request: Request):
    redirect = require_login(request)
    if redirect:
        return redirect
    servicos = load_json(servicos_path, [])
    return templates.TemplateResponse("servicos.html", {"request": request, "servicos": servicos})


@app.get("/vans", response_class=HTMLResponse)
async def tela_vans(request: Request):
    redirect = require_login(request)
    if redirect:
        return redirect
    vans = load_json(vans_path, [])
    return templates.TemplateResponse("vans.html", {"request": request, "vans": vans})


@app.get("/organizacoes", response_class=HTMLResponse)
async def tela_organizacoes(request: Request):
    redirect = require_login(request)
    if redirect:
        return redirect
    org = load_json(organizacoes_path, [])
    return templates.TemplateResponse("organizacoes.html", {"request": request, "organizacoes": org})


@app.get("/fichas", response_class=HTMLResponse)
async def tela_fichas(request: Request):
    redirect = require_login(request)
    if redirect:
        return redirect
    return templates.TemplateResponse("fichas.html", {"request": request})


@app.get("/backup", response_class=HTMLResponse)
async def tela_backup(request: Request):
    redirect = require_login(request)
    if redirect:
        return redirect
    return templates.TemplateResponse("backup.html", {"request": request})


@app.get("/api/cadastros")
async def listar_cadastros(request: Request):
    redirect = require_login(request)
    if redirect:
        return redirect
    db = load_json(db_path, {"cadastros": []})
    return db.get("cadastros", [])


@app.get("/api/cadastros/pesquisar")
async def pesquisar_cadastro(request: Request, protocolo: str = ""):
    redirect = require_login(request)
    if redirect:
        return redirect
    db = load_json(db_path, {"cadastros": []})
    cadastros = db.get("cadastros", [])
    if protocolo:
        cadastros = [c for c in cadastros if protocolo.lower() in str(c.get("protocolo", "")).lower()]
    return cadastros


@app.post("/api/cadastros")
async def salvar_cadastro(request: Request):
    redirect = require_login(request)
    if redirect:
        return redirect
    data = await request.json()
    db = load_json(db_path, {"cadastros": []})
    cadastros = db.get("cadastros", [])
    existing = next((c for c in cadastros if str(c.get("protocolo", "")).strip() == str(data.get("protocolo", "")).strip()), None)
    if existing:
        existing.update(data)
        save_json(db_path, db)
        return JSONResponse({"status": "updated", "id": existing.get("id")})
    data["id"] = str(len(cadastros) + 1)
    cadastros.append(data)
    db["cadastros"] = cadastros
    save_json(db_path, db)
    return JSONResponse({"status": "ok", "id": data["id"]})


@app.put("/api/cadastros/{item_id}")
async def atualizar_cadastro(item_id: str, request: Request):
    redirect = require_login(request)
    if redirect:
        return redirect
    data = await request.json()
    db = load_json(db_path, {"cadastros": []})
    cadastros = db.get("cadastros", [])
    for i, item in enumerate(cadastros):
        if str(item.get("id")) == str(item_id):
            cadastros[i] = data
            break
    db["cadastros"] = cadastros
    save_json(db_path, db)
    return JSONResponse({"status": "ok"})


@app.delete("/api/cadastros/{item_id}")
async def excluir_cadastro(item_id: str, request: Request):
    redirect = require_login(request)
    if redirect:
        return redirect
    db = load_json(db_path, {"cadastros": []})
    cadastros = db.get("cadastros", [])
    cadastros = [c for c in cadastros if str(c.get("id")) != str(item_id)]
    db["cadastros"] = cadastros
    save_json(db_path, db)
    return JSONResponse({"status": "ok"})


@app.get("/api/acoes")
async def listar_acoes(request: Request):
    redirect = require_login(request)
    if redirect:
        return redirect
    acoes = load_json(acoes_path, [])
    return acoes


@app.post("/api/acoes")
async def salvar_acao(request: Request):
    redirect = require_login(request)
    if redirect:
        return redirect
    data = await request.json()
    acoes = load_json(acoes_path, [])
    data["id"] = str(len(acoes) + 1)
    acoes.append(data)
    save_json(acoes_path, acoes)
    return JSONResponse({"status": "ok", "id": data["id"]})


@app.delete("/api/acoes/{acao_id}")
async def excluir_acao(acao_id: str, request: Request):
    redirect = require_login(request)
    if redirect:
        return redirect
    acoes = load_json(acoes_path, [])
    acoes = [a for a in acoes if str(a.get("id")) != str(acao_id)]
    save_json(acoes_path, acoes)
    return JSONResponse({"status": "ok"})


@app.get("/api/servicos")
async def listar_servicos(request: Request):
    redirect = require_login(request)
    if redirect:
        return redirect
    servicos = load_json(servicos_path, [])
    return servicos


@app.post("/api/servicos")
async def salvar_servico(request: Request):
    redirect = require_login(request)
    if redirect:
        return redirect
    data = await request.json()
    servicos = load_json(servicos_path, [])
    data["id"] = str(len(servicos) + 1)
    servicos.append(data)
    save_json(servicos_path, servicos)
    return JSONResponse({"status": "ok", "id": data["id"]})


@app.get("/api/vans")
async def listar_vans(request: Request):
    redirect = require_login(request)
    if redirect:
        return redirect
    vans = load_json(vans_path, [])
    return vans


@app.post("/api/vans")
async def salvar_van(request: Request):
    redirect = require_login(request)
    if redirect:
        return redirect
    data = await request.json()
    vans = load_json(vans_path, [])
    data["id"] = str(len(vans) + 1)
    vans.append(data)
    save_json(vans_path, vans)
    return JSONResponse({"status": "ok", "id": data["id"]})


@app.get("/api/organizacoes")
async def listar_organizacoes(request: Request):
    redirect = require_login(request)
    if redirect:
        return redirect
    org = load_json(organizacoes_path, [])
    return org


@app.post("/api/organizacoes")
async def salvar_organizacao(request: Request):
    redirect = require_login(request)
    if redirect:
        return redirect
    data = await request.json()
    org = load_json(organizacoes_path, [])
    data["id"] = str(len(org) + 1)
    org.append(data)
    save_json(organizacoes_path, org)
    return JSONResponse({"status": "ok", "id": data["id"]})


@app.get("/api/relatorios/cadastros-por-acao")
async def relatorio_cadastros_por_acao(request: Request):
    redirect = require_login(request)
    if redirect:
        return redirect
    db = load_json(db_path, {"cadastros": []})
    acoes = load_json(acoes_path, [])
    cadastros = db.get("cadastros", [])
    resultado = []
    for acao in acoes:
        acao_id = str(acao.get("id", "")).strip()
        total = sum(1 for c in cadastros if str(c.get("acao_id", "")).strip() == acao_id)
        resultado.append({
            "acao_id": acao_id,
            "acao_nome": acao.get("nome", acao.get("local", "")),
            "total": total
        })
    return resultado


@app.get("/api/relatorios/cadastros-por-periodo")
async def relatorio_cadastros_por_periodo(request: Request, de: str = "", ate: str = ""):
    redirect = require_login(request)
    if redirect:
        return redirect
    db = load_json(db_path, {"cadastros": []})
    cadastros = db.get("cadastros", [])
    if de and ate:
        filtrados = []
        for c in cadastros:
            data = str(c.get("data", ""))
            if de <= data <= ate:
                filtrados.append(c)
        return filtrados
    return cadastros


@app.get("/api/relatorios/estatisticas")
async def relatorio_estatisticas(request: Request):
    redirect = require_login(request)
    if redirect:
        return redirect
    db = load_json(db_path, {"cadastros": []})
    cadastros = db.get("cadastros", [])
    total = len(cadastros)
    acoes = load_json(acoes_path, [])
    vans = load_json(vans_path, [])
    return {
        "total_cadastros": total,
        "total_acoes": len(acoes),
        "total_vans": len(vans),
    }


@app.post("/api/acoes/{acao_id}/finalizar")
async def finalizar_acao(acao_id: str, request: Request):
    redirect = require_login(request)
    if redirect:
        return redirect
    acoes = load_json(acoes_path, [])
    for i, acao in enumerate(acoes):
        if str(acao.get("id")) == str(acao_id):
            acao["finalizada"] = True
            acoes[i] = acao
            break
    save_json(acoes_path, acoes)
    return JSONResponse({"status": "ok"})


@app.get("/api/acao-ativa")
async def acao_ativa(request: Request):
    redirect = require_login(request)
    if redirect:
        return redirect
    acoes = load_json(acoes_path, [])
    for acao in acoes:
        if not acao.get("finalizada"):
            return acao
    return {}


@app.get("/api/entregas")
async def listar_entregas(request: Request):
    redirect = require_login(request)
    if redirect:
        return redirect
    entregas_path = os.path.join(PARENT_DIR, "entregas_confirmadas.json")
    entregas = load_json(entregas_path, [])
    return entregas


@app.post("/api/entregas")
async def salvar_entrega(request: Request):
    redirect = require_login(request)
    if redirect:
        return redirect
    data = await request.json()
    entregas_path = os.path.join(PARENT_DIR, "entregas_confirmadas.json")
    entregas = load_json(entregas_path, [])
    data["id"] = str(len(entregas) + 1)
    entregas.append(data)
    save_json(entregas_path, entregas)
    return JSONResponse({"status": "ok", "id": data["id"]})


@app.get("/api/backup")
async def fazer_backup(request: Request):
    redirect = require_login(request)
    if redirect:
        return redirect
    import shutil
    from datetime import datetime
    backup_dir = os.path.join(PARENT_DIR, "backup_sistema_emprel")
    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    backup_file = os.path.join(backup_dir, f"backup_{timestamp}.json")
    db = load_json(db_path, {})
    save_json(backup_file, db)
    return JSONResponse({"status": "ok", "file": backup_file})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)