import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '@/layouts/MainLayout.vue'
import LoginView from '@/views/LoginView.vue'
import RecuperarSenhaView from '@/views/RecuperarSenhaView.vue'
import ResetarSenhaView from '@/views/ResetarSenhaView.vue'
import DashboardView from '@/views/DashboardView.vue'

const routes = [
  // Rotas públicas (sem autenticação)
  { path: '/login', component: LoginView, meta: { publicOnly: true } },
  { path: '/recuperar-senha', component: RecuperarSenhaView, meta: { publicOnly: true } },
  { path: '/resetar-senha', component: ResetarSenhaView, meta: { publicOnly: true } },

  // Rotas protegidas (com layout principal)
  {
    path: '/',
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      { path: '', redirect: '/dashboard' },
      { path: 'dashboard', component: DashboardView },
      { path: 'criar-chamados', component: () => import('@/views/CriarChamadoView.vue') },
      { path: 'lista-chamados', component: () => import('@/views/ListaChamadosView.vue') },
      { path: 'chamados/:id', name: 'DetalheChamado', component: () => import('@/views/DetalheChamadoView.vue') },

      // Rotas administrativas (adminOnly)
      { path: 'cadastrar-empresa', component: () => import('@/views/CadastrarEmpresaView.vue'), meta: { adminOnly: true } },
      { path: 'criar-origem-problema', component: () => import('@/views/CriarOrigemProblemaView.vue'), meta: { adminOnly: true } },
      { path: 'cadastrar-maquina', component: () => import('@/views/CadastrarMaquinaView.vue'), meta: { adminOnly: true } },
      { path: 'cadastrar-usuario', component: () => import('@/views/CadastrarUsuarioView.vue'), meta: { adminOnly: true } },
      { path: 'cadastrar-prioridade', component: () => import('@/views/CadastrarPrioridadeView.vue'), meta: { adminOnly: true } },
      { path: 'cadastrar-status', component: () => import('@/views/CadastrarStatusView.vue'), meta: { adminOnly: true } },
      { path: 'chamados-recorrentes', component: () => import('@/views/ChamadosRecorrentesView.vue'), meta: { adminOnly: true } },
    ]
  },
  { path: '/:pathMatch(.*)*', redirect: '/login' }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Guarda Global de Navegação
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  let userRole = 'comum'
  try {
    const rawUser = localStorage.getItem('usuario')
    if (rawUser) {
      const u = JSON.parse(rawUser)
      userRole = typeof u.role === 'string' ? u.role : (u.role?.nome || 'comum')
    }
  } catch {
    // ignore
  }

  const isPublicOnly = to.matched.some(record => record.meta.publicOnly)
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const adminOnly = to.matched.some(record => record.meta.adminOnly)

  if (requiresAuth && !token) {
    return next('/login')
  }

  if (isPublicOnly && token) {
    return next('/dashboard')
  }

  if (adminOnly && userRole !== 'admin') {
    return next('/dashboard')
  }

  next()
})

export default router
