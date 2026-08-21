import os
import sys
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

env_path = ROOT_DIR / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models import ChamadoRecorrente, Frequencia, Empresa
from backend.schemas import ChamadoCreate
from backend.cruds.chamado import criar_chamado

# ID de sistema para logs automáticos
USUARIO_AUTOMATICO_ID = int(os.getenv("USUARIO_AUTOMATICO_ID", "1"))


def calcular_proxima_execucao(proxima_atual: datetime, frequencia: Frequencia) -> datetime:
    nome_freq = (frequencia.nome or "").lower().strip()
    if hasattr(frequencia, "dias") and frequencia.dias:
        dias = frequencia.dias
    elif "diár" in nome_freq or "dia" in nome_freq:
        dias = 1
    elif "seman" in nome_freq:
        dias = 7
    elif "quinzen" in nome_freq:
        dias = 15
    elif "mens" in nome_freq:
        dias = 30
    elif "bimest" in nome_freq:
        dias = 60
    elif "semest" in nome_freq:
        dias = 180
    elif "an" in nome_freq:
        dias = 365
    else:
        dias = 30
    return proxima_atual + timedelta(days=dias)


def executar_chamados_recorrentes():
    db: Session = SessionLocal()
    hoje = datetime.now(timezone.utc)

    try:
        chamados_recorrentes = (
            db.query(ChamadoRecorrente)
            .join(Frequencia)
            .filter(
                ChamadoRecorrente.ativo == True,
                ChamadoRecorrente.proxima_execucao <= hoje,
            )
            .all()
        )

        for cr in chamados_recorrentes:
            print(f"Gerando chamado do CR #{cr.id} - {cr.cliente}")

            empresa_id = cr.empresa_id
            if not empresa_id:
                empresa_padrao = db.query(Empresa).filter(Empresa.ativo == True).first()
                if not empresa_padrao:
                    empresa_padrao = Empresa(nome="Empresa Padrão")
                    db.add(empresa_padrao)
                    db.commit()
                    db.refresh(empresa_padrao)
                empresa_id = empresa_padrao.id

            acao_realizada = getattr(cr, "acao_realizada", None) or getattr(cr, "descricao_acao", None)

            novo_chamado = ChamadoCreate(
                contato=cr.cliente,
                empresa_id=empresa_id,
                tipo_maquina_id=cr.tipo_maquina_id,
                origem_id=cr.origem_id,
                relato=cr.relato,
                porta_ssh=cr.porta_ssh,
                prioridade_id=cr.prioridade_id,
                responsavel_atendimento_id=cr.responsavel_atendimento_id,
                responsavel_acao_id=cr.responsavel_acao_id,
                acao_realizada=acao_realizada,
            )

            criar_chamado(db, novo_chamado, usuario_id=USUARIO_AUTOMATICO_ID)

            cr.proxima_execucao = calcular_proxima_execucao(cr.proxima_execucao or hoje, cr.frequencia)
            db.commit()

        print(f"✅ Execução de chamados recorrentes concluída. Processados: {len(chamados_recorrentes)}")
    finally:
        db.close()


if __name__ == "__main__":
    executar_chamados_recorrentes()
