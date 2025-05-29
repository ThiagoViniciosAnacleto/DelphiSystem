from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from backend.models import Chamado, Empresa, Usuario
from datetime import datetime, timedelta

def chamados_por_empresa(db: Session):
    return (
        db.query(Empresa.nome, func.count(Chamado.id))
        .join(Chamado, Chamado.empresa_id == Empresa.id)
        .filter(Chamado.ativo == True)
        .group_by(Empresa.nome)
        .all()
    )

def chamados_por_tecnico(db: Session):
    return (
        db.query(Usuario.nome, func.count(Chamado.id))
        .join(Chamado, Chamado.responsavel_atendimento_id == Usuario.id)
        .filter(Chamado.ativo == True)
        .group_by(Usuario.nome)
        .all()
    )

def chamados_ultimos_7_dias(db: Session):
    sete_dias_atras = datetime.utcnow() - timedelta(days=7)
    return (
        db.query(func.date(Chamado.datetime_abertura), func.count(Chamado.id))
        .filter(Chamado.ativo == True)
        .filter(Chamado.datetime_abertura >= sete_dias_atras)
        .group_by(func.date(Chamado.datetime_abertura))
        .order_by(func.date(Chamado.datetime_abertura))
        .all()
    )
