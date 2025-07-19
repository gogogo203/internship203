import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/HomeView.vue')
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/auth/LoginView.vue')
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/auth/RegisterView.vue')
    },
    {
      path: '/organizer',
      name: 'organizer',
      component: () => import('../views/organizer/DashboardView.vue'),
      meta: { requiresAuth: true, role: 'organizer' }
    },
    {
      path: '/presenter',
      name: 'presenter',
      component: () => import('../views/presenter/DashboardView.vue'),
      meta: { requiresAuth: true, role: 'presenter' }
    },
    {
      path: '/listener',
      name: 'listener',
      component: () => import('../views/listener/DashboardView.vue'),
      meta: { requiresAuth: true, role: 'listener' }
    }
  ]
})

export default router