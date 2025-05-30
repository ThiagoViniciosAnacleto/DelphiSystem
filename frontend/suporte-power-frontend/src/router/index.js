import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '@/layouts/MainLayout.vue'
import LoginView from '@/views/LoginView.vue'
import RecuperarSenhaView from '@/views/RecuperarSenhaView.vue'
import ResetarSenhaView from '@/views/ResetarSenhaView.vue'
import DashboardView from '@/views/DashboardView.vue'

const routes = [
    { path: '/login', component: LoginView },

    { path: '/recuperar-senha', component: RecuperarSenhaView },
    
    { path: '/resetar-senha', component: ResetarSenhaView },

    { path: '/', component: MainLayout,
        children: [
            { path: '', redirect: '/dashboard' },
            { path: 'dashboard', component: DashboardView },
            { path: 'cadastrar-empresa', component: () => import('@/views/CadastrarEmpresaView.vue') },]
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router
