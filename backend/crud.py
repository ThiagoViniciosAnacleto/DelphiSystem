from sqlalchemy.orm import Session
from models import Usuario
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_usuario(db: Session, usuario_id: int):
    return db.query(Usuario).filter(Usuario.id == usuario_id).first()

def get_usuario_por_email(db: Session, email: str):
    return db.query(Usuario).filter(Usuario.email == email).first()

def listar_usuarios(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Usuario).offset(skip).limit(limit).all()

def criar_usuario(db: Session, nome: str, email: str, senha: str):
    senha_hash = pwd_context.hash(senha)
    db_usuario = Usuario(nome=nome, email=email, senha_hash=senha_hash)
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

def atualizar_usuario(db: Session, usuario_id: int, nome: str = None, email: str = None, senha: str = None):
    usuario = get_usuario(db, usuario_id)
    if not usuario:
        return None
    if nome:
        usuario.nome = nome
    if email:
        usuario.email = email
    if senha:
        usuario.senha_hash = pwd_context.hash(senha)
    db.commit()
    db.refresh(usuario)
    return usuario

def deletar_usuario(db: Session, usuario_id: int):
    usuario = get_usuario(db, usuario_id)
    if not usuario:
        return None
    db.delete(usuario)
    db.commit()
    return usuario
