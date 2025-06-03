import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from backend.database import SessionLocal
from backend import models
from sqlalchemy.orm import joinedload

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

def gerar_hash_senha(senha: str) -> str:
    return pwd_context.hash(senha)

def verificar_senha(senha_plain: str, senha_hash: str) -> bool:
    return pwd_context.verify(senha_plain, senha_hash)

def autenticar_usuario(db: Session, email: str, senha: str) -> Optional[models.Usuario]:
    """Autentica um usuário verificando email, senha e se está ativo.
    Carrega também o relacionamento com o cargo (role).
    """
    usuario = (
        db.query(models.Usuario)
        .options(joinedload(models.Usuario.role))  # Garante que usuario.role.nome esteja disponível
        .filter(models.Usuario.email == email, models.Usuario.ativo == True)
        .first()
    )

    if not usuario or not verificar_senha(senha, usuario.senha_hash):
        return None

    return usuario


def criar_token_acesso(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

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


import smtplib
from email.mime.text import MIMEText

def enviar_email_recuperacao(destinatario: str, link: str):
    remetente = os.getenv("EMAIL_ORIGEM")
    senha = os.getenv("EMAIL_SENHA")

    if not remetente or not senha:
        raise RuntimeError("Variáveis EMAIL_ORIGEM e EMAIL_SENHA não definidas")

    msg = MIMEText(f"""
Olá,

Recebemos uma solicitação para redefinir sua senha no sistema Suporte Power Vending.

Clique no link abaixo para criar uma nova senha (válido por 30 minutos):

{link}

Se você não solicitou essa alteração, ignore este e-mail.

Att,
Equipe Power Vending
    """)
    msg["Subject"] = "Recuperação de Senha - Suporte Power"
    msg["From"] = remetente
    msg["To"] = destinatario

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(remetente, senha)
            server.send_message(msg)
    except Exception as e:
        raise RuntimeError(f"Erro ao enviar e-mail: {e}")

def verificar_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as e:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")
