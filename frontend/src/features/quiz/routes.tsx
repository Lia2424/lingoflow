import type { RouteObject } from 'react-router-dom'

const Placeholder = () => (
  <div className="min-h-screen flex items-center justify-center text-gray-400 text-sm">
    Quiz — coming soon
  </div>
)

export const quizRoutes: RouteObject[] = [
  {
    path: '/quiz/:contentId',
    element: <Placeholder />,
  },
]
