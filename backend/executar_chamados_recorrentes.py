from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import get_db
from models import ChamadoRecorrente, Frequencia
from schemas import ChamadoCreate
from crud.chamado import criar_chamado
import os

# ID de sistema para logs automáticos
USUARIO_AUTOMATICO_ID = int(os.getenv("USUARIO_AUTOMATICO_ID", 1))  # pode ajustar

def executar_chamados_recorrentes():
    db: Session = next(get_db())
    hoje = datetime.utcnow()

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
        print(f"Gerando chamado do CR {cr.id} - {cr.cliente}")

        novo_chamado = ChamadoCreate(
            cliente=cr.cliente,
            empresa_id=cr.empresa_id,
            tipo_maquina_id=cr.tipo_maquina_id,
            origem_id=cr.origem_id,
            relato=cr.relato,
            porta_ssh=cr.porta_ssh,
            prioridade_id=cr.prioridade_id,
            responsavel_atendimento_id=cr.responsavel_atendimento_id,
            responsavel_acao_id=cr.responsavel_acao_id,
            descricao_acao=cr.descricao_acao,
        )

        criar_chamado(db, novo_chamado, usuario_id=USUARIO_AUTOMATICO_ID)

        cr.proxima_execucao += timedelta(days=cr.frequencia.dias)
        db.commit()

    print("✅ Execução concluída.")

if __name__ == "__main__":
    executar_chamados_recorrentes()
