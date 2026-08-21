import { describe, it, expect, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import DetalheChamadoView from '../views/DetalheChamadoView.vue'

// Mock global fetch e route
global.fetch = vi.fn((url) => {
  if (url.includes('/chamados/1/timeline')) {
    return Promise.resolve({
      ok: true,
      json: () => Promise.resolve([])
    })
  }
  return Promise.resolve({
    ok: true,
    json: () => Promise.resolve({
      id: 1,
      contato: 'Cliente Teste',
      relato: 'Descrição teste',
      interacoes: [],
      anexos: [],
      empresa: { id: 1, nome: 'Empresa Teste' }
    }),
  })
})

vi.mock('vue-router', () => ({
  useRoute: () => ({ params: { id: '1' } }),
  useRouter: () => ({ push: vi.fn() }),
}))

describe('DetalheChamadoView.vue Component', () => {
  it('monta o componente com campos acessiveis e sem marcadores de conflito git', async () => {
    const wrapper = mount(DetalheChamadoView, {
      global: {
        stubs: {
          'router-link': {
            template: '<a><slot /></a>'
          }
        }
      }
    })

    await flushPromises()

    expect(wrapper.find('.detalhe-chamado-container').exists()).toBe(true)
    expect(wrapper.text()).toContain('Chamado #1: Cliente Teste')
    expect(wrapper.html()).not.toContain('<<' + '<<<<<')
    expect(wrapper.html()).not.toContain('>>' + '>>>>>')
  })
})
