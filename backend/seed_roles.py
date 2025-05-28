from database import SessionLocal
import backend.cruds.init as init, schemas

def seed_roles():
    db = SessionLocal()
    cargos_iniciais = ["admin", "tecnico", "comum"]

    for nome in cargos_iniciais:
        existing = init.get_role_by_nome(db, nome)
        if not existing:
            role_in = schemas.RoleCreate(nome=nome)
            init.create_role(db, role_in)
            print(f"Criado cargo: {nome}")
        else:
            print(f"Cargo {nome} já existe")
    db.close()

if __name__ == "__main__":
    seed_roles()
