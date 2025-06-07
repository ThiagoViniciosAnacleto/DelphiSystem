import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '@/layouts/MainLayout.vue'
import LoginView from '@/views/LoginView.vue'
import RecuperarSenhaView from '@/views/RecuperarSenhaView.vue'
import ResetarSenhaView from '@/views/ResetarSenhaView.vue'
import DashboardView from '@/views/DashboardView.vue'

const routes = [
  // Rotas públicas (sem autenticação)
    { path: '/login', component: LoginView },
    { path: '/recuperar-senha', component: RecuperarSenhaView },
    { path: '/resetar-senha', component: ResetarSenhaView },

  // Rotas protegidas (com layout principal)
    {
    path: '/',
    component: MainLayout,
    children: [
        { path: '', redirect: '/dashboard' },
        { path: 'dashboard', component: DashboardView },
        { path: 'criar-chamados', component: () => import('@/views/CriarChamadoView.vue') },
        { path: 'cadastrar-empresa', component: () => import('@/views/CadastrarEmpresaView.vue') },
        { path: 'criar-origem-problema', component: () => import('@/views/CriarOrigemProblemaView.vue') },
        { path: 'cadastrar-maquina', component: () => import('@/views/CadastrarMaquinaView.vue') },
        { path: 'cadastrar-usuario', component: () => import('@/views/CadastrarUsuarioView.vue') },
        { path: 'lista-chamados', component: () => import('@/views/ListaChamadosView.vue') },
        { path: 'cadastrar-prioridade', component: () => import('@/views/CadastrarPrioridadeView.vue') },
        { path: 'cadastrar-prioridade', component: () => import('@/views/CadastrarStatusView.vue') },
        { path: 'chamados-recorrentes', component: () => import('@/views/ChamadosRecorrentesView.vue') }
        ]
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router
