import pytest

def test_criar_chamado_com_campos_opcionais_e_obrigatorios(client, base_data):
    headers = {'Authorization': f"Bearer {base_data['comum_token']}"}
    payload = {
        'contato': 'Cliente Teste',
        'empresa_id': base_data['empresa'].id,
        'relato': 'Problema no equipamento',
        'prioridade_id': base_data['prioridade_alta'].id,
        'status_id': base_data['status_aberto'].id
    }
    res = client.post('/chamados/', json=payload, headers=headers)
    assert res.status_code == 201
    data = res.json()
    assert data['contato'] == 'Cliente Teste'
    assert data['empresa']['nome'] == 'Empresa Teste'
    assert data['prioridade']['nome'] == 'Alta'
    assert data['status']['nome'] == 'Aberto'

def test_filtrar_chamados_por_prioridade_e_status(client, base_data):
    headers = {'Authorization': f"Bearer {base_data['admin_token']}"}

    # Cria chamado com prioridade alta
    client.post('/chamados/', json={
        'contato': 'Cliente Alta',
        'empresa_id': base_data['empresa'].id,
        'relato': 'Problema urgente',
        'prioridade_id': base_data['prioridade_alta'].id,
        'status_id': base_data['status_aberto'].id
    }, headers=headers)

    # Cria chamado com prioridade baixa
    client.post('/chamados/', json={
        'contato': 'Cliente Baixa',
        'empresa_id': base_data['empresa'].id,
        'relato': 'Problema leve',
        'prioridade_id': base_data['prioridade_baixa'].id,
        'status_id': base_data['status_aberto'].id
    }, headers=headers)

    # Filtra por prioridade alta
    res_alta = client.get(f"/chamados/?prioridade_id={base_data['prioridade_alta'].id}", headers=headers)
    assert res_alta.status_code == 200
    chamados_alta = res_alta.json()
    assert all(c['prioridade']['id'] == base_data['prioridade_alta'].id for c in chamados_alta)

def test_privacidade_comentarios_para_roles(client, base_data):
    admin_headers = {'Authorization': f"Bearer {base_data['admin_token']}"}
    comum_headers = {'Authorization': f"Bearer {base_data['comum_token']}"}

    # Usuário comum cria seu chamado
    res_ch = client.post('/chamados/', json={
        'contato': 'Cliente Teste Privacidade',
        'empresa_id': base_data['empresa'].id,
        'relato': 'Relato inicial'
    }, headers=comum_headers)
    chamado_id = res_ch.json()['id']


    # Admin adiciona comentário privado
    res_priv = client.post(f'/chamados/{chamado_id}/interacoes/', json={
        'comentario': 'Nota interna confidencial',
        'privado': True
    }, headers=admin_headers)
    assert res_priv.status_code == 201

    # Admin adiciona comentário público
    res_pub = client.post(f'/chamados/{chamado_id}/interacoes/', json={
        'comentario': 'Nota pública visível',
        'privado': False
    }, headers=admin_headers)
    assert res_pub.status_code == 201

    # Admin visualiza todos
    res_admin_view = client.get(f'/chamados/{chamado_id}', headers=admin_headers)
    interacoes_admin = res_admin_view.json()['interacoes']
    assert len(interacoes_admin) == 2

    # Usuário comum visualiza apenas público
    res_comum_view = client.get(f'/chamados/{chamado_id}', headers=comum_headers)
    interacoes_comum = res_comum_view.json()['interacoes']
    assert len(interacoes_comum) == 1
    assert interacoes_comum[0]['comentario'] == 'Nota pública visível'

def test_dashboard_metricas(client, base_data):
    headers = {'Authorization': f"Bearer {base_data['admin_token']}"}
    res_basico = client.get('/dashboard/basico', headers=headers)
    assert res_basico.status_code == 200
    assert isinstance(res_basico.json(), dict)

    res_avancado = client.get('/dashboard/avancado', headers=headers)
    assert res_avancado.status_code == 200
    assert 'por_empresa' in res_avancado.json()
    assert 'ultimos_7_dias' in res_avancado.json()

def test_autorizacao_por_recurso_idor_cruzado(client, base_data):
    comum1_headers = {'Authorization': f"Bearer {base_data['comum1_token']}"}
    comum2_headers = {'Authorization': f"Bearer {base_data['comum2_token']}"}
    admin_headers = {'Authorization': f"Bearer {base_data['admin_token']}"}
    tecnico_headers = {'Authorization': f"Bearer {base_data['tecnico_token']}"}

    # 1. comum1 cria Chamado 1
    res1 = client.post('/chamados/', json={
        'contato': 'Contato Comum 1',
        'empresa_id': base_data['empresa'].id,
        'relato': 'Chamado de Comum 1'
    }, headers=comum1_headers)
    assert res1.status_code == 201
    id1 = res1.json()['id']
    assert res1.json()['criado_por_id'] == base_data['comum1_user'].id

    # 2. comum2 cria Chamado 2
    res2 = client.post('/chamados/', json={
        'contato': 'Contato Comum 2',
        'empresa_id': base_data['empresa'].id,
        'relato': 'Chamado de Comum 2'
    }, headers=comum2_headers)
    assert res2.status_code == 201
    id2 = res2.json()['id']
    assert res2.json()['criado_por_id'] == base_data['comum2_user'].id

    # 3. Filtragem de Listagem: comum1 só vê id1; comum2 só vê id2
    list_comum1 = client.get('/chamados/', headers=comum1_headers).json()
    assert any(c['id'] == id1 for c in list_comum1)
    assert not any(c['id'] == id2 for c in list_comum1)

    list_comum2 = client.get('/chamados/', headers=comum2_headers).json()
    assert any(c['id'] == id2 for c in list_comum2)
    assert not any(c['id'] == id1 for c in list_comum2)

    # 4. Admin e Técnico conseguem listar ambos
    list_admin = client.get('/chamados/', headers=admin_headers).json()
    assert any(c['id'] == id1 for c in list_admin) and any(c['id'] == id2 for c in list_admin)
    list_tecnico = client.get('/chamados/', headers=tecnico_headers).json()
    assert any(c['id'] == id1 for c in list_tecnico) and any(c['id'] == id2 for c in list_tecnico)

    # 5. Tentativas de acesso cruzado direto de comum2 no chamado id1 -> 403 Forbidden
    assert client.get(f'/chamados/{id1}', headers=comum2_headers).status_code == 403
    assert client.put(f'/chamados/{id1}', json={'contato': 'Hacked'}, headers=comum2_headers).status_code == 403
    assert client.get(f'/chamados/{id1}/timeline', headers=comum2_headers).status_code == 403
    assert client.get(f'/chamados/{id1}/interacoes/', headers=comum2_headers).status_code == 403
    assert client.post(f'/chamados/{id1}/interacoes/', json={'comentario': 'Invasao'}, headers=comum2_headers).status_code == 403
    assert client.get(f'/chamados/{id1}/anexos/', headers=comum2_headers).status_code == 403
