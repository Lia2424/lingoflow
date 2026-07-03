import { Navigate } from 'react-router-dom'

import { useAuthStore } from '@/stores/authStore'
import OnboardingPage from '@/features/auth/OnboardingPage'

/** Redirects already-onboarded users away from /onboarding */
export default function OnboardingGuard() {
  const user = useAuthStore((s) => s.user)
  if (user?.target_language) {
    return <Navigate to="/" replace />
  }
  return <OnboardingPage />
}
