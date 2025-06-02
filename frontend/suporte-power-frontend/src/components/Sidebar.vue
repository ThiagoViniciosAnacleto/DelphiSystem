<template>
    <aside class="sidebar">
        <nav>
            <ul>
                <li><button>📂 Chamados Abertos</button></li>
                <li><button>➕ Abrir Novo Chamado</button></li>
                <li><button>📋 Lista de Chamados</button></li>
                <li><button>📊 Dashboard</button></li>
                <li><button>🏢 Cadastrar Empresa</button></li>
                <li><button>🛠️ Cadastrar Máquina</button></li>
                <li><button>👤 Cadastrar Usuário</button></li>
                <li><button>✏️ Editar Privilégios</button></li>
                <li><button>♻️ Chamados Recorrentes</button></li>
            </ul>
        </nav>
    </aside>
</template>

<style scoped>
.sidebar {
  width: 220px;
  background-color: #1a1a1a;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  color: #fff;
}

nav ul {
  list-style: none;
  padding: 0;
}

nav li button {
  width: 100%;
  padding: 0.6rem 1rem;
  margin-bottom: 0.4rem;
  background-color: #2c2c2c;
  color: white;
  border: none;
  border-radius: 8px;
  text-align: left;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.2s;
}

nav li button:hover {
  background-color: #3d3d3d;
}
</style>
