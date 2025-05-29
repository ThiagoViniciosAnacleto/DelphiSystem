<template>
    <div class="container d-flex justify-content-center align-items-center vh-100">
        <div class="card p-4 shadow w-100" style="max-width: 400px">
        <h3 class="text-center mb-3">Recuperar Senha</h3>

            <form @submit.prevent="enviarEmail">
                <div class="mb-3">
                    <label for="email" class="form-label">E-mail</label>
                    <input
                    v-model="email"
                    type="email"
                    class="form-control"
                    id="email"
                    required
                    />
                </div>

                <button type="submit" class="btn btn-primary w-100">Enviar Link</button>

                <div v-if="mensagem" class="alert mt-3" :class="{'alert-success': sucesso, 'alert-danger': !sucesso}">
                    {{ mensagem }}
                </div>
            </form>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const email = ref('')
const mensagem = ref('')
const sucesso = ref(false)

const enviarEmail = async () => {
    try {
        const response = await axios.post(import.meta.env.VITE_API_URL + '/recuperar-senha', {
        email: email.value
    })
        mensagem.value = response.data.mensagem
        sucesso.value = true
    } catch (err) {
        mensagem.value = err.response?.data?.detail || 'Erro ao enviar e-mail de recuperação'
        sucesso.value = false
    }
}
</script>
