from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

# Importações do seu projeto
from backend.database import SessionLocal
import backend.cruds.empresa as cruds_empresa
from backend.schemas import EmpresaOut, EmpresaCreate, UsuarioOut
from backend.auth import get_current_user

# Aqui está o Architectural Router!
router = APIRouter(
    prefix="/empresas",
    tags=["Empresas"],
    # A MÁGICA DA SEGURANÇA: Aplica a trava em TODAS as rotas de empresas de uma vez só!
    dependencies=[Depends(get_current_user)] 
)

# Dependência do banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=EmpresaOut)
def criar_empresa(empresa: EmpresaCreate, db: Session = Depends(get_db)):
    return cruds_empresa.criar_empresa(db, empresa)

@router.get("/", response_model=List[EmpresaOut])
def listar_empresas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return cruds_empresa.obter_empresas(db, skip=skip, limit=limit)