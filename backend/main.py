import os
import uuid
from typing import List, Optional
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

# 1. Carrega variáveis de ambiente
ROOT_DIR = Path(__file__).resolve().parent.parent
env_path = ROOT_DIR / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

from fastapi import FastAPI, Depends, HTTPException, File, UploadFile, Request, Body, status
from fastapi.responses import FileResponse, Response

from fastapi.security import OAuth2PasswordRequestForm
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session, joinedload

# Importações internas do backend
from backend.routers import empresas, usuarios
from backend.models import LogAcao, Usuario, Chamado, Anexo, Interacao
from backend.database import get_db, SessionLocal, engine, Base
from backend.auth import (
    RoleChecker,
    get_current_user,
    criar_token_acesso,
    criar_token_recuperacao,
    verificar_token_recuperacao,
    calcular_fingerprint_senha,
    validar_fingerprint_senha,
    autenticar_usuario,
    gerar_hash_senha,
    validar_complexidade_senha,
    enviar_email_recuperacao,
    admin_only,
    tecnico_ou_admin,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

import backend.models as models
import backend.cruds as cruds
from backend.schemas import *

# Configuração de uploads seguros
UPLOAD_DIRECTORY = os.path.abspath(os.path.join(str(ROOT_DIR), "uploads"))
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".gif", ".txt", ".csv", ".docx", ".xlsx", ".zip"}
MAX_FILE_SIZE_BYTES = 15 * 1024 * 1024  # 15 MB

# CORS Config
raw_frontend_url = os.getenv("FRONTEND_URL", "").strip()
allowed_origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000"
]
if raw_frontend_url:
    for u in raw_frontend_url.split(","):
        cleaned = u.strip().rstrip("/")
        if cleaned and cleaned not in allowed_origins:
            allowed_origins.append(cleaned)

app = FastAPI(title="Delphi System API", version="1.0.0")

# Middleware de Segurança para Headers HTTP
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response

app.add_middleware(SecurityHeadersMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas Modulares
app.include_router(empresas.router)
app.include_router(usuarios.router)


# ---------------------- HEALTH CHECK ----------------------
@app.get("/health")
def health_check():
    return {"status": "ok"}


# ---------------------- LOGIN ----------------------
@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    usuario = autenticar_usuario(db, form_data.username, form_data.password)
    if not usuario:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário ou senha inválidos")

    role_final = usuario.role.nome if usuario.role and usuario.role.nome else "comum"

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = criar_token_acesso(
        data={
            "sub": usuario.email,
            "nome": usuario.nome,
            "role": role_final,
            "id": usuario.id
        },
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "usuario": {
            "id": usuario.id,
            "nome": usuario.nome,
            "email": usuario.email,
            "role": role_final
        }
    }


# ---------------------- MAQUINAS ----------------------
@app.get("/maquinas/", response_model=List[MaquinaOut])
def listar_maquinas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), usuario: models.Usuario = Depends(get_current_user)):
    return cruds.listar_maquinas(db, skip=skip, limit=limit)

@app.get("/maquinas/{maquina_id}", response_model=MaquinaOut)
def buscar_maquina(maquina_id: int, db: Session = Depends(get_db), usuario: models.Usuario = Depends(get_current_user)):
    maquina = cruds.buscar_maquina_por_id(db, maquina_id)
    if not maquina:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Máquina não encontrada")
    return maquina

@app.post("/maquinas/", response_model=MaquinaOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(admin_only)])
def criar_maquina(maquina: MaquinaCreate, db: Session = Depends(get_db)):
    return cruds.criar_maquina(db, maquina)

@app.put("/maquinas/{maquina_id}", response_model=MaquinaOut, dependencies=[Depends(admin_only)])
def atualizar_maquina(maquina_id: int, dados: MaquinaUpdate, db: Session = Depends(get_db)):
    maquina = cruds.atualizar_maquina(db, maquina_id, dados)
    if not maquina:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Máquina não encontrada")
    return maquina

