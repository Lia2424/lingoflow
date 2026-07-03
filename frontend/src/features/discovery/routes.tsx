import type { RouteObject } from 'react-router-dom'

import Placeholder from '@/components/ui/Placeholder'

export const discoveryRoutes: RouteObject[] = [
  { path: '/', element: <Placeholder label="Discovery Feed" /> },
]
