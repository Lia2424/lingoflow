import { create } from 'zustand'
import { persist } from 'zustand/middleware'

import type { User } from '@/types'

interface AuthState {
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  setAuth: (user: User, accessToken: string, refreshToken: string) => void
  updateUser: (patch: Partial<User>) => void
  clearAuth: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      setAuth: (user, accessToken, refreshToken) =>
        set({ user, accessToken, refreshToken, isAuthenticated: true }),
      updateUser: (patch) =>
        set((state) => ({
          user: state.user ? { ...state.user, ...patch } : state.user,
        })),
      clearAuth: () =>
        set({ user: null, accessToken: null, refreshToken: null, isAuthenticated: false }),
    }),
    {
      name: 'lingoflow-auth',
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
      }),
      // After rehydration, derive isAuthenticated from token presence — not
      // token validity. An expired or malformed token stored in localStorage
      // will still set isAuthenticated=true here, and the user will appear
      // logged in until the first API call returns 401 and the axios interceptor
      // calls clearAuth(). This is an intentional tradeoff: validating the JWT
      // signature client-side would require shipping the secret key to the browser.
      // Milestone 6 (httpOnly cookies + /auth/me check on load) eliminates this gap.
      onRehydrateStorage: () => (state) => {
        if (state) {
          state.isAuthenticated = state.accessToken !== null
        }
      },
    },
  ),
)