@app.delete("/maquinas/{maquina_id}", dependencies=[Depends(admin_only)])
def deletar_maquina(maquina_id: int, db: Session = Depends(get_db)):
    sucesso = cruds.deletar_maquina(db, maquina_id)
    if not sucesso:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Máquina não encontrada")
    return {"detail": "Máquina removida"}


# ---------------------- ORIGENS DO PROBLEMA ----------------------
@app.get("/origens_problema/", response_model=List[OrigemProblemaOut])
def listar_origens_problema(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), usuario: models.Usuario = Depends(get_current_user)):
    return cruds.listar_origens_problema(db, skip=skip, limit=limit)

@app.get("/origens_problema/{origem_id}", response_model=OrigemProblemaOut)
def buscar_origem_problema(origem_id: int, db: Session = Depends(get_db), usuario: models.Usuario = Depends(get_current_user)):
    origem = cruds.buscar_origem_problema_por_id(db, origem_id)
    if not origem:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Origem não encontrada")
    return origem

@app.post("/origens_problema/", response_model=OrigemProblemaOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(admin_only)])
def criar_origem_problema(origem: OrigemProblemaCreate, db: Session = Depends(get_db)):
    return cruds.criar_origem_problema(db, origem)

@app.put("/origens_problema/{origem_id}", response_model=OrigemProblemaOut, dependencies=[Depends(admin_only)])
def atualizar_origem_problema(origem_id: int, dados: OrigemProblemaUpdate, db: Session = Depends(get_db)):
    origem = cruds.atualizar_origem_problema(db, origem_id, dados)
    if not origem:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Origem não encontrada")
    return origem

@app.delete("/origens_problema/{origem_id}", dependencies=[Depends(admin_only)])
def deletar_origem_problema(origem_id: int, db: Session = Depends(get_db)):
    sucesso = cruds.deletar_origem_problema(db, origem_id)
    if not sucesso:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Origem não encontrada")
    return {"detail": "Origem removida"}


# ---------------------- PRIORIDADES ----------------------
@app.get("/prioridades/", response_model=List[PrioridadeOut])
def listar_prioridades(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), usuario: models.Usuario = Depends(get_current_user)):
    return cruds.listar_prioridades(db, skip=skip, limit=limit)

@app.get("/prioridades/{prioridade_id}", response_model=PrioridadeOut)
def buscar_prioridade(prioridade_id: int, db: Session = Depends(get_db), usuario: models.Usuario = Depends(get_current_user)):
    prioridade = cruds.buscar_prioridade_por_id(db, prioridade_id)
    if not prioridade:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prioridade não encontrada")
    return prioridade

@app.post("/prioridades/", response_model=PrioridadeOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(admin_only)])
def criar_prioridade(prioridade: PrioridadeCreate, db: Session = Depends(get_db)):
    return cruds.criar_prioridade(db, prioridade)

@app.put("/prioridades/{prioridade_id}", response_model=PrioridadeOut, dependencies=[Depends(admin_only)])
def atualizar_prioridade(prioridade_id: int, dados: PrioridadeUpdate, db: Session = Depends(get_db)):
    prioridade = cruds.atualizar_prioridade(db, prioridade_id, dados)
    if not prioridade:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prioridade não encontrada")
    return prioridade

@app.delete("/prioridades/{prioridade_id}", dependencies=[Depends(admin_only)])
def deletar_prioridade(prioridade_id: int, db: Session = Depends(get_db)):
    sucesso = cruds.deletar_prioridade(db, prioridade_id)
    if not sucesso:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prioridade não encontrada")
    return {"detail": "Prioridade removida"}


# ---------------------- STATUS ----------------------
@app.get("/status_chamado/", response_model=List[StatusOut])
def listar_status(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), usuario: models.Usuario = Depends(get_current_user)):
    return cruds.listar_status(db, skip=skip, limit=limit)

@app.get("/status_chamado/{status_id}", response_model=StatusOut)
def buscar_status(status_id: int, db: Session = Depends(get_db), usuario: models.Usuario = Depends(get_current_user)):
    status_obj = cruds.buscar_status_por_id(db, status_id)
    if not status_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Status não encontrado")
    return status_obj

