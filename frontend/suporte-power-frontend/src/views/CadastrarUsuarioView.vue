<template>
    <div class="usuarios">
        <h2>Cadastro de Usuário</h2>

        <form @submit.prevent="salvarUsuario">
            <input v-model="usuario.nome" placeholder="Nome completo" required />
            <input v-model="usuario.email" type="email" placeholder="E-mail" required />
            <input v-model="usuario.senha" type="password" placeholder="Senha" required />
            <select v-model="usuario.role_id" required>
                <option value="" disabled>Selecione o perfil</option>
                <option v-for="r in roles" :value="r.id" :key="r.id">{{ r.nome }}</option>
            </select>

            <button type="submit">
                {{ editandoId ? "Atualizar" : "Cadastrar" }}
            </button>
        </form>

        <hr />

        <h3>Usuários Cadastrados</h3>
        <ul>
            <li v-for="u in usuarios" :key="u.id">
                <span>{{ u.nome }} ({{ u.email }})</span>
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

const usuarios = ref([])
const roles = ref([])
const usuario = ref({ nome: '', email: '', senha: '', role_id: '' })
const editandoId = ref(null)

const baseURL = import.meta.env.VITE_API_URL.replace(/\/$/, '')
const headers = {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${localStorage.getItem('token')}`
}

const carregarUsuarios = async () => {
    const res = await fetch(`${baseURL}/usuarios/`, { headers })
    usuarios.value = await res.json()
}

const carregarRoles = async () => {
    const res = await fetch(`${baseURL}/roles/`, { headers })
    roles.value = await res.json()
}

const salvarUsuario = async () => {
    const url = editandoId.value
        ? `${baseURL}/usuarios/${editandoId.value}`
        : `${baseURL}/usuarios/`

    const method = editandoId.value ? 'PUT' : 'POST'

    await fetch(url, {
        method,
        headers,
        body: JSON.stringify(usuario.value)
    })

    resetarFormulario()
    carregarUsuarios()
}

const editar = (u) => {
    usuario.value = {
        nome: u.nome,
        email: u.email,
        senha: '', // não se edita senha diretamente aqui
        role_id: u.role_id
    }
    editandoId.value = u.id
}

const deletar = async (id) => {
    if (confirm('Deseja desativar este usuário?')) {
    await fetch(`${baseURL}/usuarios/${id}`, {
        method: 'DELETE',
        headers
    })
    carregarUsuarios()
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
