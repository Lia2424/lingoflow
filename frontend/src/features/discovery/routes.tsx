import type { RouteObject } from 'react-router-dom'

const Placeholder = () => (
  <div className="min-h-screen flex items-center justify-center text-gray-400 text-sm">
    Discovery Feed — coming soon
  </div>
)

export const discoveryRoutes: RouteObject[] = [
  {
    path: '/',
    element: <Placeholder />,
  },
]
