## --- Importações ---
import os
import hmac
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, List

# Dependências de Terceiros
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session, joinedload
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# Módulos Locais
from backend.database import SessionLocal, get_db
from backend import models

## --- Configuração de Segurança (Carregada do .env) ---

ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
SECRET_KEY = os.getenv("SECRET_KEY", "delphi_secret_key_default_for_development_replace_in_prod")

if ENVIRONMENT == "production":
    if not os.getenv("SECRET_KEY") or SECRET_KEY == "delphi_secret_key_default_for_development_replace_in_prod":
        raise RuntimeError("SECRET_KEY obrigatória e segura em ambiente de produção.")

ALGORITHM = "HS256"
ACCESS_AUDIENCE = "delphi_access"
RESET_AUDIENCE = "delphi_reset"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 horas
RESET_TOKEN_EXPIRE_MINUTES = 30       # 30 minutos

# Chaves para o serviço de e-mail (SendGrid)
EMAIL_ORIGEM = os.getenv("EMAIL_ORIGEM")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

# Contexto do Passlib para senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Esquema OAuth2 para o FastAPI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# Exceção padrão para falhas de credencial
CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Não foi possível validar as credenciais",
    headers={"WWW-Authenticate": "Bearer"},
)


## --- Funções de Criptografia, Validação e Token ---

def validar_complexidade_senha(senha: str) -> tuple[bool, str]:
    """Valida requisitos de complexidade da senha."""
    if not senha or len(senha) < 8:
        return False, "A senha deve ter no mínimo 8 caracteres."
    if not any(c.isdigit() for c in senha):
        return False, "A senha deve conter pelo menos um número."
    if not any(c.isalpha() for c in senha):
        return False, "A senha deve conter pelo menos uma letra."
    return True, ""

def gerar_hash_senha(senha: str) -> str:
    """Gera um hash seguro para uma senha em texto puro."""
    return pwd_context.hash(senha)

def verificar_senha(senha_plain: str, senha_hash: str) -> bool:
    """Verifica se a senha em texto puro corresponde ao hash."""
    return pwd_context.verify(senha_plain, senha_hash)

def calcular_fingerprint_senha(senha_hash: str) -> str:
    """Calcula um fingerprint criptográfico opaco (HMAC-SHA256) da hash de senha usando chave derivada."""
    if not senha_hash:
        return ""
    chave_derivada = hashlib.sha256(f"delphi_pwh_pepper:{SECRET_KEY}".encode("utf-8")).digest()
    return hmac.new(chave_derivada, senha_hash.encode("utf-8"), hashlib.sha256).hexdigest()

def validar_fingerprint_senha(fingerprint_token: str, senha_hash_atual: str) -> bool:
    """Valida se o fingerprint contido no token corresponde à hash atual da senha via compare_digest."""
    if not fingerprint_token or not senha_hash_atual:
        return False
    esperado = calcular_fingerprint_senha(senha_hash_atual)
    return hmac.compare_digest(fingerprint_token, esperado)

def criar_token_acesso(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Cria um token JWT específico para ACESSO à API com claim type e aud obrigatórias."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({
        "exp": expire,
        "type": "access",
        "aud": ACCESS_AUDIENCE
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def criar_token_recuperacao(data: dict, expires_delta: Optional[timedelta] = None, senha_hash: Optional[str] = None, pwh_fingerprint: Optional[str] = None) -> str:
    """Cria um token JWT específico para RECUPERAÇÃO DE SENHA com fingerprint opaco de uso único."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES))
    fingerprint = pwh_fingerprint or (calcular_fingerprint_senha(senha_hash) if senha_hash else None)
    if not fingerprint:
        raise ValueError("Fingerprint de senha obrigatório para token de recuperação.")
    to_encode.update({
        "exp": expire,
        "type": "password_reset",
        "aud": RESET_AUDIENCE,
        "pwh": fingerprint
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verificar_token_recuperacao(token: str) -> dict:
    """Decodifica e valida estritamente um token de recuperação de senha."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], audience=RESET_AUDIENCE)
        token_type = payload.get("type")
        if token_type != "password_reset":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token inválido para redefinição de senha."
            )
        if not payload.get("sub"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token de recuperação inválido."
            )
        if not payload.get("pwh"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token de recuperação sem fingerprint de segurança."
            )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado"
        )