@app.post("/status_chamado/", response_model=StatusOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(admin_only)])
def criar_status(status_data: StatusCreate, db: Session = Depends(get_db)):
    return cruds.criar_status(db, status_data)

@app.put("/status_chamado/{status_id}", response_model=StatusOut, dependencies=[Depends(admin_only)])
def atualizar_status(status_id: int, dados: StatusUpdate, db: Session = Depends(get_db)):
    status_obj = cruds.atualizar_status(db, status_id, dados)
    if not status_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Status não encontrado")
    return status_obj

@app.delete("/status_chamado/{status_id}", dependencies=[Depends(admin_only)])
def deletar_status(status_id: int, db: Session = Depends(get_db)):
    sucesso = cruds.deletar_status(db, status_id)
    if not sucesso:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Status não encontrado")
    return {"detail": "Status removido"}


# ---------------------- FREQUÊNCIAS ----------------------
@app.get("/frequencias/", response_model=List[FrequenciaOut])
def listar_frequencias(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), usuario: models.Usuario = Depends(get_current_user)):
    return cruds.listar_frequencias(db, skip=skip, limit=limit)

@app.get("/frequencias/{frequencia_id}", response_model=FrequenciaOut)
def obter_frequencia(frequencia_id: int, db: Session = Depends(get_db), usuario: models.Usuario = Depends(get_current_user)):
    frequencia = cruds.obter_frequencia(db, frequencia_id)
    if not frequencia:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Frequência não encontrada")
    return frequencia

@app.post("/frequencias/", response_model=FrequenciaOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(admin_only)])
def criar_frequencia(frequencia: FrequenciaCreate, db: Session = Depends(get_db)):
    return cruds.criar_frequencia(db, frequencia)

@app.put("/frequencias/{frequencia_id}", response_model=FrequenciaOut, dependencies=[Depends(admin_only)])
def atualizar_frequencia(frequencia_id: int, dados: FrequenciaUpdate, db: Session = Depends(get_db)):
    frequencia = cruds.atualizar_frequencia(db, frequencia_id, dados)
    if not frequencia:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Frequência não encontrada")
    return frequencia

@app.delete("/frequencias/{frequencia_id}", dependencies=[Depends(admin_only)])
def deletar_frequencia(frequencia_id: int, db: Session = Depends(get_db)):
    sucesso = cruds.deletar_frequencia(db, frequencia_id)
    if not sucesso:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Frequência não encontrada")
    return {"detail": "Frequência removida"}


# ---------------------- CHAMADOS ----------------------
@app.get("/chamados/", response_model=List[ChamadoOut])
def listar_chamados(
    status_id: Optional[int] = None,
    empresa_id: Optional[int] = None,
    prioridade_id: Optional[int] = None,
    contato: Optional[str] = None,
    responsavel_id: Optional[int] = None,
    order_by: str = "datetime_abertura",
    desc: bool = False,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(get_current_user)
):
    chamados = cruds.listar_chamados(
        db,
        status_id=status_id,
        empresa_id=empresa_id,
        prioridade_id=prioridade_id,
        contato=contato,
        responsavel_id=responsavel_id,
        order_by=order_by,
        desc=desc,
        skip=skip,
        limit=limit,
        usuario=usuario
    )
    for ch in chamados:
        for anexo in ch.anexos:
            anexo.url = f"/anexos/{anexo.id}"
    return chamados

@app.get("/chamados/{chamado_id}", response_model=ChamadoOut)
def obter_chamado(chamado_id: int, db: Session = Depends(get_db), usuario: models.Usuario = Depends(get_current_user)):
    is_staff = bool(usuario.role and usuario.role.nome in ["admin", "tecnico"])
    chamado = cruds.obter_chamado(db, chamado_id, is_staff=is_staff)
    if not chamado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chamado não encontrado")
    if not cruds.verificar_acesso_chamado(chamado, usuario):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado a este chamado.")
    for anexo in chamado.anexos:
        anexo.url = f"/anexos/{anexo.id}"
    return chamado

