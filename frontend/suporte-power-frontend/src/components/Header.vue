<template>
    <header class="header">
        <div class="left">
        <!-- Espaço para futuro breadcrumb, etc. -->
        </div>

        <div class="right">
            <button class="notificacoes">🔔 Notificações</button>
            <button class="modo-claro">⚙️ Modo Claro</button>
            <button class="sair" @click="logout">Sair</button>
            <div class="usuario">
                <span>Thiago</span>
                <small>Administrador</small>
            </div>
        </div>
    </header>
</template>

<script setup>
import { useRouter } from 'vue-router'
const router = useRouter()

function logout() {
    localStorage.removeItem('token')
    router.push('/login')
}
</script>

<style scoped>
.header {
    height: 60px;
    background-color: #1a1a1a;
    color: white;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 1.5rem;
}

.right {
    display: flex;
    align-items: center;
    gap: 1rem;
}

button {
    background-color: #ffc107;
    border: none;
    border-radius: 6px;
    padding: 6px 12px;
    font-weight: bold;
    cursor: pointer;
}

.sair {
    background-color: #dc3545;
    color: white;
}

.usuario {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    margin-left: 10px;
}
</style>
