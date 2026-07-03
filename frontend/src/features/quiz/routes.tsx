import type { RouteObject } from 'react-router-dom'

import Placeholder from '@/components/ui/Placeholder'

export const quizRoutes: RouteObject[] = [
  { path: '/quiz/:contentId', element: <Placeholder label="Quiz" /> },
]
