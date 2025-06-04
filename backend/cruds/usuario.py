from sqlalchemy.orm import Session
from backend.models import Usuario
from backend.schemas import UsuarioCreate, UsuarioUpdate
from backend.auth import gerar_hash_senha


def criar_usuario(db: Session, dados: UsuarioCreate):
    senha_hash = gerar_hash_senha(dados.senha)

    final_role_id = dados.role_id

    if final_role_id is None:
        # Se nenhum role_id foi fornecido, buscar o ID da role "comum"
        role_comum = db.query(Role).filter(Role.nome == "comum").first()

        if role_comum:
            final_role_id = role_comum.id

        else:
            raise HTTPException(status_code=500, detail="Role 'comum' não encontrada. Crie-a primeiro.")
        
    novo_usuario = Usuario(
        nome=dados.nome,
        email=dados.email,
        senha_hash=senha_hash,
        role_id=final_role_id)

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
            dados_dict["senha_hash"] = gerar_hash_senha(dados_dict.pop("senha"))

        for campo, valor in dados_dict.items():

            if hasattr(usuario, campo):
                setattr(usuario, campo, valor)
                
            else:
                print(f"Aviso: Tentativa de atualizar campo '{campo}' que não existe no modelo Usuario.")

        db.add(usuario)
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
