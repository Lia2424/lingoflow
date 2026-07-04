import { Navigate, Outlet, useLocation } from 'react-router-dom'

import { useAuthStore } from '@/stores/authStore'

import NavBar from './NavBar'

/**
 * Wraps all protected routes.
 * - Redirects to /login if not authenticated.
 * - Renders the persistent NavBar above the page content.
 */
export default function AppLayout() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  const location = useLocation()

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  return (
    <div className="flex min-h-screen flex-col">
      <NavBar />
      <main className="flex-1">
        <Outlet />
      </main>
    </div>
  )
}
