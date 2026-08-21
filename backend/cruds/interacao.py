from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
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

def listar_interacoes_por_chamado(db: Session, chamado_id: int, is_staff: bool = True) -> List[models.Interacao]:
    """Retorna uma lista de todas as interações ativas de um chamado específico."""
    query = (
        db.query(models.Interacao)
        .options(joinedload(models.Interacao.usuario))
        .filter(models.Interacao.chamado_id == chamado_id, models.Interacao.ativo == True)
    )
    if not is_staff:
        query = query.filter(models.Interacao.privado == False)
    return query.order_by(models.Interacao.data_interacao.asc()).all()

def buscar_interacao_por_id(db: Session, interacao_id: int) -> Optional[models.Interacao]:
    """Busca uma interação específica ativa pelo seu ID."""
    return (
        db.query(models.Interacao)
        .options(joinedload(models.Interacao.usuario))
        .filter(models.Interacao.id == interacao_id, models.Interacao.ativo == True)
        .first()
    )

def atualizar_interacao(db: Session, interacao_id: int, dados: schemas.InteracaoUpdate) -> Optional[models.Interacao]:
    """Atualiza o conteúdo de uma interação."""
    db_interacao = buscar_interacao_por_id(db, interacao_id)
    if db_interacao:
        update_data = dados.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_interacao, key, value)
        db.commit()
        db.refresh(db_interacao)
    return db_interacao

def deletar_interacao(db: Session, interacao_id: int) -> bool:
    """Deleta logicamente (soft delete) uma interação."""
    db_interacao = buscar_interacao_por_id(db, interacao_id)
    if db_interacao:
        db_interacao.ativo = False
        db.commit()
        return True
    return False
