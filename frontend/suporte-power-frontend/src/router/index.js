import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'

const routes = [
    {
        path: '/',
        name: 'Login',
        component: LoginView
    },

    {
        path: '/dashboard',
        name: 'Dashboard',
        component: () => import('../views/DashboardView.vue') // criaremos depois
    }

    {
        path: '/recuperar-senha',
        name: 'RecuperarSenha',
        omponent: () => import('@/views/RecuperarSenhaView.vue')
    }

    {
        path: '/resetar-senha',
        component: () => import('@/views/ResetarSenhaView.vue')
    }
    
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router
