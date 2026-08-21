from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.database import get_db
import backend.cruds.empresa as cruds_empresa
from backend.schemas import EmpresaOut, EmpresaCreate, EmpresaUpdate
from backend.auth import get_current_user, admin_only

router = APIRouter(
    prefix="/empresas",
    tags=["Empresas"],
    dependencies=[Depends(get_current_user)]
)


@router.get("/", response_model=List[EmpresaOut])
def listar_empresas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return cruds_empresa.listar_empresas(db, skip=skip, limit=limit)


@router.get("/{id}", response_model=EmpresaOut)
def obter_empresa(id: int, db: Session = Depends(get_db)):
    empresa = cruds_empresa.obter_empresa(db, id)
    if not empresa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa não encontrada")
    return empresa


@router.post("/", response_model=EmpresaOut, dependencies=[Depends(admin_only)], status_code=status.HTTP_201_CREATED)
def criar_empresa(empresa: EmpresaCreate, db: Session = Depends(get_db)):
    return cruds_empresa.criar_empresa(db, empresa)


@router.put("/{id}", response_model=EmpresaOut, dependencies=[Depends(admin_only)])
def atualizar_empresa(id: int, dados: EmpresaUpdate, db: Session = Depends(get_db)):
    empresa = cruds_empresa.atualizar_empresa(db, id, dados)
    if not empresa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa não encontrada")
    return empresa


@router.delete("/{id}", dependencies=[Depends(admin_only)])
def deletar_empresa(id: int, db: Session = Depends(get_db)):
    empresa = cruds_empresa.deletar_empresa(db, id)
    if not empresa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Empresa não encontrada")
    return {"message": "Empresa inativada com sucesso"}
