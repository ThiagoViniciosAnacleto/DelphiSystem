from sqlalchemy.orm import Session
from backend.models import Usuario
from backend.schemas import UsuarioCreate, UsuarioUpdate
from werkzeug.security import generate_password_hash


def criar_usuario(db: Session, dados: UsuarioCreate):
    senha_hash = generate_password_hash(dados.senha)
    novo_usuario = Usuario(nome=dados.nome, email=dados.email, senha_hash=senha_hash)
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return novo_usuario


def listar_usuarios(db: Session, skip: int = 0, limit: int = 100) -> list[Usuario]:
    return db.query(Usuario).filter(Usuario.ativo == True).offset(skip).limit(limit).all()


def buscar_usuario_por_id(db: Session, usuario_id: int) -> Usuario | None:
    return db.query(Usuario).filter(Usuario.id == usuario_id, Usuario.ativo == True).first()


def get_usuario_por_email(db: Session, email: str) -> Usuario | None:
    return db.query(Usuario).filter(Usuario.email == email, Usuario.ativo == True).first()


def atualizar_usuario(
    db: Session, usuario_id: int, dados: UsuarioUpdate
) -> Usuario | None:
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id, Usuario.ativo == True).first()
    if usuario:
        dados_dict = dados.model_dump(exclude_unset=True)
        if "senha" in dados_dict:
            dados_dict["senha_hash"] = generate_password_hash(dados_dict.pop("senha"))
        for campo, valor in dados_dict.items():
            setattr(usuario, campo, valor)
        db.commit()
        db.refresh(usuario)
        return usuario
    return None


def deletar_usuario(db: Session, usuario_id: int) -> bool:
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id, Usuario.ativo == True).first()
    if usuario:
        usuario.ativo = False
        db.commit()
        return True
    return False
