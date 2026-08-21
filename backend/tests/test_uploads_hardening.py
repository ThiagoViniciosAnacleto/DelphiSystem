import pytest
import io

def test_upload_anexo_valido_e_download_com_magic_bytes(client, base_data):
    headers = {'Authorization': f"Bearer {base_data['admin_token']}"}

    # Cria chamado
    res_ch = client.post('/chamados/', json={
        'contato': 'Cliente Teste Anexo',
        'empresa_id': base_data['empresa'].id,
        'relato': 'Relato anexo'
    }, headers=headers)
    chamado_id = res_ch.json()['id']

    # 1. Upload de PNG com magic bytes válidos
    png_content = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
    files_png = {'file': ('documento.png', io.BytesIO(png_content), 'image/png')}
    res_png = client.post(f'/chamados/{chamado_id}/anexos/', files=files_png, headers=headers)
    assert res_png.status_code == 201
    anexo_png_id = res_png.json()['id']

    # 2. Upload de PDF com magic bytes válidos
    pdf_content = b"%PDF-1.4 header test"
    files_pdf = {'file': ('manual.pdf', io.BytesIO(pdf_content), 'application/pdf')}
    res_pdf = client.post(f'/chamados/{chamado_id}/anexos/', files=files_pdf, headers=headers)
    assert res_pdf.status_code == 201
    anexo_pdf_id = res_pdf.json()['id']

    # 3. Upload de TXT válido
    txt_content = b"Texto explicativo simples"
    files_txt = {'file': ('info.txt', io.BytesIO(txt_content), 'text/plain')}
    res_txt = client.post(f'/chamados/{chamado_id}/anexos/', files=files_txt, headers=headers)
    assert res_txt.status_code == 201

    # Download do anexo PNG
    res_download = client.get(f'/anexos/{anexo_png_id}', headers=headers)
    assert res_download.status_code == 200
    assert res_download.content == png_content

def test_upload_anexo_extensao_proibida(client, base_data):
    headers = {'Authorization': f"Bearer {base_data['admin_token']}"}

    res_ch = client.post('/chamados/', json={
        'contato': 'Cliente Teste Anexo Invalido',
        'empresa_id': base_data['empresa'].id,
        'relato': 'Relato'
    }, headers=headers)
    chamado_id = res_ch.json()['id']

    file_obj = io.BytesIO(b"echo 'malicious script'")
    files = {'file': ('script.sh', file_obj, 'application/x-sh')}

    res_upload = client.post(f'/chamados/{chamado_id}/anexos/', files=files, headers=headers)
    assert res_upload.status_code == 400

def test_upload_anexo_magic_bytes_incompativeis(client, base_data):
    headers = {'Authorization': f"Bearer {base_data['admin_token']}"}

    res_ch = client.post('/chamados/', json={
        'contato': 'Cliente Teste Assinatura Falsa',
        'empresa_id': base_data['empresa'].id,
        'relato': 'Relato'
    }, headers=headers)
    chamado_id = res_ch.json()['id']

    # Arquivo com extensão .png mas contendo script ou executável
    corrupted_file = io.BytesIO(b"MZ\x90\x00 executavel falso")
    files = {'file': ('malware_disfarçado.png', corrupted_file, 'image/png')}

    res_upload = client.post(f'/chamados/{chamado_id}/anexos/', files=files, headers=headers)
    assert res_upload.status_code == 400
    assert 'incompatível' in res_upload.json().get('detail', '').lower()

def test_anexo_download_e_upload_idor_cruzado(client, base_data):
    comum1_headers = {'Authorization': f"Bearer {base_data['comum1_token']}"}
    comum2_headers = {'Authorization': f"Bearer {base_data['comum2_token']}"}
    admin_headers = {'Authorization': f"Bearer {base_data['admin_token']}"}

    # comum1 cria Chamado
    res_ch1 = client.post('/chamados/', json={
        'contato': 'Comum 1',
        'empresa_id': base_data['empresa'].id,
        'relato': 'Chamado 1 com anexo'
    }, headers=comum1_headers)
    ch1_id = res_ch1.json()['id']

    # comum1 faz upload no seu chamado
    png_content = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
    files = {'file': ('anexo1.png', io.BytesIO(png_content), 'image/png')}
    res_up1 = client.post(f'/chamados/{ch1_id}/anexos/', files=files, headers=comum1_headers)
    assert res_up1.status_code == 201
    anexo_id = res_up1.json()['id']

    # comum2 tenta fazer upload no chamado de comum1 -> 403
    files2 = {'file': ('invasao.png', io.BytesIO(png_content), 'image/png')}
    assert client.post(f'/chamados/{ch1_id}/anexos/', files=files2, headers=comum2_headers).status_code == 403

    # comum2 tenta baixar anexo de comum1 -> 403
    assert client.get(f'/anexos/{anexo_id}', headers=comum2_headers).status_code == 403

    # comum2 tenta deletar anexo de comum1 -> 403
    assert client.delete(f'/anexos/{anexo_id}', headers=comum2_headers).status_code == 403

    # Sem autenticação -> 401
    assert client.get(f'/anexos/{anexo_id}').status_code == 401

    # Admin e comum1 conseguem baixar
    assert client.get(f'/anexos/{anexo_id}', headers=comum1_headers).status_code == 200
    assert client.get(f'/anexos/{anexo_id}', headers=admin_headers).status_code == 200
