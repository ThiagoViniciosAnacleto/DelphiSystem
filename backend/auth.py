## --- Importações ---
import os
import smtplib
from datetime import datetime, timedelta
from typing import Optional, List
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Dependências de Terceiros
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session, joinedload

# Módulos Locais
from backend.database import SessionLocal
from backend import models

## --- Configuração de Segurança (Carregada do .env pelo main.py) ---

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 horas

# Chaves para o serviço de e-mail (SMTP nativo)
EMAIL_ORIGEM = os.getenv("EMAIL_ORIGEM")
EMAIL_SENHA_APP = os.getenv("EMAIL_SENHA_APP")

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

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY não definida no ambiente! (Verifique o .env e as variáveis no Render)")

## --- Dependência de Sessão do DB ---

def get_db():
    """Gera uma sessão do banco de dados para uma requisição."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

## --- Funções de Criptografia e Token ---

def gerar_hash_senha(senha: str) -> str:
    """Gera um hash seguro para uma senha em texto puro."""
    return pwd_context.hash(senha)

def verificar_senha(senha_plain: str, senha_hash: str) -> bool:
    """Verifica se a senha em texto puro corresponde ao hash."""
    return pwd_context.verify(senha_plain, senha_hash)

def criar_token_acesso(data: dict, expires_delta: Optional[timedelta] = None):
    """Cria um novo token JWT."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verificar_token(token: str) -> dict:
    """Decodifica um token, tratando erros. Usado para reset de senha."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")

## --- Funções de Autenticação e Autorização ---

def autenticar_usuario(db: Session, email: str, senha: str) -> Optional[models.Usuario]:
    """
    Autentica um usuário. 
    Verifica email, senha, se está ativo e já carrega o cargo (role).
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
    Dependência do FastAPI para obter o usuário logado a partir de um token.
    Também carrega o cargo (role) para evitar queries N+1.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if not email:
            raise CREDENTIALS_EXCEPTION
    except JWTError:
        raise CREDENTIALS_EXCEPTION

    usuario = (
        db.query(models.Usuario)
        .options(joinedload(models.Usuario.role)) # Eager load do cargo
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
        # Define 'comum' como padrão se o usuário não tiver cargo (role)
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


## --- Serviço de Envio de E-mail (SMTP Gmail Nativo) ---

def enviar_email_recuperacao(destinatario: str, link_recuperacao: str):
    """
    Envia um e-mail de recuperação de senha usando o SMTP nativo do Gmail.
    """
    # Verifica se as variáveis de ambiente essenciais foram carregadas
    if not EMAIL_ORIGEM or not EMAIL_SENHA_APP:
        print("ERRO DE CONFIGURAÇÃO: EMAIL_ORIGEM ou EMAIL_SENHA_APP não definidas.")
        raise RuntimeError("Erro ao enviar e-mail: Configuração do servidor incompleta.")

    # Criação do contêiner da mensagem
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Recuperação de Senha - Delphi System"
    msg["From"] = EMAIL_ORIGEM
    msg["To"] = destinatario

    # Template HTML profissional para o Delphi System
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px;">
        <h2 style="color: #333;">Recuperação de Senha</h2>
        <p style="color: #555; line-height: 1.6;">Olá,</p>
        <p style="color: #555; line-height: 1.6;">Recebemos uma solicitação para redefinir sua senha no <strong>Delphi System</strong>.</p>
        <p style="color: #555; line-height: 1.6;">Clique no botão abaixo para criar uma nova senha (este link é válido por 30 minutos):</p>
        <div style="text-align: center; margin: 30px 0;">
            <a href="{link_recuperacao}" style="background-color: #007BFF; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold;">Redefinir Minha Senha</a>
        </div>
        <p style="color: #555; line-height: 1.6; font-size: 14px;">Se você não solicitou essa alteração, basta ignorar este e-mail. Nenhuma mudança será feita na sua conta.</p>
        <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
        <p style="color: #999; font-size: 12px; text-align: center;">Equipe Técnica - Delphi System</p>
    </div>
    """

    # Anexa o HTML à mensagem
    part = MIMEText(html_content, "html")
    msg.attach(part)

    try:
        # Conecta ao servidor seguro do Gmail
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_ORIGEM, EMAIL_SENHA_APP)
            server.sendmail(EMAIL_ORIGEM, destinatario, msg.as_string())
            
        print(f"📧 E-mail de recuperação enviado via Gmail para {destinatario}!")
    except Exception as e:
        print(f"ERRO SMTP DO GMAIL: {e}")
        raise RuntimeError(f"Erro ao enviar e-mail via SMTP Gmail. Detalhes: {e}")