@app.get("/chamados/{chamado_id}/timeline", response_model=List[LogAcaoOut])
def timeline_chamado(chamado_id: int, db: Session = Depends(get_db), usuario: models.Usuario = Depends(get_current_user)):
    chamado = cruds.obter_chamado(db, chamado_id)
    if not chamado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chamado não encontrado")
    if not cruds.verificar_acesso_chamado(chamado, usuario):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado a este chamado.")

    logs = (
        db.query(LogAcao)
        .filter_by(chamado_id=chamado_id, ativo=True)
        .options(joinedload(LogAcao.usuario))
        .order_by(LogAcao.data_hora.asc())
        .all()
    )
    return logs

@app.post("/chamados/", response_model=ChamadoOut, status_code=status.HTTP_201_CREATED)
def criar_chamado(chamado: ChamadoCreate, db: Session = Depends(get_db), usuario: models.Usuario = Depends(get_current_user)):
    novo_chamado = cruds.criar_chamado(db, chamado, usuario.id)
    chamado_completo = cruds.obter_chamado(db, novo_chamado.id)
    return chamado_completo

@app.put("/chamados/{chamado_id}", response_model=ChamadoOut)
def atualizar_chamado(chamado_id: int, dados: ChamadoUpdate, db: Session = Depends(get_db), usuario: models.Usuario = Depends(get_current_user)):
    chamado_existente = cruds.obter_chamado(db, chamado_id)
    if not chamado_existente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chamado não encontrado")
    if not cruds.verificar_acesso_chamado(chamado_existente, usuario):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado a este chamado.")

    chamado = cruds.atualizar_chamado(db, chamado_id, dados, usuario_id=usuario.id)
    is_staff = bool(usuario.role and usuario.role.nome in ["admin", "tecnico"])
    chamado_completo = cruds.obter_chamado(db, chamado_id, is_staff=is_staff)
    for anexo in (chamado_completo.anexos if chamado_completo else []):
        anexo.url = f"/anexos/{anexo.id}"
    return chamado_completo

@app.delete("/chamados/{chamado_id}", dependencies=[Depends(admin_only)])
def deletar_chamado(chamado_id: int, db: Session = Depends(get_db), usuario: models.Usuario = Depends(get_current_user)):
    sucesso = cruds.deletar_chamado(db, chamado_id, usuario.id)
    if not sucesso:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chamado não encontrado")
    return {"detail": "Chamado removido"}



# ---------------------- TAGS ----------------------
@app.get("/tags/", response_model=List[TagOut])
def listar_tags_endpoint(db: Session = Depends(get_db), usuario: models.Usuario = Depends(get_current_user)):
    return cruds.listar_tags(db)

@app.get("/tags/{tag_id}", response_model=TagOut)
def buscar_tag_endpoint(tag_id: int, db: Session = Depends(get_db), usuario: models.Usuario = Depends(get_current_user)):
    db_tag = cruds.buscar_tag_por_id(db, tag_id)
    if not db_tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag não encontrada")
    return db_tag

@app.post("/tags/", response_model=TagOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(tecnico_ou_admin)])
def criar_tag_endpoint(tag: TagCreate, db: Session = Depends(get_db)):
    db_tag = cruds.buscar_tag_por_nome(db, tag.nome)
    if db_tag:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uma tag com este nome já existe.")
    return cruds.criar_tag(db, tag)

