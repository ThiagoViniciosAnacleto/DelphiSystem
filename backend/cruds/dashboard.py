from sqlalchemy.orm import Session
from sqlalchemy import func
from models import Chamado, Status

def contar_chamados_por_status(db: Session):
    resultado = (
        db.query(Status.nome, func.count(Chamado.id))
        .join(Chamado, Chamado.status_id == Status.id)
        .filter(Chamado.ativo == True)
        .group_by(Status.nome)
        .all()
    )
    return [{"status": nome, "quantidade": qtd} for nome, qtd in resultado]