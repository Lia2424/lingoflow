import axios, { type AxiosRequestConfig, type InternalAxiosRequestConfig } from 'axios'

import { useAuthStore } from '@/stores/authStore'

const apiClient = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
  withCredentials: true,
})

// ── Request interceptor — attach access token ─────────────────────────────

apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  // useAuthStore.getState() works outside React components — Zustand stores
  // are module-level singletons. There is no circular import: authStore does
  // not import from this module.
  const token = useAuthStore.getState().accessToken
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// ── Response interceptor — refresh token on 401 ───────────────────────────

let isRefreshing = false
// Queue of { resolve, reject } callbacks waiting for the refresh to complete.
let waitQueue: Array<{ resolve: (token: string) => void; reject: (err: unknown) => void }> = []

function processQueue(error: unknown, token: string | null) {
  waitQueue.forEach(({ resolve, reject }) => {
    if (error) reject(error)
    else resolve(token!)
  })
  waitQueue = []
}

function redirectToLogin() {
  useAuthStore.getState().clearAuth()
  // replace() avoids adding the protected page to browser history so the
  // back button doesn't return the user to a page they can no longer access.
  window.location.replace('/login')
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original: AxiosRequestConfig & { _retried?: boolean } = error.config

    const is401 = error.response?.status === 401
    const isRefreshEndpoint = original?.url?.includes('/auth/refresh')
    const alreadyRetried = original?._retried

    // If the 401 came from the refresh endpoint itself, or we already retried,
    // the session is genuinely expired — clear auth and redirect.
    if (is401 && (isRefreshEndpoint || alreadyRetried)) {
      processQueue(error, null)
      isRefreshing = false
      redirectToLogin()
      return Promise.reject(error)
    }

    if (is401 && !alreadyRetried) {
      original._retried = true

      if (isRefreshing) {
        // Another request already kicked off a refresh — wait for it.
        return new Promise((resolve, reject) => {
          waitQueue.push({ resolve, reject })
        }).then((token) => {
          original.headers = { ...original.headers, Authorization: `Bearer ${token}` }
          return apiClient(original)
        })
      }

      isRefreshing = true

      try {
        const refreshToken = useAuthStore.getState().refreshToken
        if (!refreshToken) throw new Error('No refresh token')

        const { data } = await apiClient.post('/auth/refresh', { refresh_token: refreshToken })
        const newAccessToken: string = data.access_token
        const newRefreshToken: string = data.refresh_token

        const { user } = useAuthStore.getState()
        if (user) useAuthStore.getState().setAuth(user, newAccessToken, newRefreshToken)

        processQueue(null, newAccessToken)
        original.headers = { ...original.headers, Authorization: `Bearer ${newAccessToken}` }
        return apiClient(original)
      } catch (refreshError) {
        processQueue(refreshError, null)
        redirectToLogin()
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    return Promise.reject(error)
  },
)

export default apiClient
