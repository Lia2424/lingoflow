import { createBrowserRouter } from 'react-router-dom'

import ProtectedRoute from '@/app/ProtectedRoute'
import { authRoutes } from '@/features/auth/routes'
import { contentRoutes } from '@/features/content/routes'
import { discoveryRoutes } from '@/features/discovery/routes'
import { immersionPlanRoutes } from '@/features/immersion-plan/routes'
import { quizRoutes } from '@/features/quiz/routes'
import { vocabularyRoutes } from '@/features/vocabulary/routes'

export const router = createBrowserRouter([
  // Public — no auth required
  ...authRoutes,

  // Protected — redirects to /login if not authenticated
  {
    element: <ProtectedRoute />,
    children: [
      ...discoveryRoutes,
      ...contentRoutes,
      ...vocabularyRoutes,
      ...immersionPlanRoutes,
      ...quizRoutes,
    ],
  },
])
