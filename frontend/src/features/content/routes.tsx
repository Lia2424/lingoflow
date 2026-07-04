import type { RouteObject } from 'react-router-dom'

import ContentDetailPage from '@/features/content/ContentDetailPage'

export const contentRoutes: RouteObject[] = [
  { path: '/content/:id', element: <ContentDetailPage /> },
]
