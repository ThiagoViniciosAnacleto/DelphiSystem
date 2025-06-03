<template>
    <div class="formulario-chamado">
        <h2>Criar Novo Chamado</h2>
        <form @submit.prevent="enviarFormulario">
            <label>Cliente*</label>
            <input v-model="form.cliente" required />

            <label>Relato*</label>
            <textarea v-model="form.relato" required></textarea>

            <label>Porta SSH</label>
            <input v-model="form.porta_ssh" />

            <label>Descrição da Ação</label>
            <textarea v-model="form.descricao_acao" />

            <label>Empresa</label>
            <select v-model="form.empresa_id">
                <option :value="null">Selecione</option>
                <option v-for="e in empresas" :value="e.id" :key="e.id">{{ e.nome }}</option>
            </select>

            <label>Máquina</label>
            <select v-model="form.tipo_maquina_id">
                <option :value="null">Selecione</option>
                <option v-for="m in maquinas" :value="m.id" :key="m.id">{{ m.modelo }}</option>
            </select>

            <label>Prioridade</label>
            <select v-model="form.prioridade_id">
                <option :value="null">Selecione</option>
                <option v-for="p in prioridades" :value="p.id" :key="p.id">{{ p.nome }}</option>
            </select>

            <label>Origem do Problema</label>
            <select v-model="form.origem_id">
                <option :value="null">Selecione</option>
                <option v-for="o in origens" :value="o.id" :key="o.id">{{ o.nome }}</option>
            </select>

            <label>Responsável</label>
            <select v-model="form.responsavel_atendimento_id">
                <option :value="null">Selecione</option>
                <option v-for="u in usuarios" :value="u.id" :key="u.id">{{ u.nome }}</option>
            </select>

            <button type="submit">Salvar Chamado</button>
        </form>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const form = ref({
    cliente: '',
    relato: '',
    porta_ssh: '',
    descricao_acao: '',
    prioridade_id: null,
    status_id: null,
    empresa_id: null,
    tipo_maquina_id: null,
    origem_id: null,
    responsavel_atendimento_id: null,
    responsavel_acao_id: null
})

const empresas = ref([])
const maquinas = ref([])
const prioridades = ref([])
const origens = ref([])
const usuarios = ref([])

onMounted(async () => {
    const headers = { Authorization: `Bearer ${localStorage.getItem('token')}` }

    empresas.value = await fetch('/api/empresas', { headers }).then(r => r.json())
    maquinas.value = await fetch('/api/maquinas', { headers }).then(r => r.json())
    prioridades.value = await fetch('/api/prioridades', { headers }).then(r => r.json())
    origens.value = await fetch('/api/origens', { headers }).then(r => r.json())
    usuarios.value = await fetch('/api/usuarios', { headers }).then(r => r.json())
})

const enviarFormulario = async () => {
    const resp = await fetch('/api/chamados', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${localStorage.getItem('token')}`
        },
    body: JSON.stringify(form.value)
})

    if (resp.ok) {
        alert('Chamado criado com sucesso!')
    } else {
    const erro = await resp.json()
    alert('Erro ao criar chamado: ' + erro.detail)
    }
}
</script>

<style scoped>
.formulario-chamado {
    max-width: 700px;
    margin: 0 auto;
}
form {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}
input, select, textarea {
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 6px;
    font-size: 14px;
}
button {
    background-color: #198754;
    color: white;
    padding: 10px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
}
button:hover {
    background-color: #157347;
}
</style>
