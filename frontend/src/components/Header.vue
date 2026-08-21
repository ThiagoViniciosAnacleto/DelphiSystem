<template>
    <header class="header">
        <div class="left">
            <img src="/logo.png" alt="Power Vending" class="logo" />
        </div>

        <div class="right">
            <button class="btn yellow">🔔 Notificações</button>
            <button class="btn yellow">⚙️ Modo Claro</button>
            <button class="btn red" @click="logout">Sair</button>

            <section class="usuario" aria-label="Informações do usuário logado">
                <img
                :src="usuario.avatar"
                alt="Avatar do usuário"
                class="usuario-avatar"
                @error="usuario.avatar = '/avatar.png'"/>
                <div class="usuario-dados">
                    <span class="usuario-nome">{{ usuario.nome }}</span>
                    <span class="usuario-cargo">{{ usuario.nivel }}</span>
                </div>
            </section>
        </div>
    </header>
</template>

<script setup>
import { reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const usuario = reactive({
    nome: '',
    nivel: '',
    avatar: ''
})

onMounted(() => {
    const raw = localStorage.getItem('usuario')

    try {
        const userData = raw ? JSON.parse(raw) : null

        if (userData) {
            usuario.nome = userData.nome || ''

            const nivelMap = {
                admin: 'Administrador',
                tecnico: 'Técnico',
                comum: 'Usuário'
            }

            const avatarPorNivel = {
                Administrador: '/avatar-admin.png',
                Técnico: '/avatar-tecnico.png',
                Usuário: '/avatar-usuario.png'
            }

            const role = userData.role || 'comum'
            usuario.nivel = nivelMap[role] || 'Usuário'
            usuario.avatar = userData.avatar || avatarPorNivel[usuario.nivel] || '/avatar.png'
        }
    } catch {
        // Ignora erro de parse corrompido sem vazar dados
    }
})




function logout() {
    localStorage.removeItem('token')
    localStorage.removeItem('usuario')
    router.push('/login')
}
</script>

<style scoped>
.header {
    height: 60px;
    width: 100%;
    background-color: #f8f9fa;
    color: #212529;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 1.5rem;
    border-bottom: 1px solid #dee2e6;
    position: sticky;
    top: 0;
    z-index: 100;
}

.logo {
    height: 36px;
}

.right {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.btn {
    border: none;
    border-radius: 6px;
    padding: 6px 12px;
    font-weight: bold;
    cursor: pointer;
    font-size: 14px;
    transition: background 0.2s;
}

.btn.yellow {
    background-color: #ffc107;
    color: #000;
}

.btn.red {
    background-color: #dc3545;
    color: #fff;
}

.usuario {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-left: 12px;
}

.usuario-avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    object-fit: cover;
}

.usuario-dados {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
}

.usuario-nome {
    font-weight: bold;
    color: #212529;
}

.usuario-cargo {
    font-size: 12px;
    color: #6c757d;
}
</style>
