import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'

import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import LanguageSelect from '@/components/ui/LanguageSelect'
import StepIndicator from '@/components/ui/StepIndicator'
import { parseApiError } from '@/hooks/useApiError'
import { updateMe } from '@/services/users'
import { useAuthStore } from '@/stores/authStore'
import { usePreferencesStore } from '@/stores/preferencesStore'
import type { CEFRLevel } from '@/types'

// ── CEFR level metadata ───────────────────────────────────────────────────────

interface CEFROption {
  level: CEFRLevel
  label: string
  description: string
}

const CEFR_OPTIONS: CEFROption[] = [
  { level: 'A1', label: 'A1 — Beginner', description: 'I know basic words and simple phrases' },
  { level: 'A2', label: 'A2 — Elementary', description: 'I can handle simple, familiar topics' },
  { level: 'B1', label: 'B1 — Intermediate', description: 'I can manage in most everyday situations' },
  { level: 'B2', label: 'B2 — Upper-intermediate', description: 'I understand complex texts and can discuss abstractly' },
  { level: 'C1', label: 'C1 — Advanced', description: 'I express myself fluently with little effort' },
  { level: 'C2', label: 'C2 — Mastery', description: 'I understand virtually everything I hear or read' },
]

const STEP_LABELS = ['Native', 'Target', 'Level']

// ── Component ─────────────────────────────────────────────────────────────────

export default function OnboardingPage() {
  const navigate = useNavigate()
  const setAuth = useAuthStore((s) => s.setAuth)
  const user = useAuthStore((s) => s.user)
  const accessToken = useAuthStore((s) => s.accessToken)
  const refreshToken = useAuthStore((s) => s.refreshToken)
  const setPreferences = usePreferencesStore((s) => s.setPreferences)

  const [step, setStep] = useState(1)
  const [nativeLanguage, setNativeLanguage] = useState(user?.native_language ?? '')
  const [targetLanguage, setTargetLanguage] = useState(user?.target_language ?? '')
  const [cefrLevel, setCefrLevel] = useState<CEFRLevel>(user?.cefr_level ?? 'A1')
  const [apiError, setApiError] = useState<string | null>(null)

  const { mutate, isPending } = useMutation({
    mutationFn: () =>
      updateMe({
        native_language: nativeLanguage,
        target_language: targetLanguage,
        cefr_level: cefrLevel,
      }),
    onSuccess: (updatedUser) => {
      setPreferences(targetLanguage, cefrLevel)
      if (accessToken && refreshToken) {
        setAuth(updatedUser, accessToken, refreshToken)
      }
      navigate('/', { replace: true })
    },
    onError: (error) => setApiError(parseApiError(error)),
  })

  const canAdvanceStep1 = nativeLanguage !== ''
  const canAdvanceStep2 = targetLanguage !== '' && targetLanguage !== nativeLanguage

  function handleNext() {
    setApiError(null)
    setStep((s) => s + 1)
  }

  function handleBack() {
    setApiError(null)
    setStep((s) => s - 1)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-100 to-slate-200 flex flex-col items-center justify-center px-4">
      <div className="mb-8 text-center">
        <h1 className="text-3xl font-bold text-slate-900 tracking-tight">LingoFlow</h1>
        <p className="text-slate-500 text-sm mt-1">Let's set up your experience</p>
      </div>

      <Card className="w-full max-w-md shadow-lg border-slate-200">
        <CardHeader className="pb-2 space-y-4">
          <StepIndicator currentStep={step} totalSteps={3} labels={STEP_LABELS} />
          <div>
            <h2 className="text-lg font-semibold text-slate-900">
              {step === 1 && 'What is your native language?'}
              {step === 2 && 'What language are you learning?'}
              {step === 3 && 'What is your current level?'}
            </h2>
            <p className="text-sm text-slate-500 mt-0.5">
              {step === 1 && 'This helps us understand your background.'}
              {step === 2 && "We'll tailor content recommendations to this language."}
              {step === 3 && 'Be honest — you can update this any time.'}
            </p>
          </div>
        </CardHeader>

        <CardContent className="space-y-4">
          {/* Step 1 — Native language */}
          {step === 1 && (
            <LanguageSelect
              id="native-language"
              label="Native language"
              value={nativeLanguage}
              onChange={setNativeLanguage}
            />
          )}

          {/* Step 2 — Target language */}
          {step === 2 && (
            <LanguageSelect
              id="target-language"
              label="Language you're learning"
              value={targetLanguage}
              onChange={setTargetLanguage}
              excludeCode={nativeLanguage}
            />
          )}

          {/* Step 3 — CEFR level */}
          {step === 3 && (
            <div className="space-y-2" role="radiogroup" aria-label="CEFR level">
              {CEFR_OPTIONS.map((option) => (
                <button
                  key={option.level}
                  type="button"
                  role="radio"
                  aria-checked={cefrLevel === option.level}
                  onClick={() => setCefrLevel(option.level)}
                  className={`w-full rounded-lg border px-4 py-3 text-left transition-colors ${
                    cefrLevel === option.level
                      ? 'border-slate-800 bg-slate-900 text-white'
                      : 'border-slate-200 bg-white text-slate-700 hover:bg-slate-50'
                  }`}
                >
                  <span className="block text-sm font-semibold">{option.label}</span>
                  <span className={`block text-xs mt-0.5 ${cefrLevel === option.level ? 'text-slate-300' : 'text-slate-400'}`}>
                    {option.description}
                  </span>
                </button>
              ))}
            </div>
          )}

          {/* API error */}
          {apiError && (
            <p role="alert" className="text-sm text-red-600 bg-red-50 px-3 py-2 rounded-md">
              {apiError}{' '}
              <button
                type="button"
                className="underline font-medium"
                onClick={() => { setApiError(null); mutate() }}
              >
                Retry
              </button>
            </p>
          )}

          {/* Navigation */}
          <div className="flex items-center justify-between pt-2">
            <div>
              {step > 1 ? (
                <Button variant="ghost" type="button" onClick={handleBack} disabled={isPending}>
                  Back
                </Button>
              ) : (
                <button
                  type="button"
                  onClick={() => navigate('/', { replace: true })}
                  className="text-sm text-slate-400 hover:text-slate-600 transition-colors"
                >
                  Skip for now
                </button>
              )}
            </div>

            <div>
              {step < 3 ? (
                <Button
                  type="button"
                  onClick={handleNext}
                  disabled={(step === 1 && !canAdvanceStep1) || (step === 2 && !canAdvanceStep2)}
                >
                  Next
                </Button>
              ) : (
                <Button type="button" onClick={() => mutate()} disabled={isPending}>
                  {isPending ? 'Saving…' : 'Finish'}
                </Button>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
