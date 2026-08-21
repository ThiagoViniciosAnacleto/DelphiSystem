## --- Importações ---
import os
import json
import urllib.request
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
        .options(joinedload(models.Usuario.role))  # Eager load do cargo
        .filter(models.Usuario.email == email, models.Usuario.ativo.is_(True))
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
        .options(joinedload(models.Usuario.role))  # Eager load do cargo
        .filter(models.Usuario.email == email, models.Usuario.ativo.is_(True))
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


## --- Serviço de Envio de E-mail (Brevo API nativa HTTPS) ---

def enviar_email_recuperacao(destinatario: str, link_recuperacao: str):
    """
    Envia um e-mail de recuperação de senha usando a API HTTPS do Brevo.
    As variáveis são lidas dentro da função para evitar amnésia de cache do Render.
    """
    email_remetente = os.getenv("EMAIL_ORIGEM")
    api_key = os.getenv("BREVO_API_KEY")

    # Validação rigorosa para logar o problema real
    if not email_remetente:
        print("❌ ERRO: A variável 'EMAIL_ORIGEM' não foi encontrada.")
        raise HTTPException(status_code=500, detail="Configuração de remetente incompleta no servidor.")
        
    if not api_key:
        print("❌ ERRO: A variável 'BREVO_API_KEY' não foi encontrada.")
        raise HTTPException(status_code=500, detail="Chave de API do Brevo incompleta no servidor.")

    url = "https://api.brevo.com/v3/smtp/email"
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
        <h2 style="color: #333;">Recuperação de Senha</h2>
        <p style="color: #555; line-height: 1.6;">Olá,</p>
        <p style="color: #555; line-height: 1.6;">Recebemos uma solicitação para redefinir a sua senha no <strong>Delphi System</strong>.</p>
        <p style="color: #555; line-height: 1.6;">Clique no botão abaixo para criar uma nova senha (este link é válido por 30 minutos):</p>
        <div style="text-align: center; margin: 30px 0;">
            <a href="{link_recuperacao}" style="background-color: #007BFF; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold;">Redefinir Minha Senha</a>
        </div>
        <p style="color: #555; line-height: 1.6; font-size: 14px;">Se não solicitou esta alteração, basta ignorar este e-mail. Nenhuma mudança será feita na sua conta.</p>
        <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
        <p style="color: #999; font-size: 12px; text-align: center;">Equipe Técnica - Delphi System</p>
    </div>
    """

    payload = {
        "sender": {"email": email_remetente, "name": "Delphi System"},
        "to": [{"email": destinatario}],
        "subject": "Recuperação de Senha - Delphi System",
        "htmlContent": html_content
    }

    data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(url, data=data, headers={
        "api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json"
    })

    try:
        with urllib.request.urlopen(req) as response:
            status_code = response.getcode()
            print(f"📧 E-mail de recuperação enviado via Brevo API! Status: {status_code}")
    except Exception as e:
        print(f"❌ ERRO API BREVO: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao disparar e-mail via Brevo API: {e}")
