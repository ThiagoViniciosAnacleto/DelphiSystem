<template>
    <div class="formulario-chamado">
        <h2>Criar Novo Chamado</h2>
        <form @submit.prevent="enviarFormulario">
            <label>Responsável</label>
            <select v-model="form.responsavel_atendimento_id">
                <option :value="null">Selecione</option>
                <option v-for="u in usuarios" :value="u.id" :key="u.id">{{ u.nome }}</option>
            </select>

            <label>Contato*</label>
            <input v-model="form.contato" required />

            <label>Empresa*</label>
            <select v-model="form.empresa_id" required>
                <option :value="null">Selecione</option>
                <option v-for="e in empresas" :value="e.id" :key="e.id">{{ e.nome }}</option>
            </select>

            <label>Relato*</label>
            <textarea v-model="form.relato" required></textarea>

            <label>Prioridade</label>
            <select v-model="form.prioridade_id">
                <option :value="null">Selecione</option>
                <option v-for="p in prioridades" :value="p.id" :key="p.id">{{ p.nome }}</option>
            </select>

            <label>Máquina</label>
            <select v-model="form.tipo_maquina_id">
                <option :value="null">Selecione</option>
                <option v-for="m in maquinas" :value="m.id" :key="m.id">{{ m.modelo }}</option>
            </select>

            <label>Porta SSH</label>
            <input v-model="form.porta_ssh" />

            <label>Origem do Problema</label>
            <select v-model="form.origem_id">
                <option :value="null">Selecione</option>
                <option v-for="o in origens" :value="o.id" :key="o.id">{{ o.nome }}</option>
            </select>

            <label>Status</label>
            <select v-model="form.status_id">
                <option :value="null">Selecione</option>
                <option v-for="s in status" :value="s.id" :key="s.id">{{ s.nome }}</option>
            </select>

            <button type="submit">Salvar Chamado</button>
        </form>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const form = ref({
    responsavel_atendimento_id: null,
    // 'data_hora_atendimento' é registrado via backend.
    contato: '',
    empresa_id: null,
    relato: '',
    prioridade_id: null,
    tipo_maquina_id: null,
    porta_ssh: '',
    origem_id: null,
    responsavel_acao_id: null,
    acao_realizada: null,
    status_id: null,
})

// Listas para os selects
const empresas = ref([])
const maquinas = ref([])
const prioridades = ref([])
const origens = ref([])
const usuarios = ref([])
const status = ref([]) // Lista de estados do chamado (ex: Aberto, Em Andamento, Fechado)

import apiClient from '../services/api'

onMounted(async () => {
    try {
        // Carregando todas as listas necessárias para os selects
        empresas.value = await apiClient.get('/empresas/')
        maquinas.value = await apiClient.get('/maquinas/')
        prioridades.value = await apiClient.get('/prioridades/')
        origens.value = await apiClient.get('/origens_problema/')
        usuarios.value = await apiClient.get('/usuarios/')
        status.value = await apiClient.get('/status_chamado/')
    } catch (error) {
        alert(`Erro ao carregar dados: ${error.message || 'Erro de comunicação'}`)
    }
})

const enviarFormulario = async () => {
    // Validação dos campos obrigatórios conforme o schema do backend
    if (
        !form.value.contato ||
        !form.value.empresa_id ||
        !form.value.relato
    ) {
        alert('Por favor, preencha todos os campos obrigatórios (*: Empresa, Contato e Relato).')
        return
    }

    try {
        const payload = { ...form.value }
        await apiClient.post('/chamados/', payload)

        alert('Chamado criado com sucesso!')

        // Limpar o formulário para um novo chamado somente em sucesso
        form.value = {
            responsavel_atendimento_id: null,
            contato: '',
            empresa_id: null,
            relato: '',
            prioridade_id: null,
            tipo_maquina_id: null,
            porta_ssh: '',
            origem_id: null,
            responsavel_acao_id: null,
            acao_realizada: null,
            status_id: null
        }
    } catch (error) {
        alert('Erro ao criar chamado: ' + (error.message || 'Erro desconhecido.'))
    }
}
</script>


<style scoped>
.formulario-chamado {
    max-width: 700px;
    margin: 0 auto;
    padding: 20px;
    background-color: #f9f9f9;
    border-radius: 8px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

h2 {
    text-align: center;
    color: #333;
    margin-bottom: 1.5rem;
}

form {
    display: flex;
    flex-direction: column;
    gap: 1.2rem;
}

label {
    font-weight: bold;
    color: #555;
    margin-bottom: 0.2rem; /* Espaçamento entre label e input */
}

input, select, textarea {
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 6px;
    font-size: 15px;
    width: 100%;
    box-sizing: border-box;
}

textarea {
    resize: vertical;
    min-height: 80px;
}

input[type="datetime-local"] {
    /* Estilos específicos para datetime-local se necessário */
}

button {
    background-color: #007bff;
    color: white;
    padding: 12px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 16px;
    font-weight: bold;
    transition: background-color 0.2s ease;
}

button:hover {
    background-color: #0056b3;
}

label::after {
    content: '*';
    color: red;
    margin-left: 4px;
}
</style>
