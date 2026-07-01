import type { RouteObject } from 'react-router-dom'

import Placeholder from '@/components/ui/Placeholder'
import LoginPage from '@/features/auth/LoginPage'
import RegisterPage from '@/features/auth/RegisterPage'

export const authRoutes: RouteObject[] = [
  { path: '/login', element: <LoginPage /> },
  { path: '/register', element: <RegisterPage /> },
  { path: '/onboarding', element: <Placeholder label="Onboarding" /> },
  { path: '/forgot-password', element: <Placeholder label="Forgot password — coming in Milestone 6" /> },
]
