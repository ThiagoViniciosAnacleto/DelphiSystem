import pytest
from datetime import datetime, timedelta, timezone
from backend.models import ChamadoRecorrente, Chamado
import backend.executar_chamados_recorrentes as rec_module
from backend.tests.conftest import TestingSessionLocal

def test_executar_chamados_recorrentes(monkeypatch, db_session, base_data):
    monkeypatch.setattr(rec_module, "SessionLocal", TestingSessionLocal)

    agora = datetime.now(timezone.utc)
    passado = agora - timedelta(days=1)

    cr = ChamadoRecorrente(
        cliente='Cliente Recorrente 1',
        empresa_id=base_data['empresa'].id,
        relato='Manutenção preventiva mensal',
        frequencia_id=base_data['frequencia'].id,
        proxima_execucao=passado,
        ativo=True
    )
    db_session.add(cr)
    db_session.commit()

    # Executa o job
    rec_module.executar_chamados_recorrentes()

    # Verifica se o chamado foi gerado
    chamado_gerado = db_session.query(Chamado).filter(Chamado.contato == 'Cliente Recorrente 1').first()
    assert chamado_gerado is not None
    assert chamado_gerado.relato == 'Manutenção preventiva mensal'

    # Verifica se proxima_execucao foi avançada para o futuro
    db_session.refresh(cr)
    proxima = cr.proxima_execucao
    if proxima.tzinfo is not None:
        proxima = proxima.astimezone(timezone.utc).replace(tzinfo=None)
    assert proxima > datetime.utcnow()
