<template>
    <div class="empresas">
        <h2>Cadastrar Empresas</h2>

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
import apiClient from '../services/api'

const empresas = ref([])
const novaEmpresa = ref({ nome: '' })
const editandoId = ref(null)
const erro = ref('')

// Lista empresas do backend.
const carregarEmpresas = async () => {
    try {
        erro.value = ''
        empresas.value = await apiClient.get('/empresas/')
    } catch (err) {
        erro.value = 'Erro ao carregar empresas: ' + (err.message || 'Erro de comunicação')
    }
}

// Cria ou atualiza uma empresa
const salvarEmpresa = async () => {
    try {
        erro.value = ''
        if (editandoId.value) {
            await apiClient.put(`/empresas/${editandoId.value}`, novaEmpresa.value)
        } else {
            await apiClient.post('/empresas/', novaEmpresa.value)
        }
        resetarFormulario()
        await carregarEmpresas()
    } catch (err) {
        erro.value = 'Erro ao salvar empresa: ' + (err.message || 'Erro de comunicação')
        alert(erro.value)
    }
}

// Preenche o form para edição
const editar = (empresa) => {
    novaEmpresa.value = { nome: empresa.nome }
    editandoId.value = empresa.id
}

// Desativa a empresa
const deletar = async (id) => {
    if (confirm('Deseja desativar esta empresa?')) {
        try {
            erro.value = ''
            await apiClient.delete(`/empresas/${id}`)
            await carregarEmpresas()
        } catch (err) {
            alert('Falha ao desativar empresa: ' + (err.message || 'Erro de comunicação'))
        }
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
