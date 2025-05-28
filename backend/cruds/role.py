from sqlalchemy.orm import Session
from models import Role
from schemas import RoleCreate, RoleUpdate


def criar_role(db: Session, dados: RoleCreate) -> Role:
    nova_role = Role(**dados.model_dump())
    db.add(nova_role)
    db.commit()
    db.refresh(nova_role)
    return nova_role


def listar_roles(db: Session) -> list[Role]:
    return db.query(Role).filter(Role.ativo == True).all()


def buscar_role_por_id(db: Session, role_id: int) -> Role | None:
    return db.query(Role).filter(Role.id == role_id, Role.ativo == True).first()


def atualizar_role(
    db: Session, role_id: int, dados: RoleUpdate
) -> Role | None:
    role = db.query(Role).filter(Role.id == role_id, Role.ativo == True).first()
    if role:
        for campo, valor in dados.model_dump(exclude_unset=True).items():
            setattr(role, campo, valor)
        db.commit()
        db.refresh(role)
        return role
    return None


def deletar_role(db: Session, role_id: int) -> bool:
    role = db.query(Role).filter(Role.id == role_id, Role.ativo == True).first()
    if role:
        role.ativo = False
        db.commit()
        return True
    return False
