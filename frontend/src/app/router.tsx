import { createBrowserRouter } from 'react-router-dom'

import AppLayout from '@/app/AppLayout'
import { authRoutes } from '@/features/auth/routes'
import { contentRoutes } from '@/features/content/routes'
import { discoveryRoutes } from '@/features/discovery/routes'
import { immersionPlanRoutes } from '@/features/immersion-plan/routes'
import { quizRoutes } from '@/features/quiz/routes'
import { vocabularyRoutes } from '@/features/vocabulary/routes'

export const router = createBrowserRouter([
  // Public — no auth required
  ...authRoutes,

  // Protected — redirects to /login if not authenticated; renders NavBar
  {
    element: <AppLayout />,
    children: [
      ...discoveryRoutes,
      ...contentRoutes,
      ...vocabularyRoutes,
      ...immersionPlanRoutes,
      ...quizRoutes,
    ],
  },
])
