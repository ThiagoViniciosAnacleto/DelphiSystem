from fastapi.testclient import TestClient
from backend.main import app

# Cria um cliente de teste que simula um navegador/usuário
client = TestClient(app)

def test_listar_empresas_sem_token_deve_falhar():
    """
    Testa a segurança da rota de listar empresas.
    Como não estamos enviando um token JWT de login, a API DEVE bloquear
    o acesso e retornar o status 401 (Unauthorized).
    """
    response = client.get("/empresas/")

    # Valida se o status da resposta é 401
    assert response.status_code == 401

    # Valida se o sistema retorna a mensagem de erro padrão
    assert response.json() == {"detail": "Not authenticated"}
