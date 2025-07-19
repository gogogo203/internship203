import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { User } from '@/types/user'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  const isAuthenticated = ref(false)

  function login(userData: User, authToken: string) {
    user.value = userData
    token.value = authToken
    isAuthenticated.value = true
  }

  function logout() {
    user.value = null
    token.value = null
    isAuthenticated.value = false
  }

  return { user, token, isAuthenticated, login, logout }
})