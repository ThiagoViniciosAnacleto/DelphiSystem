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
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router
