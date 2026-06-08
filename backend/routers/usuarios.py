from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List

# Importações internas
from backend.database import SessionLocal
import backend.cruds as cruds
import backend.models as models
from backend.schemas import UsuarioOut, UsuarioCreate, UsuarioUpdate
from backend.auth import get_current_user, admin_only

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuários"]
)

# Dependência do banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[UsuarioOut])
def listar_usuarios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
    return cruds.listar_usuarios(db, skip=skip, limit=limit)

@router.get("/{usuario_id}", response_model=UsuarioOut)
def obter_usuario(usuario_id: int, db: Session = Depends(get_db), usuario: UsuarioOut = Depends(get_current_user)):
    usuario_obj = cruds.get_usuario(db, usuario_id)
    if not usuario_obj:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario_obj

@router.post("/", response_model=UsuarioOut)
def criar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db), usuario_autenticado: models.Usuario = Depends(admin_only)):
    existente = cruds.get_usuario_por_email(db, email=usuario.email)
    if existente:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    return cruds.criar_usuario(db, usuario)

@router.put("/{usuario_id}", response_model=UsuarioOut)
async def atualizar_usuario(
    usuario_id: int,
    dados: UsuarioUpdate,
    db: Session = Depends(get_db),
    usuario_autenticado: models.Usuario = Depends(get_current_user)
):
    usuario_db = cruds.buscar_usuario_por_id(db, usuario_id)
    if not usuario_db:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # Regra 1: Apenas admins podem atualizar outros usuários
    if usuario_autenticado.id != usuario_id and usuario_autenticado.role.nome != "admin":
        raise HTTPException(
            status_code=403,
            detail="Você não tem permissão para atualizar este usuário."
        )

    # Regra 2: Apenas admins podem alterar status 'ativo' ou 'role_id'
    if (dados.ativo is not None and dados.ativo != usuario_db.ativo) or \
       (dados.role_id is not None and dados.role_id != usuario_db.role_id):
        if usuario_autenticado.role.nome != "admin":
            raise HTTPException(
                status_code=403,
                detail="Você não tem permissão para alterar o status ou o cargo deste usuário."
            )

    atualizado = cruds.atualizar_usuario(db, usuario_id, dados)
    if not atualizado:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return atualizado

@router.delete("/{usuario_id}")
def deletar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    usuario_autenticado: models.Usuario = Depends(admin_only)
):
    sucesso = cruds.deletar_usuario(db, usuario_id)
    if not sucesso:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return {"detail": "Usuário removido"}