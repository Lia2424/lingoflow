import axios, { type AxiosRequestConfig, type InternalAxiosRequestConfig } from 'axios'

const apiClient = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
  withCredentials: true,
})

// ── Request interceptor — attach access token ─────────────────────────────

apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  // Read directly from the store's persisted localStorage key to avoid
  // a circular import between this module and authStore.
  const raw = localStorage.getItem('lingoflow-auth')
  const token = raw ? (JSON.parse(raw)?.state?.accessToken as string | null) : null
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

      // Lazy import avoids circular dependency
      const { useAuthStore } = await import('@/stores/authStore')
      useAuthStore.getState().clearAuth()
      window.location.href = '/login'
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
        const raw = localStorage.getItem('lingoflow-auth')
        const refreshToken = raw ? (JSON.parse(raw)?.state?.refreshToken as string | null) : null

        if (!refreshToken) throw new Error('No refresh token')

        const { data } = await apiClient.post('/auth/refresh', { refresh_token: refreshToken })
        const newAccessToken: string = data.access_token
        const newRefreshToken: string = data.refresh_token

        const { useAuthStore } = await import('@/stores/authStore')
        const { user } = useAuthStore.getState()
        if (user) useAuthStore.getState().setAuth(user, newAccessToken, newRefreshToken)

        processQueue(null, newAccessToken)
        original.headers = { ...original.headers, Authorization: `Bearer ${newAccessToken}` }
        return apiClient(original)
      } catch (refreshError) {
        processQueue(refreshError, null)
        const { useAuthStore } = await import('@/stores/authStore')
        useAuthStore.getState().clearAuth()
        window.location.href = '/login'
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    return Promise.reject(error)
  },
)

export default apiClient
