from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.database import SessionLocal
import backend.cruds as cruds 
from backend.schemas import EmpresaOut, EmpresaCreate, EmpresaUpdate 
from backend.auth import get_current_user

router = APIRouter(
    prefix="/empresas",
    tags=["Empresas"],
    dependencies=[Depends(get_current_user)] 
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 1. LISTAR TODAS AS EMPRESAS
@router.get("/", response_model=List[EmpresaOut])
def listar_empresas(db: Session = Depends(get_db)):
    print("🛰️ Requisição recebida em /empresas")
    # Agora chamamos do módulo global
    return cruds.listar_empresas(db)

# 2. OBTER UMA EMPRESA POR ID
@router.get("/{empresa_id}", response_model=EmpresaOut)
def obter_empresa(empresa_id: int, db: Session = Depends(get_db)):
    empresa = cruds.obter_empresa(db, empresa_id)
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Empresa não encontrada"
        )
    return empresa

# 3. CRIAR UMA NOVA EMPRESA
@router.post("/", response_model=EmpresaOut, status_code=status.HTTP_201_CREATED)
def criar_empresa(empresa: EmpresaCreate, db: Session = Depends(get_db)):
    return cruds.criar_empresa(db, empresa)

# 4. ATUALIZAR UMA EMPRESA EXISTENTE
@router.put("/{empresa_id}", response_model=EmpresaOut)
def atualizar_empresa(empresa_id: int, dados: EmpresaUpdate, db: Session = Depends(get_db)):
    empresa = cruds.atualizar_empresa(db, empresa_id, dados)
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Empresa não encontrada"
        )
    return empresa

# 5. DELETAR UMA EMPRESA
@router.delete("/{empresa_id}", status_code=status.HTTP_200_OK)
def deletar_empresa(empresa_id: int, db: Session = Depends(get_db)):
    resultado = cruds.deletar_empresa(db, empresa_id)
    if not resultado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Empresa não encontrada"
        )
    return {"detail": "Empresa removida com sucesso"}