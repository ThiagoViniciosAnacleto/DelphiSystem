from sqlalchemy.orm import Session
from models import Chamado
from schemas import ChamadoCreate, ChamadoUpdate
from datetime import datetime

def criar_chamado(db: Session, dados: ChamadoCreate):
    chamado = Chamado(**dados.model_dump())
    chamado.datetime_abertura = datetime.utcnow()
    db.add(chamado)
    db.commit()
    db.refresh(chamado)
    return chamado

def listar_chamados(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Chamado).filter_by(ativo=True).offset(skip).limit(limit).all()

def obter_chamado(db: Session, chamado_id: int):
    return db.query(Chamado).filter_by(id=chamado_id, ativo=True).first()

def atualizar_chamado(db: Session, chamado_id: int, dados: ChamadoUpdate):
    chamado = db.query(Chamado).filter_by(id=chamado_id, ativo=True).first()
    if not chamado:
        return None
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(chamado, campo, valor)
        
    chamado.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(chamado)
    return chamado

def deletar_chamado(db: Session, chamado_id: int):
    chamado = db.query(Chamado).filter_by(id=chamado_id, ativo=True).first()
    if not chamado:
        return None
    chamado.ativo = False
    db.commit()
    return chamado
