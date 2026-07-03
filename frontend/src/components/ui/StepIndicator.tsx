interface StepIndicatorProps {
  currentStep: number
  totalSteps: number
  labels?: string[]
}

export default function StepIndicator({ currentStep, totalSteps, labels }: StepIndicatorProps) {
  return (
    <div className="flex items-center justify-center gap-2" aria-label="Progress">
      {Array.from({ length: totalSteps }, (_, i) => {
        const step = i + 1
        const isComplete = step < currentStep
        const isActive = step === currentStep

        return (
          <div key={step} className="flex items-center gap-2">
            <div className="flex flex-col items-center gap-1">
              <div
                aria-current={isActive ? 'step' : undefined}
                className={`flex h-7 w-7 items-center justify-center rounded-full text-xs font-semibold transition-colors ${
                  isComplete
                    ? 'bg-slate-800 text-white'
                    : isActive
                      ? 'bg-slate-900 text-white ring-2 ring-slate-300 ring-offset-2'
                      : 'bg-slate-100 text-slate-400'
                }`}
              >
                {isComplete ? (
                  <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                  </svg>
                ) : (
                  step
                )}
              </div>
              {labels?.[i] && (
                <span className={`text-xs ${isActive ? 'text-slate-700 font-medium' : 'text-slate-400'}`}>
                  {labels[i]}
                </span>
              )}
            </div>

            {step < totalSteps && (
              <div
                className={`h-px w-8 transition-colors ${isComplete ? 'bg-slate-800' : 'bg-slate-200'}`}
              />
            )}
          </div>
        )
      })}
    </div>
  )
}
