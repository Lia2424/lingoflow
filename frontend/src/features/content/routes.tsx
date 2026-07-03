import type { RouteObject } from 'react-router-dom'

import Placeholder from '@/components/ui/Placeholder'

export const contentRoutes: RouteObject[] = [
  { path: '/content/:id', element: <Placeholder label="Content Detail" /> },
]
