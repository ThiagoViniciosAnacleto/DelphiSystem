from sqlalchemy.orm import Session
from typing import Optional, List
from backend.models import Empresa
from backend.schemas import EmpresaCreate, EmpresaUpdate


def criar_empresa(db: Session, empresa: EmpresaCreate) -> Empresa:
    nova_empresa = Empresa(**empresa.model_dump())
    db.add(nova_empresa)
    db.commit()
    db.refresh(nova_empresa)
    return nova_empresa


def listar_empresas(db: Session, skip: int = 0, limit: Optional[int] = None) -> List[Empresa]:
    query = db.query(Empresa).filter(Empresa.ativo == True)
    if skip:
        query = query.offset(skip)
    if limit is not None:
        query = query.limit(limit)
    return query.all()


obter_empresas = listar_empresas


def obter_empresa(db: Session, empresa_id: int) -> Optional[Empresa]:
    return db.query(Empresa).filter(Empresa.id == empresa_id, Empresa.ativo == True).first()


buscar_empresa_por_id = obter_empresa


def atualizar_empresa(db: Session, empresa_id: int, dados: EmpresaUpdate) -> Optional[Empresa]:
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id, Empresa.ativo == True).first()
    if not empresa:
        return None

    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(empresa, campo, valor)

    db.commit()
    db.refresh(empresa)
    return empresa


def deletar_empresa(db: Session, empresa_id: int) -> Optional[Empresa]:
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id, Empresa.ativo == True).first()
    if not empresa:
        return None

    empresa.ativo = False
    db.commit()
    return empresa
