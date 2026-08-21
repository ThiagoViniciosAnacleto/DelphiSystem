import { describe, it, expect, beforeEach } from 'vitest'
import router from '../router/index.js'

describe('Router Navigation Guards', () => {
  beforeEach(async () => {
    localStorage.clear()
    try {
      await router.push('/login')
    } catch {}
  })

  it('redireciona usuario nao autenticado de rota protegida para /login', async () => {
    await router.push('/dashboard')
    expect(router.currentRoute.value.path).toBe('/login')
  })

  it('redireciona usuario autenticado de rota publica para /dashboard', async () => {
    localStorage.setItem('token', 'fake-token-jwt')
    localStorage.setItem('usuario', JSON.stringify({ email: 'user@test.com', role: 'comum' }))

    await router.push('/recuperar-senha')
    expect(router.currentRoute.value.path).toBe('/dashboard')
  })


  it('bloqueia rota administrativa para usuario comum e redireciona para /dashboard', async () => {
    localStorage.setItem('token', 'fake-token-jwt')
    localStorage.setItem('usuario', JSON.stringify({ email: 'user@test.com', role: 'comum' }))

    await router.push('/cadastrar-usuario')
    expect(router.currentRoute.value.path).toBe('/dashboard')
  })

  it('permite acesso a rota administrativa para usuario admin', async () => {
    localStorage.setItem('token', 'fake-admin-token')
    localStorage.setItem('usuario', JSON.stringify({ email: 'admin@test.com', role: 'admin' }))

    await router.push('/cadastrar-usuario')
    expect(router.currentRoute.value.path).toBe('/cadastrar-usuario')
  })
})
