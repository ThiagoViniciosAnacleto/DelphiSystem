from sqlalchemy.orm import Session
from models import Empresa
from schemas import EmpresaCreate, EmpresaUpdate
from datetime import datetime


def criar_empresa(db: Session, empresa: EmpresaCreate):
    nova_empresa = Empresa(**empresa.dict())
    db.add(nova_empresa)
    db.commit()
    db.refresh(nova_empresa)
    return nova_empresa


def listar_empresas(db: Session):
    return db.query(Empresa).filter(Empresa.ativo == True).all()


def obter_empresa(db: Session, empresa_id: int):
    return db.query(Empresa).filter(Empresa.id == empresa_id, Empresa.ativo == True).first()


def atualizar_empresa(db: Session, empresa_id: int, dados: EmpresaUpdate):
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id, Empresa.ativo == True).first()
    if not empresa:
        return None

    for campo, valor in dados.dict(exclude_unset=True).items():
        setattr(empresa, campo, valor)

    db.commit()
    db.refresh(empresa)
    return empresa


def deletar_empresa(db: Session, empresa_id: int):
    empresa = db.query(Empresa).filter(Empresa.id == empresa_id, Empresa.ativo == True).first()
    if not empresa:
        return None

    empresa.ativo = False
    db.commit()
    return empresa
