from sqlalchemy.orm import Session
from .. import models, schemas

# ---------------------- TAGS ----------------------

def criar_tag(db: Session, tag: schemas.TagCreate) -> models.Tag:
    """Cria uma nova tag no banco de dados."""
    db_tag = models.Tag(nome=tag.nome)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag

def listar_tags(db: Session) -> list[models.Tag]:
    """Retorna uma lista de todas as tags."""
    return db.query(models.Tag).all()

def buscar_tag_por_id(db: Session, tag_id: int) -> models.Tag | None:
    """Busca uma tag específica pelo seu ID."""
    return db.query(models.Tag).filter(models.Tag.id == tag_id).first()

def buscar_tag_por_nome(db: Session, nome: str) -> models.Tag | None:
    """Busca uma tag específica pelo seu nome."""
    return db.query(models.Tag).filter(models.Tag.nome == nome).first()

def deletar_tag(db: Session, tag_id: int) -> bool:
    """Deleta uma tag do banco de dados."""
    db_tag = db.query(models.Tag).filter(models.Tag.id == tag_id).first()
    if db_tag:
        db.delete(db_tag)
        db.commit()
        return True
    return False