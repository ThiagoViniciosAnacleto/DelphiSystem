from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

config = context.config

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# ---------- Configuração do .env ----------
env_path = Path(__file__).resolve().parent.parent / "backend" / ".env.dev"
load_dotenv(dotenv_path=env_path)

# ---------- Define URL do banco ----------
database_url = os.getenv("DATABASE_URL")
if database_url:
    config.set_main_option("sqlalchemy.url", database_url)
else:
    raise Exception("DATABASE_URL não encontrado no .env.dev")

# ---------- Logging padrão do Alembic ----------
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---------- Importa metadata dos modelos ----------
# Adiciona o diretório 'backend' ao sys.path para conseguir importar o models.py
sys.path.append(str(Path(__file__).resolve().parent.parent / "backend"))
from models import Base

target_metadata = Base.metadata

# ---------- Modo OFFLINE ----------
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

# ---------- Modo ONLINE ----------
def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

# ---------- Execução ----------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
