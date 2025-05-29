from sqlalchemy.orm import Session
from backend.models import Frequencia
from backend.schemas import FrequenciaCreate, FrequenciaUpdate


def criar_frequencia(db: Session, frequencia_data: FrequenciaCreate) -> Frequencia:
    nova_frequencia = Frequencia(**frequencia_data.dict())
    db.add(nova_frequencia)
    db.commit()
    db.refresh(nova_frequencia)
    return nova_frequencia


def listar_frequencias(db: Session):
    return db.query(Frequencia).all()


def obter_frequencia(db: Session, frequencia_id: int):
    return db.query(Frequencia).first()


def atualizar_frequencia(db: Session, frequencia_id: int, frequencia_data: FrequenciaUpdate):
    frequencia = obter_frequencia(db, frequencia_id)
    if not frequencia:
        return None
    for campo, valor in frequencia_data.dict(exclude_unset=True).items():
        setattr(frequencia, campo, valor)
    db.commit()
    db.refresh(frequencia)
    return frequencia


def deletar_frequencia(db: Session, frequencia_id: int):
    frequencia = obter_frequencia(db, frequencia_id)
    if not frequencia:
        return None
    db.delete(frequencia)
    db.commit()
    return frequencia
