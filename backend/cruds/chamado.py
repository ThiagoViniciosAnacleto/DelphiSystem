from sqlalchemy.orm import Session
from backend.models import Chamado, LogAcao
from backend.models.schemas import ChamadoCreate, ChamadoUpdate
from datetime import datetime

def criar_chamado(db: Session, dados: ChamadoCreate, usuario_id: int):
    chamado = Chamado(**dados.model_dump())
    chamado.datetime_abertura = datetime.utcnow()
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
    status_id: int = None,
    empresa_id: int = None,
    cliente: str = None,
    responsavel_id: int = None,
    order_by: str = "datetime_abertura",
    desc: bool = False,
):
    query = db.query(Chamado).filter(Chamado.ativo == True)

    if status_id:
        query = query.filter(Chamado.status_id == status_id)
    if empresa_id:
        query = query.filter(Chamado.empresa_id == empresa_id)
    if cliente:
        query = query.filter(Chamado.cliente.ilike(f"%{cliente}%"))
    if responsavel_id:
        query = query.filter(Chamado.responsavel_atendimento_id == responsavel_id)

    if hasattr(Chamado, order_by):
        coluna = getattr(Chamado, order_by)
        query = query.order_by(coluna.desc() if desc else coluna.asc())

    return query.all()

def obter_chamado(db: Session, chamado_id: int):
    return db.query(Chamado).filter_by(id=chamado_id, ativo=True).first()

def atualizar_chamado(db: Session, chamado_id: int, dados: ChamadoUpdate, usuario_id: int):
    chamado = db.query(Chamado).filter_by(id=chamado_id, ativo=True).first()
    if not chamado:
        return None

    campos = dados.dict(exclude_unset=True)
    for campo, novo_valor in campos.items():
        valor_antigo = getattr(chamado, campo)
        if valor_antigo != novo_valor:
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

def deletar_chamado(db: Session, chamado_id: int, usuario_id: int):
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

