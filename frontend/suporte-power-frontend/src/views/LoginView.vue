<template>
    <div class="container d-flex justify-content-center align-items-center vh-100">
        <div class="card p-4 shadow w-100" style="max-width: 400px">
        <h3 class="text-center mb-3">Login</h3>

        <form @submit.prevent="fazerLogin">
            <div class="mb-3">
                <label for="username" class="form-label">E-mail</label>
                <input
                    v-model="username"
                    type="email"
                    class="form-control"
                    id="username"
                    placeholder="email@empresa.com"
                    required
                    />
            </div>

            <div class="mb-3">
                <label for="password" class="form-label">Senha</label>
                <input
                v-model="password"
                type="password"
                class="form-control"
                id="password"
                required
                />
            </div>

            <button type="submit" class="btn btn-primary w-100">Entrar</button>

            <div class="text-center mt-2">
                <a href="/recuperar-senha" class="small">Esqueci minha senha</a>
            </div>

            <div v-if="erro" class="alert alert-danger mt-3" role="alert">
            {{ erro }}
            </div>
        </form>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import qs from 'qs'
import { useRouter } from 'vue-router'

const username = ref('')
const password = ref('')
const erro = ref('')
const router = useRouter()

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL
})

const fazerLogin = async () => {
    try {
        const response = await api.post(
        '/login',
        qs.stringify({
            username: username.value,
            password: password.value
        }),
        {
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
            }
        }
    )

    const token = response.data.access_token
    const usuario = response.data.usuario

    localStorage.setItem('token', token)
    localStorage.setItem('usuario', JSON.stringify(usuario))

    router.push('/dashboard')
    } catch (err) {
        erro.value = 'Usuário ou senha inválidos'
    }
}
</script>
