import type { RouteObject } from 'react-router-dom'

import DiscoveryPage from '@/features/discovery/DiscoveryPage'

export const discoveryRoutes: RouteObject[] = [{ path: '/', element: <DiscoveryPage /> }]
