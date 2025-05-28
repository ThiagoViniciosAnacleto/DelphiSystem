from database import SessionLocal
import backend.cruds as cruds, schemas

def seed_roles():
    db = SessionLocal()
    cargos_iniciais = ["admin", "tecnico", "comum"]

    for nome in cargos_iniciais:
        existing = cruds.get_role_by_nome(db, nome)
        if not existing:
            role_in = schemas.RoleCreate(nome=nome)
            cruds.create_role(db, role_in)
            print(f"Criado cargo: {nome}")
        else:
            print(f"Cargo {nome} já existe")
    db.close()

if __name__ == "__main__":
    seed_roles()
