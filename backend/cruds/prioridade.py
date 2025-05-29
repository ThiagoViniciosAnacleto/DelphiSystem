from sqlalchemy.orm import Session
from backend.models import Prioridade
from backend.schemas import PrioridadeCreate, PrioridadeUpdate


def criar_prioridade(db: Session, dados: PrioridadeCreate) -> Prioridade:
    nova_prioridade = Prioridade(**dados.model_dump())
    db.add(nova_prioridade)
    db.commit()
    db.refresh(nova_prioridade)
    return nova_prioridade


def listar_prioridades(db: Session) -> list[Prioridade]:
    return db.query(Prioridade).all()


def buscar_prioridade_por_id(db: Session, prioridade_id: int) -> Prioridade | None:
    return db.query(Prioridade).filter(Prioridade.id == prioridade_id).first()


def atualizar_prioridade(
    db: Session, prioridade_id: int, dados: PrioridadeUpdate
) -> Prioridade | None:
    prioridade = db.query(Prioridade).filter(Prioridade.id == prioridade_id).first()
    if prioridade:
        for campo, valor in dados.model_dump(exclude_unset=True).items():
            setattr(prioridade, campo, valor)
        db.commit()
        db.refresh(prioridade)
        return prioridade
    return None


def deletar_prioridade(db: Session, prioridade_id: int) -> bool:
    prioridade = db.query(Prioridade).filter(Prioridade.id == prioridade_id).first()
    if prioridade:
        db.delete(prioridade)
        db.commit()
        return True
    return False
