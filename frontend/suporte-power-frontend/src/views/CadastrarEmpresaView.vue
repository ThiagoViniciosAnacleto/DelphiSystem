<template>
    <div class="empresas">
        <h2>Empresas</h2>

        <form @submit.prevent="salvarEmpresa">
            <input
                v-model="novaEmpresa.nome"
                placeholder="Nome da empresa"
                required
            />
            <button type="submit">
                {{ editandoId ? "Atualizar" : "Salvar" }}
            </button>
        </form>
        <hr />

        <h3>Empresas Cadastradas</h3>
        <ul>
            <li v-for="e in empresas" :key="e.id">
                <span>{{ e.nome }}</span>
            <div class="acoes">
                <button @click="editar(e)">✏️</button>
                <button @click="deletar(e.id)">🗑️</button>
            </div>
        </li>
    </ul>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const empresas = ref([])
const novaEmpresa = ref({ nome: '' })
const editandoId = ref(null)

const baseURL = import.meta.env.VITE_API_URL.replace(/\/$/, '')
const headers = {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${localStorage.getItem('token')}`
}
console.log("🚀 VITE_API_URL:", import.meta.env.VITE_API_URL)

// Lista empresas do backend.
const carregarEmpresas = async () => {
    try {
    const res = await fetch(`${baseURL}/empresas/`, { headers })
    empresas.value = await res.json()
    } catch (err) {
    console.error("Erro ao carregar empresas:", err)
    }
}

// Cria ou atualiza uma empresa
const salvarEmpresa = async () => {
    const url = editandoId.value
        ? `${baseURL}/empresas/${editandoId.value}`
        : `${baseURL}/empresas/`

    const method = editandoId.value ? 'PUT' : 'POST'

    await fetch(url, {
        method,
        headers,
        body: JSON.stringify(novaEmpresa.value)
})

    resetarFormulario()
    carregarEmpresas()
}

// Preenche o form para edição
const editar = (empresa) => {
    novaEmpresa.value = { nome: empresa.nome }
    editandoId.value = empresa.id
}

// Desativa a empresa
const deletar = async (id) => {
    if (confirm('Deseja desativar esta empresa?')) {
        await fetch(`${baseURL}/empresas/${id}`, {
        method: 'DELETE',
        headers
    })
    carregarEmpresas()
    }
}

// Limpa o formulário
const resetarFormulario = () => {
    novaEmpresa.value = { nome: '' }
    editandoId.value = null
}

onMounted(() => {
    carregarEmpresas()
})
</script>

<style scoped>
.empresas {
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
