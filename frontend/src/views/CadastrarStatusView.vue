<template>
    <div class="status-chamado">
        <h2>Cadastrar Tipos de Status de Chamado</h2>

        <form @submit.prevent="salvarStatus">
            <input v-model="novoStatus.nome" placeholder="Nome do status" required />
            <button type="submit">
            {{ editandoId ? "Atualizar" : "Salvar" }}
            </button>
        </form>

        <hr />

        <h3>Status Cadastrados</h3>

        <ul>
            <li v-for="s in status" :key="s.id">
                <span>{{ s.nome }}</span>
                <div class="acoes">
                    <button @click="editar(s)">✏️</button>
                    <button @click="deletar(s.id)">🗑️</button>
                </div>
            </li>
        </ul>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import apiClient from '../services/api'

const status = ref([])
const novoStatus = ref({ nome: '' })
const editandoId = ref(null)
const erro = ref('')

const carregarStatus = async () => {
    try {
        erro.value = ''
        status.value = await apiClient.get('/status_chamado/')
    } catch (err) {
        erro.value = 'Erro ao carregar status: ' + (err.message || 'Erro de comunicação')
    }
}

const salvarStatus = async () => {
    try {
        erro.value = ''
        if (editandoId.value) {
            await apiClient.put(`/status_chamado/${editandoId.value}`, novoStatus.value)
        } else {
            await apiClient.post('/status_chamado/', novoStatus.value)
        }

        resetarFormulario()
        await carregarStatus()
        alert('Status salvo com sucesso!')
    } catch (err) {
        erro.value = 'Erro ao salvar status: ' + (err.message || 'Erro de comunicação')
        alert(erro.value)
    }
}

const editar = (itemStatus) => {
    novoStatus.value = { nome: itemStatus.nome }
    editandoId.value = itemStatus.id
}

const deletar = async (id) => {
    if (confirm('Deseja desativar este status?')) {
        try {
            erro.value = ''
            await apiClient.delete(`/status_chamado/${id}`)
            await carregarStatus()
            alert('Status desativado com sucesso!')
        } catch (err) {
            alert('Erro ao desativar status: ' + (err.message || 'Erro de comunicação'))
        }
    }
}

const resetarFormulario = () => {
    novoStatus.value = { nome: '' }
    editandoId.value = null
}

onMounted(carregarStatus)
</script>


<style scoped>
.status-chamado {
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
