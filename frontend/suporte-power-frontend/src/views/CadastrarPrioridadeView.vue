<template>
  <div class="prioridades">
    <h2>Cadastrar Níveis de Prioridade</h2>

    <form @submit.prevent="salvarPrioridade">
      <input v-model="novaPrioridade.nome" placeholder="Nome da prioridade" required />
      <button type="submit">
        {{ editandoId ? "Atualizar" : "Salvar" }}
      </button>
    </form>

    <hr />

    <h3>Prioridades Cadastradas</h3>

    <ul>
      <li v-for="p in prioridades" :key="p.id">
        <span>{{ p.nome }}</span>
        <div class="acoes">
          <button @click="editar(p)">✏️</button>
          <button @click="deletar(p.id)">🗑️</button>
        </div>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const prioridades = ref([])
const novaPrioridade = ref({ nome: '' })
const editandoId = ref(null)

const baseURL = import.meta.env.VITE_API_URL.replace(/\/$/, '')
const headers = {
  'Content-Type': 'application/json',
  Authorization: `Bearer ${localStorage.getItem('token')}`
}

const carregarPrioridades = async () => {
  try {
    const res = await fetch(`${baseURL}/prioridades/`, { headers })
    prioridades.value = await res.json()
  } catch (err) {
    console.error('Erro ao carregar prioridades:', err)
  }
}

const salvarPrioridade = async () => {
  const url = editandoId.value
    ? `${baseURL}/prioridades/${editandoId.value}`
    : `${baseURL}/prioridades/`

  const method = editandoId.value ? 'PUT' : 'POST'

  await fetch(url, {
    method,
    headers,
    body: JSON.stringify(novaPrioridade.value)
  })

  resetarFormulario()
  carregarPrioridades()
}

const editar = (prioridade) => {
  novaPrioridade.value = { nome: prioridade.nome }
  editandoId.value = prioridade.id
}

const deletar = async (id) => {
  if (confirm('Deseja desativar esta prioridade?')) {
    await fetch(`${baseURL}/prioridades/${id}`, {
      method: 'DELETE',
      headers
    })
    carregarPrioridades()
  }
}

const resetarFormulario = () => {
  novaPrioridade.value = { nome: '' }
  editandoId.value = null
}

onMounted(carregarPrioridades)
</script>

<style scoped>
.prioridades {
  max-width: 700px;
  margin: 40px auto;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
  font-family: 'Segoe UI', sans-serif;
}

h2,
h3 {
  margin-bottom: 16px;
  color: #1a1a1a;
}

form {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 8px;
  font-size: 16px;
}

button {
  padding: 10px 14px;
  font-size: 16px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: 0.2s;
}

button:hover {
  filter: brightness(1.1);
}

button[type='submit'] {
  background-color: #2d88ff;
  color: #fff;
}

ul {
  list-style: none;
  padding: 0;
}

li {
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 10px;
  padding: 12px 16px;
  margin-bottom: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.acoes button {
  margin-left: 8px;
}

.acoes button:first-child {
  background-color: #ffeb3b;
}

.acoes button:last-child {
  background-color: #e74c3c;
  color: white;
}
</style>
