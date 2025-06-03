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

const headers = {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${localStorage.getItem('token')}`
}

const carregarEmpresas = async () => {
    empresas.value = await fetch('/empresas', { headers }).then(res => res.json())
}

const salvarEmpresa = async () => {
    const url = editandoId.value
        ? `/empresas${editandoId.value}`
        : '/empresas'

    const method = editandoId.value ? 'PUT' : 'POST'

    await fetch(url, {
    method,
    headers,
    body: JSON.stringify(novaEmpresa.value)
})

    novaEmpresa.value = { nome: '' }
    editandoId.value = null
    carregarEmpresas()
}

const editar = (empresa) => {
    novaEmpresa.value = { nome: empresa.nome }
    editandoId.value = empresa.id
}

const deletar = async (id) => {
    if (confirm('Deseja desativar esta empresa?')) {
        await fetch(`/empresas${id}`, {
        method: 'DELETE',
        headers
    })
    carregarEmpresas()
    }
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
