import pytest
from jose import jwt
from datetime import datetime, timedelta, timezone
from backend.auth import (
    criar_token_acesso,
    criar_token_recuperacao,
    calcular_fingerprint_senha,
    validar_complexidade_senha,
    SECRET_KEY,
    ALGORITHM,
    RESET_AUDIENCE
)

def test_login_sucesso(client, base_data):
    res = client.post('/login', data={'username': 'admin@test.com', 'password': 'SenhaForte123'})
    assert res.status_code == 200
    data = res.json()
    assert 'access_token' in data
    assert data['usuario']['email'] == 'admin@test.com'
    assert data['usuario']['role'] == 'admin'

def test_login_credenciais_invalidas(client, base_data):
    res = client.post('/login', data={'username': 'admin@test.com', 'password': 'SenhaIncorreta'})
    assert res.status_code == 401

def test_segregacao_semantica_token_acesso_e_reset(client, base_data):
    user = base_data['admin_user']
    token_reset = criar_token_recuperacao({'sub': user.email}, senha_hash=user.senha_hash)
    res = client.get('/empresas/', headers={'Authorization': f'Bearer {token_reset}'})
    assert res.status_code == 401

    token_acesso = base_data['admin_token']
    res_reset = client.post('/resetar-senha', json={'token': token_acesso, 'nova_senha': 'NovaSenhaValida123'})
    assert res_reset.status_code in [400, 401]

def test_token_sem_type_ou_audiencia_invalida(client, base_data):
    payload_no_type = {
        'sub': 'admin@test.com',
        'aud': 'delphi_access',
        'exp': datetime.now(timezone.utc) + timedelta(minutes=60)
    }
    raw_token = jwt.encode(payload_no_type, SECRET_KEY, algorithm=ALGORITHM)
    res = client.get('/empresas/', headers={'Authorization': f'Bearer {raw_token}'})
    assert res.status_code == 401

    payload_wrong_aud = {
        'sub': 'admin@test.com',
        'type': 'access',
        'aud': 'outra_aud',
        'exp': datetime.now(timezone.utc) + timedelta(minutes=60)
    }
    raw_token_aud = jwt.encode(payload_wrong_aud, SECRET_KEY, algorithm=ALGORITHM)
    res_aud = client.get('/empresas/', headers={'Authorization': f'Bearer {raw_token_aud}'})
    assert res_aud.status_code == 401

def test_validacao_complexidade_senha():
    valida, motivo = validar_complexidade_senha('Curta1')
    assert not valida
    valida, motivo = validar_complexidade_senha('SemNumerosAqui')
    assert not valida
    valida, motivo = validar_complexidade_senha('123456789')
    assert not valida
    valida, motivo = validar_complexidade_senha('SenhaValida123')
    assert valida

def test_recuperacao_senha_sem_enumeracao(client, base_data):
    res1 = client.post('/recuperar-senha', json={'email': 'admin@test.com'})
    assert res1.status_code == 200

    res2 = client.post('/recuperar-senha', json={'email': 'inexistente@naoexiste.com'})
    assert res2.status_code == 200
    assert res1.json() == res2.json()

def test_redefinicao_senha_fluxo_completo_e_rejeicao_de_replay(client, base_data):
    user = base_data['admin_user']
    token_reset = criar_token_recuperacao({'sub': user.email}, senha_hash=user.senha_hash)

    # Verifica que o payload contém fingerprint HMAC opaco de 64 caracteres e NÃO vaza bcrypt
    decoded_payload = jwt.decode(token_reset, SECRET_KEY, algorithms=[ALGORITHM], audience=RESET_AUDIENCE)
    pwh_claim = decoded_payload.get('pwh')
    assert len(pwh_claim) == 64
    assert '$2b$' not in pwh_claim
    assert '$2a$' not in pwh_claim
    assert user.senha_hash[:16] not in pwh_claim

    # 1. Primeira redefinição: sucesso
    res = client.post('/resetar-senha', json={'token': token_reset, 'nova_senha': 'MinhaNovaSenhaForte88'})
    assert res.status_code == 200

    # 2. Login com a nova senha: sucesso
    res_login = client.post('/login', data={'username': user.email, 'password': 'MinhaNovaSenhaForte88'})
    assert res_login.status_code == 200

    # 3. Tentativa de replay do mesmo token de recuperação: DEVE FALHAR (400)
    res_replay = client.post('/resetar-senha', json={'token': token_reset, 'nova_senha': 'TentativaReplay123'})
    assert res_replay.status_code == 400
    assert 'utilizado' in res_replay.json().get('detail', '').lower() or 'inválido' in res_replay.json().get('detail', '').lower()

def test_redefinicao_senha_sem_fingerprint_deve_falhar(client, base_data):
    user = base_data['admin_user']
    payload_no_pwh = {
        'sub': user.email,
        'type': 'password_reset',
        'aud': RESET_AUDIENCE,
        'exp': datetime.now(timezone.utc) + timedelta(minutes=30)
    }
    raw_token = jwt.encode(payload_no_pwh, SECRET_KEY, algorithm=ALGORITHM)
    res = client.post('/resetar-senha', json={'token': raw_token, 'nova_senha': 'NovaSenhaValida123'})
    assert res.status_code == 400
