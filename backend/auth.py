## --- Importações ---
import os
from datetime import datetime, timedelta
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
from backend.database import SessionLocal
from backend import models

## --- Configuração de Segurança (Carregada do .env pelo main.py) ---

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 horas

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
        .filter(models.Usuario.email == email, models.Usuario.ativo == True)
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