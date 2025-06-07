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

const status = ref([])
const novoStatus = ref({ nome: '' })
const editandoId = ref(null)

const baseURL = import.meta.env.VITE_API_URL.replace(/\/$/, '')
const headers = {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${localStorage.getItem('token')}`
}

const carregarStatus = async () => {
    try {
        // CORREÇÃO: Indentação movida para dentro do try
        const res = await fetch(`${baseURL}/status_chamado/`, { headers })
        if (!res.ok) {
            const errorData = await res.json();
            throw new Error(errorData.detail || `Erro HTTP ${res.status} ao carregar status`);
        }
        status.value = await res.json()
    } catch (err) {
        // CORREÇÃO: Indentação movida para dentro do catch
        console.error('Erro ao carregar status:', err)
        alert(`Erro ao carregar status: ${err.message || err}`);
    }
}

const salvarStatus = async () => {
    const url = editandoId.value
        ? `${baseURL}/status_chamado/${editandoId.value}`
        : `${baseURL}/status_chamado/`

    const method = editandoId.value ? 'PUT' : 'POST'

    try {
        // CORREÇÃO: Indentação movida para dentro do try
        const res = await fetch(url, {
            method,
            headers,
            body: JSON.stringify(novoStatus.value)
        });

        if (!res.ok) {
            const errorData = await res.json();
            throw new Error(errorData.detail || `Erro HTTP ${res.status} ao salvar status`);
        }

        resetarFormulario()
        carregarStatus()
        alert('Status salvo com sucesso!');
    } catch (err) {
        // CORREÇÃO: Indentação movida para dentro do catch
        console.error('Erro ao salvar status:', err);
        alert(`Erro ao salvar status: ${err.message || err}`);
    }
}

const editar = (itemStatus) => {
    novoStatus.value = { nome: itemStatus.nome }
    editandoId.value = itemStatus.id
}

const deletar = async (id) => {
    if (confirm('Deseja desativar este status?')) {
        try {
            // CORREÇÃO: Indentação movida para dentro do try
            const res = await fetch(`${baseURL}/status_chamado/${id}`, {
                method: 'DELETE',
                headers
            });

            if (!res.ok) {
                // CORREÇÃO: Removida a palavra 'new' extra aqui (new new Error)
                const errorData = await res.json();
                throw new Error(errorData.detail || `Erro HTTP ${res.status} ao deletar status`);
            }
            carregarStatus();
            alert('Status desativado com sucesso!');
        } catch (err) {
            // CORREÇÃO: Indentação movida para dentro do catch
            console.error('Erro ao desativar status:', err);
            alert(`Erro ao desativar status: ${err.message || err}`);
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