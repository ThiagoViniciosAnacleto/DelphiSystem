from sqlalchemy.orm import Session
from sqlalchemy import desc as sa_desc, asc as sa_asc # Importa para order_by dinâmico
from sqlalchemy.orm import Session, joinedload, selectinload
from backend import models
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
    chamado.criado_por_id = usuario_id

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

def verificar_acesso_chamado(chamado: Optional[Chamado], usuario: models.Usuario) -> bool:
    """
    Verifica se o usuário tem permissão para acessar/modificar o chamado.
    Admin e técnicos acessam todos. Usuário comum acessa apenas os que criou.
    """
    if not chamado or not getattr(chamado, "ativo", True):
        return False
    user_role = usuario.role.nome if (usuario.role and usuario.role.nome) else "comum"
    if user_role in ["admin", "tecnico"]:
        return True
    if chamado.criado_por_id is not None and chamado.criado_por_id == usuario.id:
        return True
    return False

def listar_chamados(
    db: Session,
    status_id: Optional[int] = None,
    empresa_id: Optional[int] = None,
    contato: Optional[str] = None,
    responsavel_id: Optional[int] = None,
    prioridade_id: Optional[int] = None,
    order_by: str = "datetime_abertura",
    desc: bool = False,
    skip: int = 0,
    limit: Optional[int] = None,
    usuario: Optional[models.Usuario] = None
) -> List[Chamado]:

    query = (
        db.query(Chamado)
        .filter(Chamado.ativo == True)
        .options(
            joinedload(Chamado.empresa),
            joinedload(Chamado.prioridade),
            joinedload(Chamado.status),
            joinedload(Chamado.tipo_maquina),
            joinedload(Chamado.origem),
            joinedload(Chamado.criado_por),
            joinedload(Chamado.responsavel_atendimento),
            joinedload(Chamado.responsavel_acao),
            selectinload(Chamado.tags),
            selectinload(Chamado.anexos).joinedload(models.Anexo.usuario),
            selectinload(Chamado.interacoes).joinedload(models.Interacao.usuario),
        )
    )

    # Política de menor privilégio: usuário comum lista estritamente os chamados que criou
    is_staff = True
    if usuario is not None:
        user_role = usuario.role.nome if (usuario.role and usuario.role.nome) else "comum"
        if user_role not in ["admin", "tecnico"]:
            is_staff = False
            query = query.filter(Chamado.criado_por_id == usuario.id)

    if status_id is not None:
        query = query.filter(Chamado.status_id == status_id)
    if empresa_id is not None:
        query = query.filter(Chamado.empresa_id == empresa_id)
    if prioridade_id is not None:
        query = query.filter(Chamado.prioridade_id == prioridade_id)
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

    if skip:
        query = query.offset(skip)
    if limit is not None:
        query = query.limit(limit)

    chamados = query.all()
    if not is_staff:
        for ch in chamados:
            ch.interacoes = [i for i in ch.interacoes if not i.privado and i.ativo]
            ch.anexos = [a for a in ch.anexos if a.ativo]
    return chamados


def obter_chamado(db: Session, chamado_id: int, is_staff: bool = True) -> Optional[Chamado]:
    """
    Obtém um chamado específico pelo seu ID com eager loading de relacionamentos.
    """
    chamado = (
        db.query(models.Chamado)
        .filter_by(id=chamado_id, ativo=True)
        .options(
            joinedload(models.Chamado.empresa),
            joinedload(models.Chamado.prioridade),
            joinedload(models.Chamado.status),
            joinedload(models.Chamado.tipo_maquina),
            joinedload(models.Chamado.origem),
            joinedload(models.Chamado.responsavel_atendimento),
            joinedload(models.Chamado.responsavel_acao),
            selectinload(models.Chamado.tags),
            selectinload(models.Chamado.interacoes).joinedload(models.Interacao.usuario),
            selectinload(models.Chamado.anexos).joinedload(models.Anexo.usuario)
        )
        .first()
    )
    if chamado and not is_staff:
        chamado.interacoes = [i for i in chamado.interacoes if not i.privado and i.ativo]
        chamado.anexos = [a for a in chamado.anexos if a.ativo]
    return chamado


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
