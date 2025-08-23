from sqlalchemy.orm import Session
from .. import models, schemas
import os # Import para manipulação de arquivos/caminhos

# ---------------------- ANEXOS ----------------------

def criar_anexo(db: Session, anexo_info: dict, chamado_id: int, usuario_id: int) -> models.Anexo:
    """
    Cria um novo registro de anexo no banco de dados.
    Nota: Esta função NÃO faz o upload do arquivo, apenas salva os metadados.
    """
    db_anexo = models.Anexo(
        chamado_id=chamado_id,
        usuario_id=usuario_id,
        nome_arquivo_original=anexo_info["nome_arquivo_original"],
        path_arquivo_armazenado=anexo_info["path_arquivo_armazenado"],
        content_type=anexo_info["content_type"],
        tamanho_bytes=anexo_info["tamanho_bytes"]
    )
    db.add(db_anexo)
    db.commit()
    db.refresh(db_anexo)
    return db_anexo

def listar_anexos_por_chamado(db: Session, chamado_id: int) -> list[models.Anexo]:
    """Retorna uma lista de todos os anexos de um chamado específico."""
    return db.query(models.Anexo).filter(models.Anexo.chamado_id == chamado_id).all()

def buscar_anexo_por_id(db: Session, anexo_id: int) -> models.Anexo | None:
    """Busca um anexo específico pelo seu ID."""
    return db.query(models.Anexo).filter(models.Anexo.id == anexo_id).first()

def deletar_anexo(db: Session, anexo_id: int) -> bool:
    """
    Deleta um registro de anexo do banco.
    Nota: A lógica para deletar o arquivo físico do servidor deve ser tratada no endpoint da API.
    """
    db_anexo = buscar_anexo_por_id(db, anexo_id)
    if db_anexo:
        # Aqui você poderia adicionar a lógica para deletar o arquivo físico
        # if os.path.exists(db_anexo.path_arquivo_armazenado):
        #     os.remove(db_anexo.path_arquivo_armazenado)
        
        db.delete(db_anexo)
        db.commit()
        return True
    return False