@app.delete("/tags/{tag_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(admin_only)])
def deletar_tag_endpoint(tag_id: int, db: Session = Depends(get_db)):
    sucesso = cruds.deletar_tag(db, tag_id)
    if not sucesso:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag não encontrada")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.post("/chamados/{chamado_id}/tags/{tag_id}", response_model=ChamadoOut, dependencies=[Depends(tecnico_ou_admin)])
def associar_tag_a_chamado(chamado_id: int, tag_id: int, db: Session = Depends(get_db)):
    chamado = cruds.adicionar_tag_a_chamado(db, chamado_id=chamado_id, tag_id=tag_id)
    if not chamado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chamado ou Tag não encontrado(a)")
    chamado_completo = cruds.obter_chamado(db, chamado_id)
    return chamado_completo

@app.delete("/chamados/{chamado_id}/tags/{tag_id}", response_model=ChamadoOut, dependencies=[Depends(tecnico_ou_admin)])
def remover_tag_de_chamado(chamado_id: int, tag_id: int, db: Session = Depends(get_db)):
    chamado = cruds.remover_tag_de_chamado(db, chamado_id=chamado_id, tag_id=tag_id)
    if not chamado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chamado ou Tag não encontrado(a)")
    chamado_completo = cruds.obter_chamado(db, chamado_id)
    return chamado_completo


# ---------------------- INTERACOES (COMENTÁRIOS) ----------------------
@app.get("/chamados/{chamado_id}/interacoes/", response_model=List[InteracaoOut])
def listar_interacoes_endpoint(chamado_id: int, db: Session = Depends(get_db), usuario: models.Usuario = Depends(get_current_user)):
    chamado = cruds.obter_chamado(db, chamado_id)
    if not chamado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chamado não encontrado")
    if not cruds.verificar_acesso_chamado(chamado, usuario):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado a este chamado.")

    is_staff = bool(usuario.role and usuario.role.nome in ["admin", "tecnico"])
    return cruds.listar_interacoes_por_chamado(db, chamado_id=chamado_id, is_staff=is_staff)

@app.post("/chamados/{chamado_id}/interacoes/", response_model=InteracaoOut, status_code=status.HTTP_201_CREATED)
def criar_interacao_endpoint(
    chamado_id: int,
    interacao: InteracaoCreate,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(get_current_user)
):
    chamado = cruds.obter_chamado(db, chamado_id)
    if not chamado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chamado não encontrado")
    if not cruds.verificar_acesso_chamado(chamado, usuario):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado a este chamado.")

    # Se usuário for comum, não pode criar comentário privado
    is_staff = bool(usuario.role and usuario.role.nome in ["admin", "tecnico"])
    if interacao.privado and not is_staff:
        interacao.privado = False

    return cruds.criar_interacao(db, interacao=interacao, chamado_id=chamado_id, usuario_id=usuario.id)

@app.put("/interacoes/{interacao_id}", response_model=InteracaoOut)
def atualizar_interacao_endpoint(
    interacao_id: int,
    dados: InteracaoUpdate,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(get_current_user)
):
    db_interacao = cruds.buscar_interacao_por_id(db, interacao_id)
    if not db_interacao:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interação não encontrada")

    chamado = cruds.obter_chamado(db, db_interacao.chamado_id)
    if not cruds.verificar_acesso_chamado(chamado, usuario):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado a este comentário.")

    is_admin = bool(usuario.role and usuario.role.nome == "admin")
    if db_interacao.usuario_id != usuario.id and not is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Você não tem permissão para editar este comentário")

    return cruds.atualizar_interacao(db, interacao_id=interacao_id, dados=dados)

@app.delete("/interacoes/{interacao_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_interacao_endpoint(
    interacao_id: int,
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(get_current_user)
):
    db_interacao = cruds.buscar_interacao_por_id(db, interacao_id)
    if not db_interacao:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interação não encontrada")

    chamado = cruds.obter_chamado(db, db_interacao.chamado_id)
    if not cruds.verificar_acesso_chamado(chamado, usuario):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado a este comentário.")

    is_admin = bool(usuario.role and usuario.role.nome == "admin")
    if db_interacao.usuario_id != usuario.id and not is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Você não tem permissão para deletar este comentário")

    cruds.deletar_interacao(db, interacao_id=interacao_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ---------------------- ANEXOS SEGUROS E VALIDADOS ----------------------
def validar_assinatura_arquivo(file_ext: str, header: bytes) -> bool:
    """Valida a assinatura (magic bytes) correspondente à extensão do arquivo."""
    ext = file_ext.lower()
    if ext == ".png":
        return header.startswith(b"\x89PNG\r\n\x1a\n")
    elif ext in [".jpg", ".jpeg"]:
        return header.startswith(b"\xff\xd8\xff")
    elif ext == ".pdf":
        return header.startswith(b"%PDF-")
    elif ext in [".txt", ".csv"]:
        if b"\x00" in header:
            return False
        try:
            header.decode("utf-8")
            return True
        except UnicodeDecodeError:
            try:
                header.decode("latin-1")
                return True
            except UnicodeDecodeError:
                return False
    return False

@app.post("/chamados/{chamado_id}/anexos/", response_model=AnexoOut, status_code=status.HTTP_201_CREATED)
async def upload_anexo_endpoint(
    chamado_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    usuario: models.Usuario = Depends(get_current_user)
):
    chamado = cruds.obter_chamado(db, chamado_id)
    if not chamado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chamado não encontrado")
    if not cruds.verificar_acesso_chamado(chamado, usuario):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado a este chamado.")

    original_filename = Path(file.filename or "arquivo").name
    file_ext = os.path.splitext(original_filename)[1].lower()

    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Extensão de arquivo não permitida. Permitidas: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    # Confinamento robusto no diretório de uploads usando Path.resolve().relative_to
    upload_dir = Path(UPLOAD_DIRECTORY).resolve()
    upload_dir.mkdir(parents=True, exist_ok=True)
    safe_filename = f"{uuid.uuid4().hex}{file_ext}"
    dest_path = (upload_dir / safe_filename).resolve()

    try:
        dest_path.relative_to(upload_dir)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tentativa de evasão de diretório detectada.")

    # Leitura inicial para validação de assinatura / magic bytes
    primeiro_chunk = await file.read(512)
    if not primeiro_chunk:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Arquivo vazio não permitido.")

    if not validar_assinatura_arquivo(file_ext, primeiro_chunk):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Conteúdo/assinatura do arquivo incompatível com a extensão {file_ext} declarada."
        )

    # Gravação do arquivo com verificação de tamanho
    total_size = len(primeiro_chunk)
    try:
        with open(dest_path, "wb") as buffer:
            buffer.write(primeiro_chunk)
            while chunk := await file.read(1024 * 1024):  # 1MB chunks
                total_size += len(chunk)
                if total_size > MAX_FILE_SIZE_BYTES:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Arquivo excede o tamanho máximo permitido de 15MB."
                    )
                buffer.write(chunk)
    except Exception as e:
        if dest_path.exists():
            dest_path.unlink()
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno ao processar o arquivo.")

    anexo_info = {
        "nome_arquivo_original": original_filename,
        "path_arquivo_armazenado": str(dest_path),
        "content_type": file.content_type or "application/octet-stream",
        "tamanho_bytes": total_size
    }

    # Persistência com rollback do arquivo físico se falhar
    try:
        db_anexo = cruds.criar_anexo(db, anexo_info=anexo_info, chamado_id=chamado_id, usuario_id=usuario.id)
    except Exception:
        if dest_path.exists():
            dest_path.unlink()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno ao persistir anexo.")

    db_anexo.url = f"/anexos/{db_anexo.id}"
    return db_anexo


