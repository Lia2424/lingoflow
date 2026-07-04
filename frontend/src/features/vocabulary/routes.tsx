import type { RouteObject } from 'react-router-dom'

import ReviewPage from './ReviewPage'
import VocabularyPage from './VocabularyPage'

export const vocabularyRoutes: RouteObject[] = [
  { path: '/vocabulary', element: <VocabularyPage /> },
  { path: '/vocabulary/review', element: <ReviewPage /> },
]
