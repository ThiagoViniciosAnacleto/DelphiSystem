import pytest

def test_admin_cria_e_gerencia_empresas(client, base_data):
    admin_headers = {'Authorization': f"Bearer {base_data['admin_token']}"}
    res = client.post('/empresas/', json={'nome': 'Nova Empresa Alpha'}, headers=admin_headers)
    assert res.status_code == 201
    empresa_id = res.json()['id']

    res_put = client.put(f'/empresas/{empresa_id}', json={'nome': 'Nova Empresa Beta'}, headers=admin_headers)
    assert res_put.status_code == 200
    assert res_put.json()['nome'] == 'Nova Empresa Beta'

    res_del = client.delete(f'/empresas/{empresa_id}', headers=admin_headers)
    assert res_del.status_code == 200

def test_usuario_comum_bloqueado_em_rotas_administrativas(client, base_data):
    comum_headers = {'Authorization': f"Bearer {base_data['comum_token']}"}

    res1 = client.post('/empresas/', json={'nome': 'Empresa Nao Autorizada'}, headers=comum_headers)
    assert res1.status_code == 403

    res2 = client.post('/maquinas/', json={'modelo': 'Maquina 1'}, headers=comum_headers)
    assert res2.status_code == 403

    res3 = client.post('/prioridades/', json={'nome': 'Urgente'}, headers=comum_headers)
    assert res3.status_code == 403

    res4 = client.post('/frequencias/', json={'nome': 'Semanal'}, headers=comum_headers)
    assert res4.status_code == 403

    res5 = client.get('/logs/', headers=comum_headers)
    assert res5.status_code == 403

def test_admin_acessa_logs(client, base_data):
    admin_headers = {'Authorization': f"Bearer {base_data['admin_token']}"}
    res = client.get('/logs/', headers=admin_headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)