@app.get("/chamados/{chamado_id}/anexos/", response_model=List[AnexoOut])
def listar_anexos_endpoint(chamado_id: int, db: Session = Depends(get_db), usuario: models.Usuario = Depends(get_current_user)):
    chamado = cruds.obter_chamado(db, chamado_id)
    if not chamado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chamado não encontrado")
    if not cruds.verificar_acesso_chamado(chamado, usuario):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado a este chamado.")

    anexos = cruds.listar_anexos_por_chamado(db, chamado_id=chamado_id)
    for anexo in anexos:
        anexo.url = f"/anexos/{anexo.id}"
    return anexos


@app.get("/anexos/{anexo_id}")
def baixar_anexo_endpoint(anexo_id: int, db: Session = Depends(get_db), usuario: models.Usuario = Depends(get_current_user)):
    db_anexo = cruds.buscar_anexo_por_id(db, anexo_id)
    if not db_anexo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anexo não encontrado")

    chamado = cruds.obter_chamado(db, db_anexo.chamado_id)
    if not cruds.verificar_acesso_chamado(chamado, usuario):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado a este anexo.")

    # Confinamento seguro do caminho no download
    upload_dir = Path(UPLOAD_DIRECTORY).resolve()
    file_path = Path(db_anexo.path_arquivo_armazenado).resolve()
    try:
        file_path.relative_to(upload_dir)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Arquivo não encontrado.")

    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Arquivo físico não encontrado no servidor")

    return FileResponse(
        path=str(file_path),
        filename=db_anexo.nome_arquivo_original,
        media_type=db_anexo.content_type
    )


