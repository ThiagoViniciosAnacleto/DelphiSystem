from typing import Optional, List
from sqlalchemy.orm import Session
from backend.models import Empresa
from backend.schemas import EmpresaCreate, EmpresaUpdate

def criar_empresa(db: Session, empresa: EmpresaCreate) -> Empresa:
    """Cria uma nova empresa no banco de dados."""
    nova_empresa = Empresa(**empresa.model_dump())
    db.add(nova_empresa)
    db.commit()
    db.refresh(nova_empresa)
    return nova_empresa


def listar_empresas(db: Session, skip: int = 0, limit: Optional[int] = None) -> List[Empresa]:
    """Retorna uma lista com todas as empresas ativas."""
    query = db.query(Empresa).filter(Empresa.ativo.is_(True))
    if skip:
        query = query.offset(skip)
    if limit is not None:
        query = query.limit(limit)
    return query.all()


obter_empresas = listar_empresas


def obter_empresa(db: Session, empresa_id: int) -> Optional[Empresa]:
    """Busca uma empresa específica pelo ID, desde que esteja ativa."""
    return db.query(Empresa).filter(Empresa.id == empresa_id, Empresa.ativo.is_(True)).first()


buscar_empresa_por_id = obter_empresa


def atualizar_empresa(db: Session, empresa_id: int, dados: EmpresaUpdate) -> Optional[Empresa]:
    """Atualiza de forma parcial os dados de uma empresa existente."""
    empresa = obter_empresa(db, empresa_id)
    if not empresa:
        return None

    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(empresa, campo, valor)

    db.commit()
    db.refresh(empresa)
    return empresa


def deletar_empresa(db: Session, empresa_id: int) -> Optional[Empresa]:
    """Realiza o soft delete (inativação lógica) de uma empresa."""
    empresa = obter_empresa(db, empresa_id)
    if not empresa:
        return None

    empresa.ativo = False
    db.commit()
    return empresa
