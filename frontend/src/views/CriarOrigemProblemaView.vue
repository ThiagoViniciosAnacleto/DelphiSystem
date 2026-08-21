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
import apiClient from '../services/api'

const origens = ref([])
const novaOrigem = ref({ nome: '' })
const editandoId = ref(null)
const erro = ref('')

const carregarOrigens = async () => {
    try {
        erro.value = ''
        origens.value = await apiClient.get('/origens_problema/')
    } catch (err) {
        erro.value = 'Erro ao carregar origens: ' + (err.message || 'Erro de comunicação')
    }
}

const salvarOrigem = async () => {
    try {
        erro.value = ''
        if (editandoId.value) {
            await apiClient.put(`/origens_problema/${editandoId.value}`, novaOrigem.value)
        } else {
            await apiClient.post('/origens_problema/', novaOrigem.value)
        }

        resetarFormulario()
        await carregarOrigens()
    } catch (err) {
        erro.value = 'Erro ao salvar origem: ' + (err.message || 'Erro de comunicação')
        alert(erro.value)
    }
}

const editar = (origem) => {
    novaOrigem.value = { nome: origem.nome }
    editandoId.value = origem.id
}

const deletar = async (id) => {
    if (confirm('Deseja desativar esta origem?')) {
        try {
            erro.value = ''
            await apiClient.delete(`/origens_problema/${id}`)
            await carregarOrigens()
        } catch (err) {
            alert('Falha ao desativar origem: ' + (err.message || 'Erro de comunicação'))
        }
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
