import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from dotenv import load_dotenv  # Faltava isso!

from backend.database import SessionLocal
from backend import models

# Carrega variáveis de ambiente com base no modo
modo = os.getenv("MODO", "DEV")
if modo == "DEV":
    load_dotenv(".env.dev")
else:
    load_dotenv(".env")

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY não definida no ambiente!")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 horas

# Para gerar hash seguro da senha
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Para extração automática do token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# ------------------------
# Funções auxiliares
# ------------------------

def verificar_senha(senha_plain: str, senha_hash: str) -> bool:
    return pwd_context.verify(senha_plain, senha_hash)

def gerar_hash_senha(senha: str) -> str:
    return pwd_context.hash(senha)

def autenticar_usuario(db: Session, email: str, senha: str) -> Optional[models.Usuario]:
    usuario = db.query(models.Usuario).filter(models.Usuario.email == email, models.Usuario.ativo == True).first()
    if not usuario or not verificar_senha(senha, usuario.senha_hash):
        return None
    return usuario

def criar_token_acesso(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# ------------------------
# Obter usuário do token
# ------------------------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.Usuario:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if not email:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    usuario = db.query(models.Usuario).filter(models.Usuario.email == email, models.Usuario.ativo == True).first()
    if not usuario:
        raise credentials_exception
    return usuario
