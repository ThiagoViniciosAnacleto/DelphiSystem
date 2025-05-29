from sqlalchemy.orm import Session
from backend.models import LogAcao
from backend.schemas import LogAcaoCreate
from datetime import datetime


def criar_log_acao(db: Session, log_data: LogAcaoCreate) -> LogAcao:
    novo_log = LogAcao(**log_data.model_dump(), data_hora=datetime.utcnow())
    db.add(novo_log)
    db.commit()
    db.refresh(novo_log)
    return novo_log


def listar_logs(db: Session) -> list[LogAcao]:
    return db.query(LogAcao).filter(LogAcao.ativo == True).all()


def buscar_log_por_id(db: Session, log_id: int) -> LogAcao | None:
    return db.query(LogAcao).filter(LogAcao.id == log_id, LogAcao.ativo == True).first()


def deletar_log(db: Session, log_id: int) -> bool:
    log = db.query(LogAcao).filter(LogAcao.id == log_id, LogAcao.ativo == True).first()
    if log:
        log.ativo = False
        db.commit()
        return log
    return False
