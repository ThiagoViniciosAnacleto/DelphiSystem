<template>
    <div class="maquinas">
        <h2>Máquinas</h2>

        <form @submit.prevent="salvarMaquina">
            <input
                v-model="novaMaquina.modelo"
                placeholder="Modelo da máquina"
                required
            />
            <select v-model="novaMaquina.empresa_id" required>
                <option disabled value="">Selecione a empresa</option>
                <option v-for="e in empresas" :key="e.id" :value="e.id">
                {{ e.nome }}
                </option>
            </select>

            <button type="submit">
                {{ editandoId ? "Atualizar" : "Salvar" }}
            </button>
        </form>

        <hr />

        <h3>Máquinas Cadastradas</h3>
        <ul>
            <li v-for="m in maquinas" :key="m.id">
                <span>{{ m.modelo }} — {{ nomeEmpresa(m.empresa_id) }}</span>

            <div class="acoes">
                <button @click="editar(m)">✏️</button>
                <button @click="deletar(m.id)">🗑️</button>
            </div>
            </li>
        </ul>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const maquinas = ref([])
const empresas = ref([])
const novaMaquina = ref({ modelo: '', empresa_id: '' })
const editandoId = ref(null)

const baseURL = import.meta.env.VITE_API_URL.replace(/\/$/, '')
const headers = {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${localStorage.getItem('token')}`
}

// Carrega empresas
const carregarEmpresas = async () => {
    const res = await fetch(`${baseURL}/empresas/`, { headers })
    empresas.value = await res.json()
}

// Carrega máquinas
const carregarMaquinas = async () => {
    const res = await fetch(`${baseURL}/maquinas/`, { headers })
    maquinas.value = await res.json()
}

// Cria ou edita
const salvarMaquina = async () => {
    const url = editandoId.value
        ? `${baseURL}/maquinas/${editandoId.value}`
        : `${baseURL}/maquinas/`

    const method = editandoId.value ? 'PUT' : 'POST'

    await fetch(url, {
        method,
        headers,
        body: JSON.stringify(novaMaquina.value)
    })

    resetarFormulario()
    carregarMaquinas()
}

const editar = (maquina) => {
    novaMaquina.value = {
    modelo: maquina.modelo,
    empresa_id: maquina.empresa_id
    }
    editandoId.value = maquina.id
}

const deletar = async (id) => {
    if (confirm('Deseja desativar esta máquina?')) {
    await fetch(`${baseURL}/maquinas/${id}`, {
        method: 'DELETE',
        headers
    })
    carregarMaquinas()
    }
}

const nomeEmpresa = (id) => {
    const empresa = empresas.value.find(e => e.id === id)
    return empresa ? empresa.nome : 'Desconhecida'
}

const resetarFormulario = () => {
    novaMaquina.value = { modelo: '', empresa_id: '' }
    editandoId.value = null
}

onMounted(() => {
    carregarEmpresas()
    carregarMaquinas()
})
</script>

<style scoped>
.maquinas {
    max-width: 700px;
    margin: 40px auto;
    padding: 20px;
    background: #f8f9fa;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
    font-family: 'Segoe UI', sans-serif;
}

h2, h3 {
    margin-bottom: 16px;
    color: #1a1a1a;
}

form {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
    flex-wrap: wrap;
}

input, select {
    flex: 1;
    padding: 10px;
    border: 1px solid #ccc;
    border-radius: 8px;
    font-size: 16px;
    min-width: 250px;
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

button[type="submit"] {
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
