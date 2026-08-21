<template>
    <div class="usuarios">
        <h2>{{ editandoId ? "Atualizar Usuário" : "Cadastro de Usuário" }}</h2>

        <form @submit.prevent="salvarUsuario">
            <input v-model="usuario.nome" placeholder="Nome completo" required />
            <input v-model="usuario.email" type="email" placeholder="E-mail" required />

            <input
                v-if="!editandoId"
                v-model="usuario.senha"
                type="password"
                placeholder="Senha"
                required
            />

            <select v-model="usuario.role_id" :required="!editandoId">
                <option v-if="!editandoId" value="" disabled>Selecione o perfil</option>
                <option v-for="r in roles" :value="r.id" :key="r.id">{{ r.nome }}</option>
            </select>

            <button type="submit">
                {{ editandoId ? "Atualizar" : "Cadastrar" }}
            </button>
            <button v-if="editandoId" type="button" @click="resetarFormulario" style="background-color: #6c757d; margin-top: 5px;">
                Cancelar Edição
            </button>
        </form>

        <hr />

        <h3>Usuários Cadastrados</h3>
        <ul>
            <li v-for="u in usuarios" :key="u.id">
                <span>{{ u.nome }} ({{ u.email }}) - Perfil: {{ u.role?.nome || 'Não definido' }}</span>
                <div class="acoes">
                    <button @click="editar(u)">✏️</button>
                    <button @click="deletar(u.id)">🗑️</button>
                </div>
            </li>
        </ul>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import apiClient from '../services/api'

const usuarios = ref([])
const roles = ref([])
const usuario = ref({ nome: '', email: '', senha: '', role_id: '' })
const editandoId = ref(null)
const erro = ref('')

const carregarUsuarios = async () => {
    try {
        erro.value = ''
        usuarios.value = await apiClient.get('/usuarios/')
    } catch (error) {
        erro.value = "Erro ao carregar usuários: " + (error.message || 'Erro de comunicação')
    }
}

const carregarRoles = async () => {
    try {
        erro.value = ''
        roles.value = await apiClient.get('/roles/')
    } catch (error) {
        erro.value = "Erro ao carregar roles: " + (error.message || 'Erro de comunicação')
    }
}

const salvarUsuario = async () => {
    const payload = {
        nome: usuario.value.nome,
        email: usuario.value.email,
        role_id: usuario.value.role_id ? Number(usuario.value.role_id) : null,
    }

    if (!editandoId.value) {
        payload.senha = usuario.value.senha
    }

    try {
        erro.value = ''
        if (editandoId.value) {
            await apiClient.put(`/usuarios/${editandoId.value}`, payload)
        } else {
            await apiClient.post('/usuarios/', payload)
        }

        alert(`Usuário ${editandoId.value ? 'atualizado' : 'cadastrado'} com sucesso!`)
        resetarFormulario()
        await carregarUsuarios()
    } catch (error) {
        erro.value = `Erro ao salvar usuário: ${error.message}`
        alert(erro.value)
    }
}

const editar = (u) => {
    usuario.value = {
        nome: u.nome,
        email: u.email,
        role_id: u.role_id || u.role?.id || ''
    }
    editandoId.value = u.id
}

const deletar = async (id) => {
    if (confirm('Deseja desativar este usuário?')) {
        try {
            erro.value = ''
            await apiClient.delete(`/usuarios/${id}`)
            alert('Usuário desativado com sucesso!')
            await carregarUsuarios()
        } catch (error) {
            alert(`Erro ao desativar usuário: ${error.message}`)
        }
    }
}

const resetarFormulario = () => {
    usuario.value = { nome: '', email: '', senha: '', role_id: '' }
    editandoId.value = null
}

onMounted(() => {
    carregarUsuarios()
    carregarRoles()
})
</script>



<style scoped>
.usuarios {
    max-width: 700px;
    margin: 40px auto;
    padding: 20px;
    background: #f8f9fa;
    border-radius: 12px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
    font-family: 'Segoe UI', sans-serif;
}

form {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-bottom: 20px;
}

input,
select {
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
