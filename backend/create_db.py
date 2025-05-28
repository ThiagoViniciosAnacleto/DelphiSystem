from database import Base, engine
from models import *  # importa todas as tabelas

print("Criando tabelas no banco de dados...")
Base.metadata.create_all(bind=engine)
print("Tabelas criadas com sucesso.")
