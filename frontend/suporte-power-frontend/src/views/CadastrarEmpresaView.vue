<template>
    <div class="empresas">
        <h2>Empresas</h2>

        <form @submit.prevent="salvarEmpresa">
            <input v-model="novaEmpresa.nome" placeholder="Nome da empresa" required />
            <button type="submit">Salvar</button>
        </form>

        <hr />

        <h3>Empresas Cadastradas</h3>
        <ul>
            <li v-for="e in empresas" :key="e.id">
            {{ e.nome }}
            <button @click="editar(e)">✏️</button>
            <button @click="deletar(e.id)">🗑️</button>
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
    const res = await fetch(`${baseURL}/empresas`, { headers })
    empresas.value = await res.json()
    } catch (err) {
    console.error("Erro ao carregar empresas:", err)
    }
}

// Cria ou atualiza uma empresa
const salvarEmpresa = async () => {
    const url = editandoId.value
        ? `${baseURL}/empresas/${editandoId.value}`
        : `${baseURL}/empresas`

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
form {
    display: flex;
    gap: 10px;
    margin-bottom: 10px;
}
input {
    flex: 1;
    padding: 8px;
}
button {
    padding: 8px 12px;
}
</style>