@app.delete("/anexos/{anexo_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_anexo_endpoint(anexo_id: int, db: Session = Depends(get_db), usuario: models.Usuario = Depends(get_current_user)):
    db_anexo = cruds.buscar_anexo_por_id(db, anexo_id)
    if not db_anexo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anexo não encontrado")

    chamado = cruds.obter_chamado(db, db_anexo.chamado_id)
    if not cruds.verificar_acesso_chamado(chamado, usuario):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado a este anexo.")

    is_admin = bool(usuario.role and usuario.role.nome == "admin")
    if db_anexo.usuario_id != usuario.id and not is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Você não tem permissão para deletar este anexo")

    cruds.deletar_anexo(db, anexo_id=anexo_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# ---------------------- CHAMADOS RECORRENTES ----------------------
@app.get("/chamados_recorrentes/", response_model=List[ChamadoRecorrenteOut])
def listar_chamados_recorrentes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), usuario: models.Usuario = Depends(get_current_user)):
    return cruds.listar_chamados_recorrentes(db, skip=skip, limit=limit)

@app.get("/chamados_recorrentes/{chamado_id}", response_model=ChamadoRecorrenteOut)
def obter_chamado_recorrente(chamado_id: int, db: Session = Depends(get_db), usuario: models.Usuario = Depends(get_current_user)):
    chamado = cruds.obter_chamado_recorrente(db, chamado_id)
    if not chamado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chamado recorrente não encontrado")
    return chamado

@app.post("/chamados_recorrentes/", response_model=ChamadoRecorrenteOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(admin_only)])
def criar_chamado_recorrente(chamado: ChamadoRecorrenteCreate, db: Session = Depends(get_db)):
    return cruds.criar_chamado_recorrente(db, chamado)

@app.put("/chamados_recorrentes/{chamado_id}", response_model=ChamadoRecorrenteOut, dependencies=[Depends(admin_only)])
def atualizar_chamado_recorrente(chamado_id: int, dados: ChamadoRecorrenteUpdate, db: Session = Depends(get_db)):
    chamado = cruds.atualizar_chamado_recorrente(db, chamado_id, dados)
    if not chamado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chamado recorrente não encontrado")
    return chamado

@app.delete("/chamados_recorrentes/{chamado_id}", dependencies=[Depends(admin_only)])
def deletar_chamado_recorrente(chamado_id: int, db: Session = Depends(get_db)):
    chamado = cruds.deletar_chamado_recorrente(db, chamado_id)
    if not chamado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chamado recorrente não encontrado")
    return {"detail": "Chamado recorrente removido"}


# ---------------------- ROLES ----------------------
@app.get("/roles/", response_model=List[RoleOut])
def listar_roles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), usuario: models.Usuario = Depends(get_current_user)):
    return cruds.listar_roles(db, skip=skip, limit=limit)

@app.get("/roles/{role_id}", response_model=RoleOut)
def buscar_role(role_id: int, db: Session = Depends(get_db), usuario: models.Usuario = Depends(get_current_user)):
    role = cruds.buscar_role_por_id(db, role_id)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cargo não encontrado")
    return role

@app.post("/roles/", response_model=RoleOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(admin_only)])
def criar_role(role: RoleCreate, db: Session = Depends(get_db)):
    return cruds.criar_role(db, role)

@app.put("/roles/{role_id}", response_model=RoleOut, dependencies=[Depends(admin_only)])
def atualizar_role(role_id: int, dados: RoleUpdate, db: Session = Depends(get_db)):
    role = cruds.atualizar_role(db, role_id, dados)
    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cargo não encontrado")
    return role

