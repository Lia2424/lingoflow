import { Navigate, Outlet, useLocation } from 'react-router-dom'

import { useAuthStore } from '@/stores/authStore'

export default function ProtectedRoute() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  const location = useLocation()

  if (!isAuthenticated) {
    // Pass the attempted URL so login can redirect back after success
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  return <Outlet />
}
