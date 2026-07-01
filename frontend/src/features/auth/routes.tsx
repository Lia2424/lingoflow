import type { RouteObject } from 'react-router-dom'

const Placeholder = ({ label }: { label: string }) => (
  <div className="min-h-screen flex items-center justify-center text-gray-400 text-sm">
    {label} — coming soon
  </div>
)

export const authRoutes: RouteObject[] = [
  {
    path: '/login',
    element: <Placeholder label="Login" />,
  },
  {
    path: '/register',
    element: <Placeholder label="Register" />,
  },
  {
    path: '/onboarding',
    element: <Placeholder label="Onboarding" />,
  },
]
