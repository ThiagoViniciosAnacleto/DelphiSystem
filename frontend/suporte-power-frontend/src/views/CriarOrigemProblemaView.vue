<template>
    <div class="origens">
        <h2>Origens do Problema</h2>

        <form @submit.prevent="salvarOrigem">
            <input v-model="novaOrigem.nome" placeholder="Nome da origem" required />
            <button type="submit">
                {{ editandoId ? "Atualizar" : "Salvar" }}
            </button>
        </form>

        <hr />

        <h3>Origens Cadastradas</h3>

        <ul>
            <li v-for="o in origens" :key="o.id">
                <span>{{ o.nome }}</span>
                <div class="acoes">
                    <button @click="editar(o)">✏️</button>
                    <button @click="deletar(o.id)">🗑️</button>
                </div>
            </li>
        </ul>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const origens = ref([])
const novaOrigem = ref({ nome: '' })
const editandoId = ref(null)

const baseURL = import.meta.env.VITE_API_URL.replace(/\/$/, '')
const headers = {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${localStorage.getItem('token')}`
}

const carregarOrigens = async () => {
    try {
        const res = await fetch(`${baseURL}/origens_problema/`, { headers })
        origens.value = await res.json()
    } catch (err) {
    console.error('Erro ao carregar origens:', err)
    }
}

const salvarOrigem = async () => {
    const url = editandoId.value
        ? `${baseURL}/origens_problema/${editandoId.value}`
        : `${baseURL}/origens_problema/`

    const method = editandoId.value ? 'PUT' : 'POST'

    await fetch(url, {
    method,
    headers,
    body: JSON.stringify(novaOrigem.value)
    })

    resetarFormulario()
    carregarOrigens()
}

const editar = (origem) => {
    novaOrigem.value = { nome: origem.nome }
    editandoId.value = origem.id
}

const deletar = async (id) => {
    if (confirm('Deseja desativar esta origem?')) {
        await fetch(`${baseURL}/origens_problema/${id}`, {
        method: 'DELETE',
        headers
    })
    carregarOrigens()
    }
}

const resetarFormulario = () => {
    novaOrigem.value = { nome: '' }
    editandoId.value = null
}

onMounted(carregarOrigens)
</script>

<style scoped>
.origens {
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
