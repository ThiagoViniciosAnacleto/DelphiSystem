<template>
    <div class="container d-flex justify-content-center align-items-center vh-100">
        <div class="card p-4 shadow w-100" style="max-width: 400px">
            <h3 class="text-center mb-3">Redefinir Senha</h3>

            <form @submit.prevent="resetarSenha">
                <div class="mb-3">
                    <label for="senha" class="form-label">Nova Senha</label>
                    <input
                    v-model="senha"
                    type="password"
                    class="form-control"
                    id="senha"
                    required
                    />
                </div>

                <div class="mb-3">
                <label for="confirmar" class="form-label">Confirmar Senha</label>
                <input
                    v-model="confirmar"
                    type="password"
                    class="form-control"
                    id="confirmar"
                    required
                    />
                </div>

                <button type="submit" class="btn btn-success w-100">Salvar Nova Senha</button>

                <div v-if="mensagem" class="alert mt-3" :class="{'alert-success': sucesso, 'alert-danger': !sucesso}">
                {{ mensagem }}
                </div>
            </form>
        </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const senha = ref('')
const confirmar = ref('')
const mensagem = ref('')
const sucesso = ref(false)

const route = useRoute()
const router = useRouter()
const token = ref('')

onMounted(() => {
    token.value = route.query.token || ''
    if (!token.value) {
    mensagem.value = 'Token inválido ou ausente'
    }
})

const resetarSenha = async () => {
    if (senha.value !== confirmar.value) {
        mensagem.value = 'As senhas não coincidem'
        sucesso.value = false
    return
}

    try {
        const response = await axios.post(import.meta.env.VITE_API_URL + '/resetar-senha', {
            token: token.value,
            nova_senha: senha.value
        })

    mensagem.value = response.data.mensagem
    sucesso.value = true

    setTimeout(() => {
        router.push('/login')
    }, 3000)

    } catch (err) {
        mensagem.value = err.response?.data?.detail || 'Erro ao redefinir senha'
        sucesso.value = false
    }
}
</script>
