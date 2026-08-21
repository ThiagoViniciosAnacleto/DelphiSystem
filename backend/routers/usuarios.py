from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

# Importações internas
from backend.database import get_db
import backend.cruds as cruds
import backend.models as models
from backend.schemas import UsuarioOut, UsuarioCreate, UsuarioUpdate
from backend.auth import get_current_user, admin_only

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuários"]
)


@router.get("/", response_model=List[UsuarioOut])
def listar_usuarios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), usuario: models.Usuario = Depends(get_current_user)):
    return cruds.listar_usuarios(db, skip=skip, limit=limit)


@router.get("/{usuario_id}", response_model=UsuarioOut)
def obter_usuario(usuario_id: int, db: Session = Depends(get_db), usuario: models.Usuario = Depends(get_current_user)):
    usuario_obj = cruds.buscar_usuario_por_id(db, usuario_id)
    if not usuario_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    return usuario_obj


@router.post("/", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def criar_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db), usuario_autenticado: models.Usuario = Depends(admin_only)):
    existente = cruds.get_usuario_por_email(db, email=usuario.email)
    if existente:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email já cadastrado")
    return cruds.criar_usuario(db, usuario)


@router.put("/{usuario_id}", response_model=UsuarioOut)
def atualizar_usuario(
    usuario_id: int,
    dados: UsuarioUpdate,
    db: Session = Depends(get_db),
    usuario_autenticado: models.Usuario = Depends(get_current_user)
):
    usuario_db = cruds.buscar_usuario_por_id(db, usuario_id)
    if not usuario_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")

    is_admin = bool(usuario_autenticado.role and usuario_autenticado.role.nome == "admin")

    # Regra 1: Apenas admins podem atualizar outros usuários
    if usuario_autenticado.id != usuario_id and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Você não tem permissão para atualizar este usuário."
        )

    # Regra 2: Apenas admins podem alterar status 'ativo' ou 'role_id'
    if (dados.ativo is not None and dados.ativo != usuario_db.ativo) or \
       (dados.role_id is not None and dados.role_id != usuario_db.role_id):
        if not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Você não tem permissão para alterar o status ou o cargo deste usuário."
            )

    atualizado = cruds.atualizar_usuario(db, usuario_id, dados)
    if not atualizado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    return atualizado


@router.delete("/{usuario_id}")
def deletar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    usuario_autenticado: models.Usuario = Depends(admin_only)
):
    sucesso = cruds.deletar_usuario(db, usuario_id)
    if not sucesso:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    return {"detail": "Usuário removido"}
