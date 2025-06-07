from sqlalchemy.orm import Session
from sqlalchemy import desc as sa_desc, asc as sa_asc # Importa para order_by dinâmico
from backend.models import Chamado, LogAcao, Status
from backend.schemas import ChamadoCreate, ChamadoUpdate
from datetime import datetime
from typing import Optional, List, Type

def criar_chamado(db: Session, dados: ChamadoCreate, usuario_id: int) -> Chamado:
    """
    Cria um novo chamado no banco de dados e registra a ação no log.
    A data e hora de abertura (datetime_abertura) serão geradas automaticamente pelo backend.
    """
    chamado = Chamado(**dados.model_dump(exclude_unset=True))


    db.add(chamado)
    db.commit()
    db.refresh(chamado)

    log = LogAcao(
        usuario_id=usuario_id,
        chamado_id=chamado.id,
        acao="criacao",
        tipo="chamado",
        campo=None,
        valor_antigo=None,
        valor_novo="Chamado criado"
    )
    db.add(log)
    db.commit()
    return chamado

def listar_chamados(
    db: Session,
    status_id: Optional[int] = None,
    empresa_id: Optional[int] = None,
    contato: Optional[str] = None,
    responsavel_id: Optional[int] = None,
    order_by: str = "datetime_abertura",
    desc: bool = False,
) -> List[Chamado]:

    query = db.query(Chamado).filter(Chamado.ativo == True)

    if status_id is not None:
        query = query.filter(Chamado.status_id == status_id)
    if empresa_id is not None:
        query = query.filter(Chamado.empresa_id == empresa_id)
    if contato:
        query = query.filter(Chamado.contato.ilike(f"%{contato}%"))
    if responsavel_id is not None:
        query = query.filter(Chamado.responsavel_atendimento_id == responsavel_id)

    # Validação e aplicação da ordenação
    if hasattr(Chamado, order_by):
        coluna = getattr(Chamado, order_by)
        if desc:
            query = query.order_by(sa_desc(coluna))
        else:
            query = query.order_by(sa_asc(coluna))
    else:
        print(f"Aviso: Campo '{order_by}' para ordenação não encontrado no modelo Chamado.")

    return query.all()

def obter_chamado(db: Session, chamado_id: int) -> Optional[Chamado]:
    """
    Obtém um chamado específico pelo seu ID.
    """
    return db.query(Chamado).filter_by(id=chamado_id, ativo=True).first()

def atualizar_chamado(db: Session, chamado_id: int, dados: ChamadoUpdate, usuario_id: int) -> Optional[Chamado]:
    """
    Atualiza um chamado existente e registra as alterações no log.
    """
    chamado = db.query(Chamado).filter_by(id=chamado_id, ativo=True).first()
    if not chamado:
        return None

    campos_atualizados = dados.model_dump(exclude_unset=True)

    for campo, novo_valor in campos_atualizados.items():
        valor_antigo = getattr(chamado, campo)
        if str(valor_antigo) != str(novo_valor): 
            log = LogAcao(
                usuario_id=usuario_id,
                chamado_id=chamado_id,
                acao="atualizacao",
                tipo="chamado",
                campo=campo,
                valor_antigo=str(valor_antigo) if valor_antigo is not None else None,
                valor_novo=str(novo_valor) if novo_valor is not None else None,
            )
            db.add(log)
        setattr(chamado, campo, novo_valor)

    db.commit()
    db.refresh(chamado)
    return chamado

def deletar_chamado(db: Session, chamado_id: int, usuario_id: int) -> Optional[Chamado]:
    """
    Marca um chamado como inativo (exclusão lógica) e registra a ação no log.
    """
    chamado = db.query(Chamado).filter_by(id=chamado_id, ativo=True).first()
    if not chamado:
        return None
    chamado.ativo = False
    db.commit()

    log = LogAcao(
        usuario_id=usuario_id,
        chamado_id=chamado_id,
        acao="remocao",
        tipo="chamado",
        campo=None,
        valor_antigo="Ativo",
        valor_novo="Inativo"
    )
    db.add(log)
    db.commit()
    return chamado

