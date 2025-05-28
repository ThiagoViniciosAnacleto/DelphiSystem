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

def listar_chamados(
    db: Session,
    status_id: int = None,
    empresa_id: int = None,
    cliente: str = None,
    responsavel_id: int = None,
    order_by: str = "datetime_abertura",
    desc: bool = False,
):
    query = db.query(Chamado).filter(Chamado.ativo == True)

    if status_id:
        query = query.filter(Chamado.status_id == status_id)
    if empresa_id:
        query = query.filter(Chamado.empresa_id == empresa_id)
    if cliente:
        query = query.filter(Chamado.cliente.ilike(f"%{cliente}%"))
    if responsavel_id:
        query = query.filter(Chamado.responsavel_atendimento_id == responsavel_id)

    if hasattr(Chamado, order_by):
        coluna = getattr(Chamado, order_by)
        query = query.order_by(coluna.desc() if desc else coluna.asc())

    return query.all()

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
