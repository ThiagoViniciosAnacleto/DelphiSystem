from sqlalchemy.orm import Session
from typing import Optional, List
from backend.models import Frequencia
from backend.schemas import FrequenciaCreate, FrequenciaUpdate


def criar_frequencia(db: Session, frequencia_data: FrequenciaCreate) -> Frequencia:
    nova_frequencia = Frequencia(**frequencia_data.model_dump())
    db.add(nova_frequencia)
    db.commit()
    db.refresh(nova_frequencia)
    return nova_frequencia


def listar_frequencias(db: Session, skip: int = 0, limit: Optional[int] = None) -> List[Frequencia]:
    query = db.query(Frequencia)
    if skip:
        query = query.offset(skip)
    if limit is not None:
        query = query.limit(limit)
    return query.all()


def obter_frequencia(db: Session, frequencia_id: int) -> Optional[Frequencia]:
    return db.query(Frequencia).filter(Frequencia.id == frequencia_id).first()


buscar_frequencia_por_id = obter_frequencia


def atualizar_frequencia(db: Session, frequencia_id: int, frequencia_data: FrequenciaUpdate) -> Optional[Frequencia]:
    frequencia = obter_frequencia(db, frequencia_id)
    if not frequencia:
        return None
    for campo, valor in frequencia_data.model_dump(exclude_unset=True).items():
        setattr(frequencia, campo, valor)
    db.commit()
    db.refresh(frequencia)
    return frequencia


def deletar_frequencia(db: Session, frequencia_id: int) -> bool:
    frequencia = obter_frequencia(db, frequencia_id)
    if not frequencia:
        return False
    db.delete(frequencia)
    db.commit()
    return True
