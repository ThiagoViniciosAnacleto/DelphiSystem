from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

# Importações da arquitetura do projeto
from backend.database import SessionLocal
import backend.cruds.empresa as cruds_empresa
# Adicionei o seu schema de atualização aqui (ajuste se o nome for diferente)
from backend.schemas import EmpresaOut, EmpresaCreate, EmpresaUpdate 
from backend.auth import get_current_user

# Padrão de Projeto: Architectural Router
router = APIRouter(
    prefix="/empresas",
    tags=["Empresas"],
    # Trava global de segurança para este arquivo (mitiga duplicação de código)
    dependencies=[Depends(get_current_user)] 
)

# Injeção de dependência do Banco de Dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 1. LISTAR TODAS AS EMPRESAS
@router.get("/", response_model=List[EmpresaOut])
def listar_empresas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    print("🛰️ Requisição recebida em /empresas")
    return cruds_empresa.obter_empresas(db, skip=skip, limit=limit)

# 2. OBTER UMA EMPRESA POR ID
@router.get("/{empresa_id}", response_model=EmpresaOut)
def obter_empresa(empresa_id: int, db: Session = Depends(get_db)):
    empresa = cruds_empresa.obter_empresa(db, empresa_id)
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Empresa não encontrada"
        )
    return empresa

# 3. CRIAR UMA NOVA EMPRESA
@router.post("/", response_model=EmpresaOut, status_code=status.HTTP_201_CREATED)
def criar_empresa(empresa: EmpresaCreate, db: Session = Depends(get_db)):
    return cruds_empresa.criar_empresa(db, empresa)

# 4. ATUALIZAR UMA EMPRESA EXISTENTE
@router.put("/{empresa_id}", response_model=EmpresaOut)
def atualizar_empresa(empresa_id: int, dados: EmpresaUpdate, db: Session = Depends(get_db)):
    empresa = cruds_empresa.atualizar_empresa(db, empresa_id, dados)
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Empresa não encontrada"
        )
    return empresa

# 5. DELETAR UMA EMPRESA
@router.delete("/{empresa_id}", status_code=status.HTTP_200_OK)
def deletar_empresa(empresa_id: int, db: Session = Depends(get_db)):
    resultado = cruds_empresa.deletar_empresa(db, empresa_id)
    if not resultado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Empresa não encontrada"
        )
    return {"detail": "Empresa removida com sucesso"}