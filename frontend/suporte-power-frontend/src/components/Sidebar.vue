<template>
  <aside class="sidebar">
    <nav>
      <ul>
        <li>
          <button type="button">📂 Chamados Abertos</button>
        </li>

        <li>
          <router-link to="/criar-chamados">
            <button type="button">➕ Abrir Novo Chamado</button>
          </router-link>
        </li>

        <li>
          <router-link to="/lista-chamados">
            <button type="button">📋 Lista de Chamados</button>
          </router-link>
        </li>

        <li>
          <router-link to="/dashboard">
            <button type="button">📊 Dashboard</button>
          </router-link>
        </li>

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
          <router-link to="/cadastrar-usuario">
            <button type="button">👤 Cadastrar Usuário</button>
          </router-link>
        </li>

        <li>
          <router-link to="/editar-privilegios">
            <button type="button">✏️ Editar Privilégios</button>
          </router-link>
        </li>

        <li>
          <router-link to="/chamados-recorrentes">
            <button type="button">♻️ Chamados Recorrentes</button>
          </router-link>
        </li>
      </ul>
    </nav>
  </aside>
</template>

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

