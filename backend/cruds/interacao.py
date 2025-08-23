from sqlalchemy.orm import Session
from .. import models, schemas

# ---------------------- INTERACOES ----------------------

def criar_interacao(db: Session, interacao: schemas.InteracaoCreate, chamado_id: int, usuario_id: int) -> models.Interacao:
    """Cria uma nova interação (comentário) para um chamado."""
    db_interacao = models.Interacao(
        **interacao.model_dump(),
        chamado_id=chamado_id,
        usuario_id=usuario_id
    )
    db.add(db_interacao)
    db.commit()
    db.refresh(db_interacao)
    return db_interacao

def listar_interacoes_por_chamado(db: Session, chamado_id: int) -> list[models.Interacao]:
    """Retorna uma lista de todas as interações de um chamado específico."""
    return db.query(models.Interacao).filter(models.Interacao.chamado_id == chamado_id).all()

def buscar_interacao_por_id(db: Session, interacao_id: int) -> models.Interacao | None:
    """Busca uma interação específica pelo seu ID."""
    return db.query(models.Interacao).filter(models.Interacao.id == interacao_id).first()

def atualizar_interacao(db: Session, interacao_id: int, dados: schemas.InteracaoUpdate) -> models.Interacao | None:
    """Atualiza o conteúdo de uma interação."""
    db_interacao = buscar_interacao_por_id(db, interacao_id)
    if db_interacao:
        # Pega os dados do schema que não são nulos para atualizar
        update_data = dados.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_interacao, key, value)
        db.commit()
        db.refresh(db_interacao)
    return db_interacao

def deletar_interacao(db: Session, interacao_id: int) -> bool:
    """Deleta uma interação (usará o SoftDeleteMixin se configurado no modelo)."""
    db_interacao = buscar_interacao_por_id(db, interacao_id)
    if db_interacao:
        db.delete(db_interacao)
        db.commit()
        return True
    return False