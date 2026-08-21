from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from pathlib import Path
from dotenv import load_dotenv

from backend.models import Base

# Define o caminho raiz e carrega .env
ROOT_DIR = Path(__file__).resolve().parent.parent
env_path = ROOT_DIR / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

# Obtém URL do banco de dados com validação para ambiente de produção
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
DATABASE_URL = os.getenv("DATABASE_URL")

if ENVIRONMENT == "production":
    if not DATABASE_URL or DATABASE_URL.startswith("sqlite"):
        raise RuntimeError("DATABASE_URL de produção obrigatória e não deve utilizar SQLite.")
else:
    DATABASE_URL = DATABASE_URL or "sqlite:///./teste_local.db"

# Configurações do Engine
engine_kwargs = {}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs["pool_pre_ping"] = True

engine = create_engine(DATABASE_URL, **engine_kwargs)


# Cria sessão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Função geradora de sessão para injeção de dependência
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
