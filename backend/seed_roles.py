import os
from sqlalchemy.orm import Session
from backend.database import SessionLocal, engine, Base
from backend.cruds import usuario as cruds_usuario
from backend.cruds import role as cruds_role
from backend.schemas import UsuarioCreate, RoleCreate
from backend.models import Status, Prioridade, Frequencia, OrigemProblema, Role

# Garante que as tabelas sejam criadas se não existirem
Base.metadata.create_all(bind=engine)

def popular_banco():
    db: Session = SessionLocal()
    print("Iniciando a população do banco de dados...")

    try:
        # 1. Popular Roles
        print("\n--- Populando Roles ---")
        cargos_iniciais = ["admin", "tecnico", "comum"]
        for nome_cargo in cargos_iniciais:
            role_existente = db.query(Role).filter(Role.nome == nome_cargo).first()
            if not role_existente:
                role_schema = RoleCreate(nome=nome_cargo)
                cruds_role.criar_role(db, role_schema)
                print(f"Cargo '{nome_cargo}' criado com sucesso.")
            else:
                print(f"Cargo '{nome_cargo}' já existe.")

        # 2. Popular Status
        print("\n--- Populando Status ---")
        status_iniciais = ["Aberto", "Em Andamento", "Pendente", "Resolvido", "Fechado", "Cancelado"]
        for nome_status in status_iniciais:
            status_existente = db.query(Status).filter(Status.nome == nome_status).first()
            if not status_existente:
                db.add(Status(nome=nome_status))
                print(f"Status '{nome_status}' criado com sucesso.")
            else:
                print(f"Status '{nome_status}' já existe.")

        # 3. Popular Prioridades
        print("\n--- Populando Prioridades ---")
        prioridades_iniciais = ["Baixa", "Média", "Alta", "Urgente"]
        for nome_prioridade in prioridades_iniciais:
            prioridade_existente = db.query(Prioridade).filter(Prioridade.nome == nome_prioridade).first()
            if not prioridade_existente:
                db.add(Prioridade(nome=nome_prioridade))
                print(f"Prioridade '{nome_prioridade}' criada com sucesso.")
            else:
                print(f"Prioridade '{nome_prioridade}' já existe.")

        # 4. Popular Frequências
        print("\n--- Populando Frequências ---")
        frequencias_iniciais = [
            {"nome": "Diária", "dias": 1},
            {"nome": "Semanal", "dias": 7},
            {"nome": "Quinzenal", "dias": 15},
            {"nome": "Mensal", "dias": 30},
        ]
        for freq in frequencias_iniciais:
            frequencia_existente = db.query(Frequencia).filter(Frequencia.nome == freq["nome"]).first()
            if not frequencia_existente:
                db.add(Frequencia(nome=freq["nome"], dias=freq["dias"]))
                print(f"Frequência '{freq['nome']}' criada com sucesso.")
            else:
                print(f"Frequência '{freq['nome']}' já existe.")
        
        # 5. Popular Origens do Problema
        print("\n--- Populando Origens do Problema ---")
        origens_iniciais = ["Telefone", "E-mail", "Sistema de Monitoramento", "Visita Técnica"]
        for nome_origem in origens_iniciais:
            origem_existente = db.query(OrigemProblema).filter(OrigemProblema.nome == nome_origem).first()
            if not origem_existente:
                db.add(OrigemProblema(nome=nome_origem))
                print(f"Origem '{nome_origem}' criada com sucesso.")
            else:
                print(f"Origem '{nome_origem}' já existe.")

        # Commit de todos os dados de referência
        db.commit()

        # 6. Criar Usuário Admin Padrão
        print("\n--- Criando Usuário Admin Padrão ---")

        # --- Cláusula de Guarda 1: Verifica se as variáveis de ambiente existem ---
        EMAIL_ADMIN = os.getenv("ADMIN_EMAIL")
        SENHA_ADMIN = os.getenv("ADMIN_PASSWORD")

        if not EMAIL_ADMIN or not SENHA_ADMIN:
            print("ERRO: As variáveis de ambiente ADMIN_EMAIL e ADMIN_PASSWORD precisam ser definidas. Pulando a criação do admin.")
            return # Retorna da função se as variáveis não estiverem definidas

        # --- Cláusula de Guarda 2: Verifica se o usuário já existe ---
        admin_existente = cruds_usuario.get_usuario_por_email(db, email=EMAIL_ADMIN)
        if admin_existente:
            print(f"Usuário admin padrão '{EMAIL_ADMIN}' já existe.")
            return # Retorna da função se o usuário já foi criado

        # --- Cláusula de Guarda 3: Verifica se o cargo 'admin' existe ---
        admin_role = cruds_role.buscar_role_por_nome(db, nome="admin")
        if not admin_role:
            print("ERRO: Cargo 'admin' não encontrado no banco. Não é possível criar o usuário admin.")
            return # Retorna se o cargo essencial não foi encontrado

        # --- Caminho Feliz: Se todas as verificações passaram, cria o usuário ---
        try:
            usuario_admin_schema = UsuarioCreate(
                nome="Administrador Padrão",
                email=EMAIL_ADMIN,
                senha=SENHA_ADMIN,
                role_id=admin_role.id
            )
            cruds_usuario.criar_usuario(db, usuario_admin_schema)
            print(f"Usuário admin padrão '{EMAIL_ADMIN}' criado com sucesso.")
        except Exception as e:
            print(f"Ocorreu um erro inesperado ao criar o usuário admin: {e}")

    finally:
        db.close()
        print("Sessão do banco de dados fechada.")


if __name__ == "__main__":
    popular_banco()