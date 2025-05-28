from sqlalchemy.orm import Session
from models import ChamadoRecorrente
from schemas import ChamadoRecorrenteCreate, ChamadoRecorrenteUpdate
from datetime import datetime

def criar_chamado_recorrente(db: Session, dados: ChamadoRecorrenteCreate):
    chamado = ChamadoRecorrente(**dados.model_dump())
    db.add(chamado)
    db.commit()
    db.refresh(chamado)
    return chamado

def listar_chamados_recorrentes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(ChamadoRecorrente).filter_by(ativo=True).offset(skip).limit(limit).all()

def obter_chamado_recorrente(db: Session, chamado_id: int):
    return db.query(ChamadoRecorrente).filter_by(id=chamado_id, ativo=True).first()

def atualizar_chamado_recorrente(db: Session, chamado_id: int, dados: ChamadoRecorrenteUpdate):
    chamado = db.query(ChamadoRecorrente).filter_by(id=chamado_id, ativo=True).first()
    if not chamado:
        return None
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(chamado, campo, valor)
    chamado.proxima_execucao = chamado.proxima_execucao or datetime.utcnow()
    db.commit()
    db.refresh(chamado)
    return chamado

def deletar_chamado_recorrente(db: Session, chamado_id: int):
    chamado = db.query(ChamadoRecorrente).filter_by(id=chamado_id, ativo=True).first()
    if not chamado:
        return None
    chamado.ativo = False
    db.commit()
    return chamado
