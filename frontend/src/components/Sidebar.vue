<template>
  <aside class="sidebar">
    <nav>
      <ul>
        <li>
          <router-link to="/lista-chamados">
            <button type="button">📋 Lista de Chamados</button>
          </router-link>
        </li>

        <li>
          <router-link to="/criar-chamados">
            <button type="button">➕ Abrir Novo Chamado</button>
          </router-link>
        </li>

        <li>
          <router-link to="/dashboard">
            <button type="button">📊 Dashboard</button>
          </router-link>
        </li>

        <template v-if="isAdmin">
          <li class="nav-divider"><span>Administração</span></li>

          <li>
            <router-link to="/cadastrar-empresa">
              <button type="button">🏢 Cadastrar Empresa</button>
            </router-link>
          </li>

          <li>
            <router-link to="/cadastrar-maquina">
              <button type="button">🛠️ Cadastrar Máquina</button>
            </router-link>
          </li>

          <li>
            <router-link to="/criar-origem-problema">
              <button type="button">🛠️ Criar Origem Problema</button>
            </router-link>
          </li>

          <li>
            <router-link to="/cadastrar-prioridade">
              <button type="button">🛠️ Cadastrar Prioridade</button>
            </router-link>
          </li>

          <li>
            <router-link to="/cadastrar-status">
              <button type="button">🛠️ Cadastrar Status</button>
            </router-link>
          </li>

          <li>
            <router-link to="/cadastrar-usuario">
              <button type="button">👤 Cadastrar Usuário</button>
            </router-link>
          </li>

          <li>
            <router-link to="/chamados-recorrentes">
              <button type="button">♻️ Chamados Recorrentes</button>
            </router-link>
          </li>
        </template>
      </ul>
    </nav>
  </aside>
</template>

<script setup>
import { computed } from 'vue'

const usuario = computed(() => {
  try {
    const data = localStorage.getItem('usuario')
    return data ? JSON.parse(data) : null
  } catch {
    return null
  }
})

const isAdmin = computed(() => {
  if (!usuario.value) return false
  const roleName = typeof usuario.value.role === 'string' ? usuario.value.role : usuario.value.role?.nome
  return roleName === 'admin'
})
</script>

<style scoped>
.sidebar {
  background-color: #f8f9fa;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  color: #212529;
  height: 100%;
  border-right: 1px solid #dee2e6;
}

nav ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.nav-divider {
  padding: 8px 4px 4px 4px;
  font-size: 11px;
  font-weight: bold;
  text-transform: uppercase;
  color: #888;
  letter-spacing: 0.5px;
}

nav li button {
  width: 100%;
  padding: 0.6rem 1rem;
  margin-bottom: 0.4rem;
  background-color: #e9ecef;
  color: #212529;
  border: none;
  border-radius: 8px;
  text-align: left;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.2s;
}

nav li button:hover {
  background-color: #dee2e6;
}
</style>
