from fastapi import FastAPI, Depends, HTTPException
from fastapi import Body
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.models import LogAcao, Usuario
from backend.database import SessionLocal, engine, Base
from backend.auth import get_current_user,criar_token_acesso, verificar_token, enviar_email_recuperacao
import backend.cruds as cruds
from backend.schemas import *
from backend.utils import hash_senha
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://suporte-power-dev.netlify.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------- LOGIN ----------------------
from fastapi.security import OAuth2PasswordRequestForm
from backend.auth import autenticar_usuario, criar_token_acesso, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import timedelta

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    usuario = autenticar_usuario(db, form_data.username, form_data.password)
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuário ou senha inválidos")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = criar_token_acesso(
        data={"sub": usuario.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# ---------------------- EMPRESAS ----------------------
@app.get("/empresas/", response_model=List[EmpresaOut])
def listar_empresas(db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
    return cruds.listar_empresas(db)

@app.get("/empresas/{empresa_id}", response_model=EmpresaOut)
def obter_empresa(empresa_id: int, db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
    empresa = cruds.obter_empresa(db, empresa_id)
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    return empresa

@app.post("/empresas/", response_model=EmpresaOut)
def criar_empresa(empresa: EmpresaCreate, db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
    return cruds.criar_empresa(db, empresa)

@app.put("/empresas/{empresa_id}", response_model=EmpresaOut)
def atualizar_empresa(empresa_id: int, dados: EmpresaUpdate, db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
    empresa = cruds.atualizar_empresa(db, empresa_id, dados)
    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    return empresa

@app.delete("/empresas/{empresa_id}")
def deletar_empresa(empresa_id: int, db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
    resultado = cruds.deletar_empresa(db, empresa_id)
    if not resultado:
        raise HTTPException(status_code=404, detail="Empresa não encontrada")
    return {"detail": "Empresa removida"}

# ---------------------- MAQUINAS ----------------------
@app.get("/maquinas/", response_model=List[MaquinaOut])
def listar_maquinas(db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
    return cruds.listar_maquinas(db)

@app.get("/maquinas/{maquina_id}", response_model=MaquinaOut)
def buscar_maquina(maquina_id: int, db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
    maquina = cruds.buscar_maquina_por_id(db, maquina_id)
    if not maquina:
        raise HTTPException(status_code=404, detail="Máquina não encontrada")
    return maquina

@app.post("/maquinas/", response_model=MaquinaOut)
def criar_maquina(maquina: MaquinaCreate, db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
    return cruds.criar_maquina(db, maquina)

@app.put("/maquinas/{maquina_id}", response_model=MaquinaOut)
def atualizar_maquina(maquina_id: int, dados: MaquinaUpdate, db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
    maquina = cruds.atualizar_maquina(db, maquina_id, dados)
    if not maquina:
        raise HTTPException(status_code=404, detail="Máquina não encontrada")
    return maquina

@app.delete("/maquinas/{maquina_id}")
def deletar_maquina(maquina_id: int, db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
    sucesso = cruds.deletar_maquina(db, maquina_id)
    if not sucesso:
        raise HTTPException(status_code=404, detail="Máquina não encontrada")
    return {"detail": "Máquina removida"}

# ---------------------- ORIGENS DO PROBLEMA ----------------------
@app.get("/origens_problema/", response_model=List[OrigemProblemaOut])
def listar_origens_problema(db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
    return cruds.listar_origens_problema(db)

@app.get("/origens_problema/{origem_id}", response_model=OrigemProblemaOut)
def buscar_origem_problema(origem_id: int, db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
    origem = cruds.buscar_origem_problema_por_id(db, origem_id)
    if not origem:
        raise HTTPException(status_code=404, detail="Origem não encontrada")
    return origem

@app.post("/origens_problema/", response_model=OrigemProblemaOut)
def criar_origem_problema(origem: OrigemProblemaCreate, db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
    return cruds.criar_origem_problema(db, origem)

@app.put("/origens_problema/{origem_id}", response_model=OrigemProblemaOut)
def atualizar_origem_problema(origem_id: int, dados: OrigemProblemaUpdate, db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
    origem = cruds.atualizar_origem_problema(db, origem_id, dados)
    if not origem:
        raise HTTPException(status_code=404, detail="Origem não encontrada")
    return origem

@app.delete("/origens_problema/{origem_id}")
def deletar_origem_problema(origem_id: int, db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
    sucesso = cruds.deletar_origem_problema(db, origem_id)
    if not sucesso:
        raise HTTPException(status_code=404, detail="Origem não encontrada")
    return {"detail": "Origem removida"}

# ---------------------- PRIORIDADES ----------------------
@app.get("/prioridades/", response_model=List[PrioridadeOut])
def listar_prioridades(db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
    return cruds.listar_prioridades(db)

@app.get("/prioridades/{prioridade_id}", response_model=PrioridadeOut)
def buscar_prioridade(prioridade_id: int, db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
    prioridade = cruds.buscar_prioridade_por_id(db, prioridade_id)
    if not prioridade:
        raise HTTPException(status_code=404, detail="Prioridade não encontrada")
    return prioridade

@app.post("/prioridades/", response_model=PrioridadeOut)
def criar_prioridade(prioridade: PrioridadeCreate, db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
    return cruds.criar_prioridade(db, prioridade)

@app.put("/prioridades/{prioridade_id}", response_model=PrioridadeOut)
def atualizar_prioridade(prioridade_id: int, dados: PrioridadeUpdate, db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
    prioridade = cruds.atualizar_prioridade(db, prioridade_id, dados)
    if not prioridade:
        raise HTTPException(status_code=404, detail="Prioridade não encontrada")
    return prioridade

@app.delete("/prioridades/{prioridade_id}")
def deletar_prioridade(prioridade_id: int, db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
    sucesso = cruds.deletar_prioridade(db, prioridade_id)
    if not sucesso:
        raise HTTPException(status_code=404, detail="Prioridade não encontrada")
    return {"detail": "Prioridade removida"}

# ---------------------- STATUS ----------------------
@app.get("/status/", response_model=List[StatusOut])
def listar_status(db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
    return cruds.listar_status(db)

@app.get("/status/{status_id}", response_model=StatusOut)
def buscar_status(status_id: int, db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
    status = cruds.buscar_status_por_id(db, status_id)
    if not status:
        raise HTTPException(status_code=404, detail="Status não encontrado")
    return status

@app.post("/status/", response_model=StatusOut)
def criar_status(status: StatusCreate, db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
    return cruds.criar_status(db, status)

@app.put("/status/{status_id}", response_model=StatusOut)
def atualizar_status(status_id: int, dados: StatusUpdate, db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
    status = cruds.atualizar_status(db, status_id, dados)
    if not status:
        raise HTTPException(status_code=404, detail="Status não encontrado")
    return status

@app.delete("/status/{status_id}")
def deletar_status(status_id: int, db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
    sucesso = cruds.deletar_status(db, status_id)
    if not sucesso:
        raise HTTPException(status_code=404, detail="Status não encontrado")
    return {"detail": "Status removido"}

# ---------------------- FREQUÊNCIAS ----------------------
@app.get("/frequencias/", response_model=List[FrequenciaOut])
def listar_frequencias(db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
    return cruds.listar_frequencias(db)

@app.get("/frequencias/{frequencia_id}", response_model=FrequenciaOut)
def obter_frequencia(frequencia_id: int, db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
    frequencia = cruds.obter_frequencia(db, frequencia_id)
    if not frequencia:
        raise HTTPException(status_code=404, detail="Frequência não encontrada")
    return frequencia

@app.post("/frequencias/", response_model=FrequenciaOut)
def criar_frequencia(frequencia: FrequenciaCreate, db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
    return cruds.criar_frequencia(db, frequencia)

@app.put("/frequencias/{frequencia_id}", response_model=FrequenciaOut)
def atualizar_frequencia(frequencia_id: int, dados: FrequenciaUpdate, db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
    frequencia = cruds.atualizar_frequencia(db, frequencia_id, dados)
    if not frequencia:
        raise HTTPException(status_code=404, detail="Frequência não encontrada")
    return frequencia

@app.delete("/frequencias/{frequencia_id}")
def deletar_frequencia(frequencia_id: int, db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
    frequencia = cruds.deletar_frequencia(db, frequencia_id)
    if not frequencia:
        raise HTTPException(status_code=404, detail="Frequência não encontrada")
    return {"detail": "Frequência removida"}

# ---------------------- CHAMADOS ----------------------
@app.get("/chamados/", response_model=List[ChamadoOut])
def listar_chamados(
    status_id: Optional[int] = None,
    empresa_id: Optional[int] = None,
    cliente: Optional[str] = None,
    responsavel_id: Optional[int] = None,
    order_by: str = "datetime_abertura",
    desc: bool = False,
    db: Session = Depends(get_db),
    usuario: UsuarioOut = Depends(get_current_user)
):
    return cruds.listar_chamados(
        db,
        status_id=status_id,
        empresa_id=empresa_id,
        cliente=cliente,
        responsavel_id=responsavel_id,
        order_by=order_by,
        desc=desc
    )

@app.get("/chamados/{chamado_id}", response_model=ChamadoOut)
def obter_chamado(chamado_id: int, db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
    chamado = cruds.obter_chamado(db, chamado_id)
    if not chamado:
        raise HTTPException(status_code=404, detail="Chamado não encontrado")
    return chamado

@app.get("/chamados/{chamado_id}/timeline", response_model=List[LogAcaoOut])
def timeline_chamado(chamado_id: int, db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
    logs = db.query(LogAcao).filter_by(chamado_id=chamado_id).order_by(LogAcao.data_hora.asc()).all()
    return logs

@app.post("/chamados/", response_model=ChamadoOut)
def criar_chamado(chamado: ChamadoCreate, db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
    return cruds.criar_chamado(db, chamado, usuario.id)

@app.put("/chamados/{chamado_id}", response_model=ChamadoOut)
def atualizar_chamado(chamado_id: int, dados: ChamadoUpdate, db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
    chamado = cruds.atualizar_chamado(db, chamado_id, dados, usuario_id=usuario.id)
    if not chamado:
        raise HTTPException(status_code=404, detail="Chamado não encontrado")
    return chamado

@app.delete("/chamados/{chamado_id}")
def deletar_chamado(chamado_id: int, db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
    sucesso = cruds.deletar_chamado(db, chamado_id, usuario.id)
    if not sucesso:
        raise HTTPException(status_code=404, detail="Chamado não encontrado")
    return {"detail": "Chamado removido"}

# ---------------------- CHAMADOS RECORRENTES ----------------------
@app.get("/chamados_recorrentes/", response_model=List[ChamadoRecorrenteOut])
def listar_chamados_recorrentes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
    return cruds.listar_chamados_recorrentes(db, skip=skip, limit=limit)

@app.get("/chamados_recorrentes/{chamado_id}", response_model=ChamadoRecorrenteOut)
def obter_chamado_recorrente(chamado_id: int, db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
    chamado = cruds.obter_chamado_recorrente(db, chamado_id)
    if not chamado:
        raise HTTPException(status_code=404, detail="Chamado recorrente não encontrado")
    return chamado

@app.post("/chamados_recorrentes/", response_model=ChamadoRecorrenteOut)
def criar_chamado_recorrente(chamado: ChamadoRecorrenteCreate, db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
    return cruds.criar_chamado_recorrente(db, chamado)

@app.put("/chamados_recorrentes/{chamado_id}", response_model=ChamadoRecorrenteOut)
def atualizar_chamado_recorrente(chamado_id: int, dados: ChamadoRecorrenteUpdate, db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
    chamado = cruds.atualizar_chamado_recorrente(db, chamado_id, dados)
    if not chamado:
        raise HTTPException(status_code=404, detail="Chamado recorrente não encontrado")
    return chamado

@app.delete("/chamados_recorrentes/{chamado_id}")
def deletar_chamado_recorrente(chamado_id: int, db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
    chamado = cruds.deletar_chamado_recorrente(db, chamado_id)
    if not chamado:
        raise HTTPException(status_code=404, detail="Chamado recorrente não encontrado")
    return {"detail": "Chamado recorrente removido"}

# ---------------------- ROLES ----------------------
@app.get("/roles/", response_model=List[RoleOut])
def listar_roles(db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
    return cruds.listar_roles(db)

@app.get("/roles/{role_id}", response_model=RoleOut)
def buscar_role(role_id: int, db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
    role = cruds.buscar_role_por_id(db, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Cargo não encontrado")
    return role

@app.post("/roles/", response_model=RoleOut)
def criar_role(role: RoleCreate, db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
    return cruds.criar_role(db, role)

@app.put("/roles/{role_id}", response_model=RoleOut)
def atualizar_role(role_id: int, dados: RoleUpdate, db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
    role = cruds.atualizar_role(db, role_id, dados)
    if not role:
        raise HTTPException(status_code=404, detail="Cargo não encontrado")
    return role

@app.delete("/roles/{role_id}")
def deletar_role(role_id: int, db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
    sucesso = cruds.deletar_role(db, role_id)
    if not sucesso:
        raise HTTPException(status_code=404, detail="Cargo não encontrado")
    return {"detail": "Cargo removido"}

# ---------------------- LOGS DE AÇÕES ----------------------
@app.get("/logs/", response_model=List[LogAcaoOut])
def listar_logs(db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
    return cruds.listar_logs(db)

@app.get("/logs/{log_id}", response_model=LogAcaoOut)
def buscar_log(log_id: int, db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
    log = cruds.buscar_log_por_id(db, log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Log não encontrado")
    return log

@app.post("/logs/", response_model=LogAcaoOut)
def criar_log(log: LogAcaoCreate, db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
    return cruds.criar_log_acao(db, log)

@app.delete("/logs/{log_id}")
def deletar_log(log_id: int, db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
    sucesso = cruds.deletar_log(db, log_id)
    if not sucesso:
        raise HTTPException(status_code=404, detail="Log não encontrado")
    return {"detail": "Log removido"}

# ---------------------- USUÁRIOS ----------------------
@app.get("/usuarios/", response_model=List[UsuarioOut])
def listar_usuarios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
    return cruds.listar_usuarios(db, skip=skip, limit=limit)

@app.get("/usuarios/{usuario_id}", response_model=UsuarioOut)
def obter_usuario(usuario_id: int, db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
    usuario_obj = cruds.get_usuario(db, usuario_id)
    if not usuario_obj:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario_obj

@app.post("/usuarios/", response_model=UsuarioOut)
def criar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db), usuario_autenticado: UsuarioOut = Depends(get_current_user)):
    existente = cruds.get_usuario_por_email(db, email=usuario.email)
    if existente:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    return cruds.criar_usuario(db, usuario.nome, usuario.email, usuario.senha)

@app.put("/usuarios/{usuario_id}", response_model=UsuarioOut)
def atualizar_usuario(usuario_id: int, dados: UsuarioUpdate, db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
    atualizado = cruds.atualizar_usuario(db, usuario_id, nome=dados.nome, email=dados.email, senha=dados.senha)
    if not atualizado:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return atualizado

@app.delete("/usuarios/{usuario_id}")
def deletar_usuario(usuario_id: int, db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
    sucesso = cruds.deletar_usuario(db, usuario_id)
    if not sucesso:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return {"detail": "Usuário removido"}

# ---------------------- DASHBOARD ----------------------
@app.get("/dashboard/basico")
def dashboard_basico(db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
    return cruds.contar_chamados_por_status(db)

@app.get("/dashboard/avancado")
def dashboard_avancado(db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
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
    
    
# ---------------------- RECUPERAR SENHA ----------------------
@app.post("/recuperar-senha")
def recuperar_senha(email: str = Body(..., embed=True), db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="E-mail não encontrado")

    token = criar_token_acesso(data={"sub": usuario.email}, expires_delta=timedelta(minutes=30))
    link = f"https://gleeful-maamoul-18d695.netlify.app/resetar-senha?token={token}"

    enviar_email_recuperacao(usuario.email, link)
    return {"mensagem": "E-mail enviado com instruções para redefinir a senha"}

# ---------------------- RESETAR SENHA ----------------------
@app.post("/resetar-senha")
def resetar_senha(token: str = Body(...), nova_senha: str = Body(...), db: Session = Depends(get_db)):
    try:
        dados = verificar_token(token)
        email = dados["sub"]
    except:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")

    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    usuario.senha_hash = hash_senha(nova_senha)
    db.commit()
    return {"mensagem": "Senha redefinida com sucesso"}