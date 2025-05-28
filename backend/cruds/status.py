from sqlalchemy.orm import Session
from models import Status
from schemas import StatusCreate, StatusUpdate


def criar_status(db: Session, dados: StatusCreate) -> Status:
    novo_status = Status(**dados.model_dump())
    db.add(novo_status)
    db.commit()
    db.refresh(novo_status)
    return novo_status


def listar_status(db: Session) -> list[Status]:
    return db.query(Status).all()


def buscar_status_por_id(db: Session, status_id: int) -> Status | None:
    return db.query(Status).filter(Status.id == status_id).first()


def atualizar_status(
    db: Session, status_id: int, dados: StatusUpdate
) -> Status | None:
    status = db.query(Status).filter(Status.id == status_id).first()
    if status:
        for campo, valor in dados.model_dump(exclude_unset=True).items():
            setattr(status, campo, valor)
        db.commit()
        db.refresh(status)
        return status
    return None


def deletar_status(db: Session, status_id: int) -> bool:
    status = db.query(Status).filter(Status.id == status_id).first()
    if status:
        db.delete(status)
        db.commit()
        return True
    return False
