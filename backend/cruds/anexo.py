from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from .. import models, schemas
import os

# ---------------------- ANEXOS ----------------------

def criar_anexo(db: Session, anexo_info: dict, chamado_id: int, usuario_id: int) -> models.Anexo:
    """
    Cria um novo registro de anexo no banco de dados.
    """
    db_anexo = models.Anexo(
        chamado_id=chamado_id,
        usuario_id=usuario_id,
        nome_arquivo_original=anexo_info["nome_arquivo_original"],
        path_arquivo_armazenado=anexo_info["path_arquivo_armazenado"],
        content_type=anexo_info["content_type"],
        tamanho_bytes=anexo_info["tamanho_bytes"]
    )
    db.add(db_anexo)
    db.commit()
    db.refresh(db_anexo)
    return db_anexo

def listar_anexos_por_chamado(db: Session, chamado_id: int) -> List[models.Anexo]:
    """Retorna uma lista de todos os anexos ativos de um chamado específico."""
    return (
        db.query(models.Anexo)
        .options(joinedload(models.Anexo.usuario))
        .filter(models.Anexo.chamado_id == chamado_id, models.Anexo.ativo == True)
        .all()
    )

def buscar_anexo_por_id(db: Session, anexo_id: int) -> Optional[models.Anexo]:
    """Busca um anexo específico ativo pelo seu ID."""
    return (
        db.query(models.Anexo)
        .options(joinedload(models.Anexo.usuario), joinedload(models.Anexo.chamado))
        .filter(models.Anexo.id == anexo_id, models.Anexo.ativo == True)
        .first()
    )

def deletar_anexo(db: Session, anexo_id: int) -> bool:
    """
    Marca logicamente o anexo como inativo (soft delete).
    """
    db_anexo = buscar_anexo_por_id(db, anexo_id)
    if db_anexo:
        db_anexo.ativo = False
        db.commit()
        return True
    return False
