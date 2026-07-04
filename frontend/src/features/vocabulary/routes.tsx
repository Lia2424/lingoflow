import type { RouteObject } from 'react-router-dom'

import VocabularyPage from './VocabularyPage'

export const vocabularyRoutes: RouteObject[] = [
  { path: '/vocabulary', element: <VocabularyPage /> },
]
