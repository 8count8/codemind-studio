import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../stores/user'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/HomeView.vue')
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginView.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/RegisterView.vue')
  },
  {
    path: '/reset',
    name: 'Reset',
    component: () => import('../views/ResetView.vue')
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/DashboardView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/quizbank',
    name: 'Quizbank',
    component: () => import('../views/QuizbankView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/answerpad',
    name: 'Answerpad',
    component: () => import('../views/AnswerpadView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/code-review',
    name: 'CodeReview',
    component: () => import('../views/CodeReviewView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/ai-question',
    name: 'AiQuestion',
    component: () => import('../views/AiQuestionView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/ability-matrix',
    name: 'AbilityMatrix',
    component: () => import('../views/AbilityMatrixView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/ProfileView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/favorites',
    name: 'Favorites',
    component: () => import('../views/FavoritesView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('../views/HistoryView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/settings',
    name: 'Settings',
    component: () => import('../views/SettingsView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('../views/AdminView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 全局路由守卫：检查登录状态
router.beforeEach(async (to, from, next) => {
  if (to.meta.requiresAuth) {
    const userStore = useUserStore()

    // 如果还没有检查过登录状态，先检查一次
    if (!userStore.isLoggedIn) {
      const authenticated = await userStore.checkAuth()
      if (!authenticated) {
        return next({ name: 'Login' })
      }
    }
    if (to.meta.requiresAdmin && !userStore.user?.is_admin) {
      return next({ name: 'Dashboard' })
    }
  }
  next()
})

export default router
