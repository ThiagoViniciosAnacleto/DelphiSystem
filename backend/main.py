from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
import backend.cruds as cruds
from models import Usuario
from schemas import UsuarioCreate, UsuarioUpdate, UsuarioOut
from typing import List
from auth import get_current_user
from cruds.dashboard import (
    chamados_por_empresa,
    chamados_por_tecnico,
    chamados_ultimos_7_dias,
)

from database import Base, engine
Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/usuarios/", response_model=UsuarioOut)
def criar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    db_usuario = cruds.get_usuario_por_email(db, email=usuario.email)
    if db_usuario:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    novo_usuario = cruds.criar_usuario(db, usuario.nome, usuario.email, usuario.senha)
    return novo_usuario

@app.get("/usuarios/", response_model=List[UsuarioOut])
def ler_usuarios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    usuarios = cruds.listar_usuarios(db, skip=skip, limit=limit)
    return usuarios

@app.get("/usuarios/{usuario_id}", response_model=UsuarioOut)
def ler_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = cruds.get_usuario(db, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario

@app.put("/usuarios/{usuario_id}", response_model=UsuarioOut)
def atualizar_usuario(
    usuario_id: int,
    usuario: UsuarioUpdate,
    db: Session = Depends(get_db),
):
    usuario_atualizado = cruds.atualizar_usuario(
        db,
        usuario_id,
        nome=usuario.nome,
        email=usuario.email,
        senha=usuario.senha,
    )
    if not usuario_atualizado:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario_atualizado

@app.delete("/usuarios/{usuario_id}")
def deletar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = cruds.deletar_usuario(db, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return {"detail": "Usuário removido"}

@app.get("/dashboard/avancado")
def dashboard_avancado_view(db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
    return {
        "por_empresa": [{"empresa": nome, "quantidade": qtd} for nome, qtd in chamados_por_empresa(db)],
        "por_tecnico": [{"tecnico": nome, "quantidade": qtd} for nome, qtd in chamados_por_tecnico(db)],
        "ultimos_7_dias": [{"data": str(data), "quantidade": qtd} for data, qtd in chamados_ultimos_7_dias(db)],
    }
