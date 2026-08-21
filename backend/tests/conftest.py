import os
import shutil
from pathlib import Path
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

import backend.database as db_module
from backend.models import Base
from backend.main import app
import backend.main as main_module
from backend.models import Usuario, Role, Empresa, Status, Prioridade, Maquina, OrigemProblema, Frequencia
from backend.auth import gerar_hash_senha, criar_token_acesso, criar_token_recuperacao

# Banco de dados 100% em memória para não deixar arquivos em disco
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Substitui engine e SessionLocal do backend durante os testes
db_module.engine = engine
db_module.SessionLocal = TestingSessionLocal

@pytest.fixture(autouse=True)
def clean_db(tmp_path):
    # Configura diretório temporário isolado para uploads durante os testes
    test_upload_dir = tmp_path / "test_uploads"
    test_upload_dir.mkdir(parents=True, exist_ok=True)
    orig_upload_dir = main_module.UPLOAD_DIRECTORY
    main_module.UPLOAD_DIRECTORY = str(test_upload_dir)

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    yield

    main_module.UPLOAD_DIRECTORY = orig_upload_dir
    if test_upload_dir.exists():
        shutil.rmtree(test_upload_dir, ignore_errors=True)

@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[db_module.get_db] = override_get_db
    yield db
    db.close()
    app.dependency_overrides.pop(db_module.get_db, None)

@pytest.fixture
def client(db_session):
    return TestClient(app)

@pytest.fixture
def base_data(db_session):
    role_admin = Role(nome='admin')
    role_tecnico = Role(nome='tecnico')
    role_comum = Role(nome='comum')
    db_session.add_all([role_admin, role_tecnico, role_comum])
    db_session.commit()

    empresa = Empresa(nome='Empresa Teste')
    empresa2 = Empresa(nome='Empresa Outra')
    status_aberto = Status(nome='Aberto')
    status_fechado = Status(nome='Fechado')
    prioridade_alta = Prioridade(nome='Alta')
    prioridade_baixa = Prioridade(nome='Baixa')
    maquina = Maquina(modelo='Modelo Teste')
    origem = OrigemProblema(nome='Origem Teste')
    frequencia = Frequencia(nome='Mensal', dias=30)

    db_session.add_all([
        empresa, empresa2, status_aberto, status_fechado,
        prioridade_alta, prioridade_baixa, maquina, origem, frequencia
    ])
    db_session.commit()

    admin_user = Usuario(
        nome='Admin Teste',
        email='admin@test.com',
        senha_hash=gerar_hash_senha('SenhaForte123'),
        role_id=role_admin.id,
        ativo=True
    )
    tecnico_user = Usuario(
        nome='Tecnico Teste',
        email='tecnico@test.com',
        senha_hash=gerar_hash_senha('SenhaForte123'),
        role_id=role_tecnico.id,
        ativo=True
    )
    comum1_user = Usuario(
        nome='Comum 1 Teste',
        email='comum1@test.com',
        senha_hash=gerar_hash_senha('SenhaForte123'),
        role_id=role_comum.id,
        ativo=True
    )
    comum2_user = Usuario(
        nome='Comum 2 Teste',
        email='comum2@test.com',
        senha_hash=gerar_hash_senha('SenhaForte123'),
        role_id=role_comum.id,
        ativo=True
    )
    db_session.add_all([admin_user, tecnico_user, comum1_user, comum2_user])
    db_session.commit()

    admin_token = criar_token_acesso({'sub': admin_user.email, 'role': 'admin', 'id': admin_user.id})
    tecnico_token = criar_token_acesso({'sub': tecnico_user.email, 'role': 'tecnico', 'id': tecnico_user.id})
    comum1_token = criar_token_acesso({'sub': comum1_user.email, 'role': 'comum', 'id': comum1_user.id})
    comum2_token = criar_token_acesso({'sub': comum2_user.email, 'role': 'comum', 'id': comum2_user.id})

    return {
        'role_admin': role_admin,
        'role_tecnico': role_tecnico,
        'role_comum': role_comum,
        'empresa': empresa,
        'empresa2': empresa2,
        'status_aberto': status_aberto,
        'status_fechado': status_fechado,
        'prioridade_alta': prioridade_alta,
        'prioridade_baixa': prioridade_baixa,
        'maquina': maquina,
        'origem': origem,
        'frequencia': frequencia,
        'admin_user': admin_user,
        'tecnico_user': tecnico_user,
        'comum_user': comum1_user,
        'comum1_user': comum1_user,
        'comum2_user': comum2_user,
        'admin_token': admin_token,
        'tecnico_token': tecnico_token,
        'comum_token': comum1_token,
        'comum1_token': comum1_token,
        'comum2_token': comum2_token,
    }
