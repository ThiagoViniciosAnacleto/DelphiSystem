import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import Sidebar from '../components/Sidebar.vue'

describe('Sidebar.vue Component', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('exibe links administrativos quando usuario e admin', () => {
    localStorage.setItem('usuario', JSON.stringify({ email: 'admin@test.com', role: 'admin' }))
    const wrapper = mount(Sidebar, {
      global: {
        stubs: {
          'router-link': {
            template: '<a><slot /></a>'
          }
        }
      }
    })
    expect(wrapper.text()).toContain('Cadastrar Empresa')
    expect(wrapper.text()).toContain('Cadastrar Usuário')
    expect(wrapper.text()).toContain('Administração')
  })

  it('oculta links administrativos para usuario comum', () => {
    localStorage.setItem('usuario', JSON.stringify({ email: 'comum@test.com', role: 'comum' }))
    const wrapper = mount(Sidebar, {
      global: {
        stubs: {
          'router-link': {
            template: '<a><slot /></a>'
          }
        }
      }
    })
    expect(wrapper.text()).toContain('Lista de Chamados')
    expect(wrapper.text()).not.toContain('Cadastrar Empresa')
    expect(wrapper.text()).not.toContain('Cadastrar Usuário')
  })

})
