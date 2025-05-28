from sqlalchemy.orm import Session
from models import Maquina
from schemas import MaquinaCreate, MaquinaUpdate


def criar_maquina(db: Session, maquina_data: MaquinaCreate) -> Maquina:
    nova_maquina = Maquina(**maquina_data.model_dump())
    db.add(nova_maquina)
    db.commit()
    db.refresh(nova_maquina)
    return nova_maquina


def listar_maquinas(db: Session) -> list[Maquina]:
    return db.query(Maquina).all()


def buscar_maquina_por_id(db: Session, maquina_id: int) -> Maquina | None:
    return db.query(Maquina).filter(Maquina.id == maquina_id).first()


def atualizar_maquina(db: Session, maquina_id: int, maquina_data: MaquinaUpdate) -> Maquina | None:
    maquina = db.query(Maquina).filter(Maquina.id == maquina_id).first()
    if maquina:
        for campo, valor in maquina_data.model_dump(exclude_unset=True).items():
            setattr(maquina, campo, valor)
        db.commit()
        db.refresh(maquina)
        return maquina
    return None


def deletar_maquina(db: Session, maquina_id: int) -> bool:
    maquina = db.query(Maquina).filter(Maquina.id == maquina_id).first()
    if maquina:
        db.delete(maquina)
        db.commit()
        return True
    return False
