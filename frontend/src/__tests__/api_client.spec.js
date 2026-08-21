import { describe, it, expect, vi, beforeEach } from 'vitest'
import { apiClient, getBaseURL, getAuthHeaders } from '../services/api'

describe('Centralized API Service (services/api.js)', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.restoreAllMocks()
  })

  it('getBaseURL retorna fallback seguro http://localhost:8000 sem trailing slash', () => {
    expect(getBaseURL()).toBe('http://localhost:8000')
  })

  it('getAuthHeaders inclui Authorization Bearer apenas quando token existe', () => {
    expect(getAuthHeaders()).toEqual({})

    localStorage.setItem('token', 'meu_jwt_token_123')
    expect(getAuthHeaders()).toEqual({
      Authorization: 'Bearer meu_jwt_token_123'
    })
  })

  it('apiClient.get executa request com headers dinamicos e retorna dados', async () => {
    localStorage.setItem('token', 'token_dinamico')
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: () => Promise.resolve({ data: 'ok' })
    })

    const res = await apiClient.get('/usuarios/')
    expect(res).toEqual({ data: 'ok' })
    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:8000/usuarios/',
      expect.objectContaining({
        method: 'GET',
        headers: expect.objectContaining({
          Authorization: 'Bearer token_dinamico'
        })
      })
    )
  })

  it('apiClient lanca erro estruturado em status HTTP de falha', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 403,
      json: () => Promise.resolve({ detail: 'Acesso negado a este recurso' })
    })

    await expect(apiClient.get('/admin-only')).rejects.toThrow('Acesso negado a este recurso')
  })

  it('apiClient.download executa download autenticado e revoga blob URL', async () => {
    localStorage.setItem('token', 'token_download')
    const fakeBlob = new Blob(['conteudo anexo'])
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      blob: () => Promise.resolve(fakeBlob)
    })

    const mockCreateObjectURL = vi.fn().mockReturnValue('blob:http://localhost/1234')
    const mockRevokeObjectURL = vi.fn()
    window.URL.createObjectURL = mockCreateObjectURL
    window.URL.revokeObjectURL = mockRevokeObjectURL
    const clickSpy = vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => {})

    await apiClient.download('/anexos/1', 'documento.png')

    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:8000/anexos/1',
      expect.objectContaining({
        headers: expect.objectContaining({
          Authorization: 'Bearer token_download'
        })
      })
    )
    expect(mockCreateObjectURL).toHaveBeenCalled()
    expect(mockRevokeObjectURL).toHaveBeenCalledWith('blob:http://localhost/1234')
    expect(clickSpy).toHaveBeenCalled()
    clickSpy.mockRestore()
  })

  it('apiClient.postPublic envia JSON sem header Authorization', async () => {
    localStorage.setItem('token', 'token_indesejado')
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: () => Promise.resolve({ mensagem: 'Instruções enviadas' })
    })

    const res = await apiClient.postPublic('/recuperar-senha', { email: 'user@test.com' })
    expect(res).toEqual({ mensagem: 'Instruções enviadas' })
    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:8000/recuperar-senha',
      expect.objectContaining({
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: 'user@test.com' })
      })
    )
    const calledHeaders = global.fetch.mock.calls[0][1].headers
    expect(calledHeaders['Authorization']).toBeUndefined()
  })

  it('apiClient.postForm envia formato application/x-www-form-urlencoded para OAuth2 login', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: () => Promise.resolve({ access_token: 'jwt_ok', token_type: 'bearer' })
    })

    const res = await apiClient.postForm('/login', {
      username: 'admin@test.com',
      password: 'SenhaForte123'
    })
    expect(res).toEqual({ access_token: 'jwt_ok', token_type: 'bearer' })
    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:8000/login',
      expect.objectContaining({
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: 'username=admin%40test.com&password=SenhaForte123'
      })
    )
  })
})
