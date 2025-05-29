from sqlalchemy.orm import Session
from backend.models import OrigemProblema
from backend.schemas import OrigemProblemaCreate, OrigemProblemaUpdate


def criar_origem_problema(db: Session, origem_data: OrigemProblemaCreate) -> OrigemProblema:
    nova_origem = OrigemProblema(**origem_data.model_dump())
    db.add(nova_origem)
    db.commit()
    db.refresh(nova_origem)
    return nova_origem


def listar_origens_problema(db: Session) -> list[OrigemProblema]:
    return db.query(OrigemProblema).filter(OrigemProblema.ativo == True).all()


def buscar_origem_problema_por_id(db: Session, origem_id: int) -> OrigemProblema | None:
    return db.query(OrigemProblema).filter(
        OrigemProblema.id == origem_id,
        OrigemProblema.ativo == True
    ).first()


def atualizar_origem_problema(
    db: Session, origem_id: int, origem_data: OrigemProblemaUpdate
) -> OrigemProblema | None:
    origem = db.query(OrigemProblema).filter(
        OrigemProblema.id == origem_id,
        OrigemProblema.ativo == True
    ).first()
    if origem:
        for campo, valor in origem_data.model_dump(exclude_unset=True).items():
            setattr(origem, campo, valor)
        db.commit()
        db.refresh(origem)
    return origem


def deletar_origem_problema(db: Session, origem_id: int) -> bool:
    origem = db.query(OrigemProblema).filter(
        OrigemProblema.id == origem_id,
        OrigemProblema.ativo == True
    ).first()
    if origem:
        origem.ativo = False
        db.commit()
        return True
    return False
