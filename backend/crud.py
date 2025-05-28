from sqlalchemy.orm import Session
from models import Usuario, Role, Empresa, Maquina, OrigemProblema, Chamado, LogAcao
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ----- Usuários -----
def get_usuario(db: Session, usuario_id: int):
    return db.query(Usuario).filter(Usuario.id == usuario_id).first()

def get_usuario_por_email(db: Session, email: str):
    return db.query(Usuario).filter(Usuario.email == email).first()

def listar_usuarios(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Usuario).offset(skip).limit(limit).all()

def criar_usuario(db: Session, nome: str, email: str, senha: str, role_id: int):
    senha_hash = pwd_context.hash(senha)
    db_usuario = Usuario(nome=nome, email=email, senha_hash=senha_hash, role_id=role_id)
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

def atualizar_usuario(db: Session, usuario_id: int, nome: str = None, email: str = None, senha: str = None, role_id: int = None):
    usuario = get_usuario(db, usuario_id)
    if not usuario:
        return None
    if nome:
        usuario.nome = nome
    if email:
        usuario.email = email
    if senha:
        usuario.senha_hash = pwd_context.hash(senha)
    if role_id is not None:
        usuario.role_id = role_id
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


# ----- Roles (Cargos) -----
def get_roles(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Role).offset(skip).limit(limit).all()

def get_role(db: Session, role_id: int):
    return db.query(Role).filter(Role.id == role_id).first()

def get_role_by_nome(db: Session, nome: str):
    return db.query(Role).filter(Role.nome == nome).first()

def create_role(db: Session, role_in):
    db_role = Role(nome=role_in.nome)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

def update_role(db: Session, role_id: int, role_in):
    db_role = get_role(db, role_id)
    if not db_role:
        return None
    db_role.nome = role_in.nome
    db.commit()
    db.refresh(db_role)
    return db_role

def delete_role(db: Session, role_id: int):
    db_role = get_role(db, role_id)
    if not db_role:
        return None
    db.delete(db_role)
    db.commit()
    return db_role


# ----- Empresas -----
def get_empresa(db: Session, empresa_id: int):
    return db.query(Empresa).filter(Empresa.id == empresa_id).first()

def listar_empresas(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Empresa).offset(skip).limit(limit).all()

def criar_empresa(db: Session, nome: str):
    db_empresa = Empresa(nome=nome)
    db.add(db_empresa)
    db.commit()
    db.refresh(db_empresa)
    return db_empresa

def atualizar_empresa(db: Session, empresa_id: int, nome: str):
    empresa = get_empresa(db, empresa_id)
    if not empresa:
        return None
    empresa.nome = nome
    db.commit()
    db.refresh(empresa)
    return empresa

def deletar_empresa(db: Session, empresa_id: int):
    empresa = get_empresa(db, empresa_id)
    if not empresa:
        return None
    db.delete(empresa)
    db.commit()
    return empresa

# ----- Máquinas -----
# Similar ao acima para Maquina (get, listar, criar, atualizar, deletar)

# ----- Origens de Problema -----
# Similar ao acima para OrigemProblema (get, listar, criar, atualizar, deletar)

# ----- Chamados -----
def get_chamado(db: Session, chamado_id: int):
    return db.query(Chamado).filter(Chamado.id == chamado_id).first()

def listar_chamados(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Chamado).offset(skip).limit(limit).all()

def criar_chamado(db: Session, **kwargs):
    chamado = Chamado(**kwargs)
    db.add(chamado)
    db.commit()
    db.refresh(chamado)
    return chamado

def atualizar_chamado(db: Session, chamado_id: int, **kwargs):
    chamado = get_chamado(db, chamado_id)
    if not chamado:
        return None
    for key, value in kwargs.items():
        setattr(chamado, key, value)
    db.commit()
    db.refresh(chamado)
    return chamado

def deletar_chamado(db: Session, chamado_id: int):
    chamado = get_chamado(db, chamado_id)
    if not chamado:
        return None
    db.delete(chamado)
    db.commit()
    return chamado

# ----- Logs de ações -----
def registrar_log(db: Session, usuario_id: int, acao: str, chamado_id: int = None, tipo: str = None, campo: str = None, valor_antigo: str = None, valor_novo: str = None):
    log = LogAcao(
        usuario_id=usuario_id,
        acao=acao,
        chamado_id=chamado_id,
        tipo=tipo,
        campo=campo,
        valor_antigo=valor_antigo,
        valor_novo=valor_novo,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log