def verificar_token(token: str) -> dict:
    """Decodifica um token de acesso validando a audiência."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], audience=ACCESS_AUDIENCE)
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")

## --- Funções de Autenticação e Autorização ---

def autenticar_usuario(db: Session, email: str, senha: str) -> Optional[models.Usuario]:
    """
    Autentica um usuário.
    Verifica email, senha, se está ativo e carrega o cargo (role).
    """
    usuario = (
        db.query(models.Usuario)
        .options(joinedload(models.Usuario.role))
        .filter(models.Usuario.email == email, models.Usuario.ativo == True)
        .first()
    )

    if not usuario or not verificar_senha(senha, usuario.senha_hash):
        return None

    return usuario

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.Usuario:
    """
    Dependência para obter o usuário logado a partir do token de acesso.
    Exige estritamente type=='access' e audiência 'delphi_access'.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], audience=ACCESS_AUDIENCE)
        token_type = payload.get("type")
        if token_type != "access":
            raise CREDENTIALS_EXCEPTION
        email: str = payload.get("sub")
        if not email:
            raise CREDENTIALS_EXCEPTION
    except JWTError:
        raise CREDENTIALS_EXCEPTION

    usuario = (
        db.query(models.Usuario)
        .options(joinedload(models.Usuario.role))
        .filter(models.Usuario.email == email, models.Usuario.ativo == True)
        .first()
    )

    if not usuario:
        raise CREDENTIALS_EXCEPTION
    return usuario


class RoleChecker:
    """
    Classe de dependência para verificar se o usuário atual
    tem uma das roles permitidas.
    """
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: models.Usuario = Depends(get_current_user)):
        user_role_name = "comum"
        if current_user.role and current_user.role.nome:
            user_role_name = current_user.role.nome

        if user_role_name not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso negado. Requer uma das seguintes roles: {', '.join(self.allowed_roles)}"
            )
        return current_user

admin_only = RoleChecker(["admin"])
tecnico_ou_admin = RoleChecker(["admin", "tecnico"])



## --- Serviço de Envio de E-mail (SendGrid) ---

def enviar_email_recuperacao(destinatario: str, link_recuperacao: str):
    """
    Envia um e-mail de recuperação de senha usando a API do SendGrid.
    """
    # Verifica se as variáveis de ambiente essenciais foram carregadas
    if not SENDGRID_API_KEY or not EMAIL_ORIGEM:
        print("ERRO DE CONFIGURAÇÃO: SENDGRID_API_KEY ou EMAIL_ORIGEM não definidas.")
        raise RuntimeError("Erro ao enviar e-mail: Configuração do servidor incompleta.")

    # HTML do e-mail (usando <br> para quebras de linha em HTML)
    html_content = f"""
    <html>
    <body>
        <p>Olá,</p>
        <p>Recebemos uma solicitação para redefinir sua senha no sistema Suporte Power Vending.</p>
        <p>Clique no link abaixo para criar uma nova senha (válido por 30 minutos):</p>
        <p><a href="{link_recuperacao}">Resetar Senha</a></p>
        <br>
        <p>Se você não solicitou essa alteração, ignore este e-mail.</p>
        <br>
        <p>Att,<br>Equipe Power Vending</p>
    </body>
    </html>
    """

    # Monta o objeto de e-mail do SendGrid
    message = Mail(
        from_email=EMAIL_ORIGEM,
        to_emails=destinatario,
        subject='Recuperação de Senha - Suporte Power',
        html_content=html_content
    )

    try:
        # Envia o e-mail
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)

        # Loga o sucesso (útil para debug no Render)
        print(f"E-mail de recuperação enviado para {destinatario}, status: {response.status_code}")

    except Exception as e:
        # Loga a falha (útil para debug no Render)
        print(f"ERRO DO SENDGRID: {e}")
        # Lança a exceção que o main.py vai capturar como um erro 500
        raise RuntimeError(f"Erro ao enviar e-mail via SendGrid: {e}")
