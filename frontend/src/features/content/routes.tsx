import type { RouteObject } from 'react-router-dom'

const Placeholder = () => (
  <div className="min-h-screen flex items-center justify-center text-gray-400 text-sm">
    Content Detail — coming soon
  </div>
)

export const contentRoutes: RouteObject[] = [
  {
    path: '/content/:id',
    element: <Placeholder />,
  },
]