@app.delete("/roles/{role_id}", dependencies=[Depends(admin_only)])
def deletar_role(role_id: int, db: Session = Depends(get_db)):
    sucesso = cruds.deletar_role(db, role_id)
    if not sucesso:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cargo não encontrado")
    return {"detail": "Cargo removido"}


# ---------------------- LOGS DE AÇÕES ----------------------
@app.get("/logs/", response_model=List[LogAcaoOut], dependencies=[Depends(admin_only)])
def listar_logs(db: Session = Depends(get_db)):
    return cruds.listar_logs(db)

@app.get("/logs/{log_id}", response_model=LogAcaoOut, dependencies=[Depends(admin_only)])
def buscar_log(log_id: int, db: Session = Depends(get_db)):
    log = cruds.buscar_log_por_id(db, log_id)
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log não encontrado")
    return log


# ---------------------- DASHBOARD ----------------------
@app.get("/dashboard/basico")
def dashboard_basico(db: Session = Depends(get_db), usuario: models.Usuario = Depends(get_current_user)):
    return cruds.contar_chamados_por_status(db)

@app.get("/dashboard/avancado")
def dashboard_avancado(db: Session = Depends(get_db), usuario: models.Usuario = Depends(get_current_user)):
    return {
        "por_empresa": [
            {"empresa": nome, "quantidade": qtd} for nome, qtd in cruds.chamados_por_empresa(db)
        ],
        "por_tecnico": [
            {"tecnico": nome, "quantidade": qtd} for nome, qtd in cruds.chamados_por_tecnico(db)
        ],
        "ultimos_7_dias": [
            {"data": str(data), "quantidade": qtd} for data, qtd in cruds.chamados_ultimos_7_dias(db)
        ],
    }


# ---------------------- RECUPERAR SENHA (SEM ENUMERAÇÃO) ----------------------
@app.post("/recuperar-senha")
def recuperar_senha(email: str = Body(..., embed=True), db: Session = Depends(get_db)):
    """
    Solicita recuperação de senha. Retorna resposta indistinguível
    independentemente de o email existir para evitar enumeração de contas.
    """
    usuario = db.query(Usuario).filter(Usuario.email == email, Usuario.ativo == True).first()
    if usuario:
        pwh_fingerprint = calcular_fingerprint_senha(usuario.senha_hash)
        token = criar_token_recuperacao(
            data={"sub": usuario.email},
            expires_delta=timedelta(minutes=30),
            pwh_fingerprint=pwh_fingerprint
        )
        base_front = raw_frontend_url or "http://localhost:5173"
        link = f"{base_front.rstrip('/')}/resetar-senha?token={token}"
        try:
            enviar_email_recuperacao(usuario.email, link)
        except Exception as e:
            # Em caso de falha de envio de email, loga localmente sem quebrar o fluxo com erro exposto
            print(f"[AVISO] Falha ao enviar email de recuperação: {e}")

    return {"mensagem": "Se o e-mail estiver cadastrado, as instruções para redefinição foram enviadas."}


# ---------------------- RESETAR SENHA SEGURO (USO ÚNICO) ----------------------
@app.post("/resetar-senha")
def resetar_senha(token: str = Body(..., embed=True), nova_senha: str = Body(..., embed=True), db: Session = Depends(get_db)):
    """
    Redefine a senha do usuário utilizando o token com claim semântica 'password_reset'
    e invalidação por fingerprint criptográfico opaco de senha.
    """
    dados = verificar_token_recuperacao(token)
    email = dados.get("sub")
    token_pwh = dados.get("pwh")

    usuario = db.query(Usuario).filter(Usuario.email == email, Usuario.ativo == True).first()
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado ou inativo.")

    if not token_pwh or not validar_fingerprint_senha(token_pwh, usuario.senha_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Este token de recuperação já foi utilizado ou é inválido.")

    valida, motivo = validar_complexidade_senha(nova_senha)
    if not valida:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=motivo)

    usuario.senha_hash = gerar_hash_senha(nova_senha)
    db.commit()
    return {"mensagem": "Senha redefinida com sucesso."}
