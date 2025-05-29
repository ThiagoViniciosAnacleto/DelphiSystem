from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

from backend.models import Base

# Carrega variáveis de ambiente com base no modo
modo = os.getenv("MODO", "DEV")

if modo == "DEV":
    load_dotenv(".env.dev")
else:
    load_dotenv(".env")

# Cria conexão com o banco
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

# Cria sessão
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Função geradora de sessão para injeção de dependência
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
