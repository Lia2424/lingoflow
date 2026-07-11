import { useState } from 'react'

import { useMutation } from '@tanstack/react-query'

import { fetchContentQuestions } from '@/services/content'
import type { ContentQuestion } from '@/types'

interface QuestionsSectionProps {
  contentId: string
}

function getErrorMessage(err: unknown, fallback: string): string {
  return (
    (err as { response?: { data?: { detail?: string } } })?.response?.data
      ?.detail ?? fallback
  )
}

export default function QuestionsSection({ contentId }: QuestionsSectionProps) {
  const [questions, setQuestions] = useState<ContentQuestion[]>([])
  const [phase, setPhase] = useState<'idle' | 'quiz' | 'summary'>('idle')
  const [currentIndex, setCurrentIndex] = useState(0)
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null)
  const [results, setResults] = useState<boolean[]>([])

  const { mutate: loadQuiz, isPending, error, reset } = useMutation({
    mutationFn: () => fetchContentQuestions(contentId),
    onSuccess: (data) => {
      setQuestions(data)
      setCurrentIndex(0)
      setSelectedIndex(null)
      setResults([])
      setPhase('quiz')
    },
  })

  function handleGenerate() {
    reset()
    loadQuiz()
  }

  const current = questions[currentIndex]
  const hasAnswered = selectedIndex !== null
  const score = results.filter(Boolean).length

  function handleSelect(optionIndex: number) {
    if (!current || hasAnswered) return
    setSelectedIndex(optionIndex)
    setResults((prev) => {
      const next = [...prev]
      next[currentIndex] = optionIndex === current.answer_index
      return next
    })
  }

  function handleNext() {
    if (currentIndex >= questions.length - 1) {
      setPhase('summary')
      return
    }
    setCurrentIndex((i) => i + 1)
    setSelectedIndex(null)
  }

  function handleTryAgain() {
    setCurrentIndex(0)
    setSelectedIndex(null)
    setResults([])
    setPhase('quiz')
  }

  function handleStartOver() {
    setQuestions([])
    setCurrentIndex(0)
    setSelectedIndex(null)
    setResults([])
    setPhase('idle')
  }

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5">
      <h2 className="mb-1 text-sm font-semibold uppercase tracking-wide text-slate-500">
        Comprehension quiz
      </h2>
      <p className="mb-4 text-xs text-slate-400">
        Test your understanding of this content with AI-generated questions.
      </p>

      {phase === 'idle' && (
        <div className="flex flex-col gap-3">
          <button
            type="button"
            onClick={handleGenerate}
            disabled={isPending}
            className="w-fit cursor-pointer rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isPending ? 'Generating…' : 'Generate quiz'}
          </button>
          {error && (
            <p className="rounded-lg bg-amber-50 px-3 py-2 text-sm text-amber-800">
              {getErrorMessage(error, 'Could not generate quiz. Please try again.')}
            </p>
          )}
        </div>
      )}

      {phase === 'quiz' && current && (
        <div className="flex flex-col gap-4">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>
              Question {currentIndex + 1} of {questions.length}
            </span>
            <span>{Math.round(((currentIndex + (hasAnswered ? 1 : 0)) / questions.length) * 100)}%</span>
          </div>

          <div className="h-1.5 w-full overflow-hidden rounded-full bg-slate-200">
            <div
              className="h-full rounded-full bg-emerald-500 transition-all duration-300"
              style={{
                width: `${((currentIndex + (hasAnswered ? 1 : 0)) / questions.length) * 100}%`,
              }}
            />
          </div>

          <p className="text-base font-medium text-slate-900">{current.question}</p>

          <div className="flex flex-col gap-2">
            {current.options.map((option, index) => {
              let optionClass =
                'cursor-pointer rounded-lg border px-4 py-3 text-left text-sm transition-colors '

              if (!hasAnswered) {
                optionClass +=
                  'border-slate-200 bg-white text-slate-700 hover:border-slate-300 hover:bg-slate-50'
              } else if (index === current.answer_index) {
                optionClass += 'border-emerald-300 bg-emerald-50 text-emerald-800'
              } else if (index === selectedIndex) {
                optionClass += 'border-red-300 bg-red-50 text-red-700'
              } else {
                optionClass += 'border-slate-200 bg-slate-50 text-slate-400'
              }

              return (
                <button
                  key={index}
                  type="button"
                  disabled={hasAnswered}
                  onClick={() => handleSelect(index)}
                  className={optionClass}
                >
                  {option}
                </button>
              )
            })}
          </div>

          {hasAnswered && (
            <div className="flex flex-col gap-3 border-t border-slate-100 pt-3">
              <p
                className={`text-sm font-medium ${
                  results[currentIndex] ? 'text-emerald-700' : 'text-red-600'
                }`}
              >
                {results[currentIndex] ? '✓ Correct!' : '✗ Not quite.'}
              </p>
              <button
                type="button"
                onClick={handleNext}
                className="w-fit cursor-pointer rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700"
              >
                {currentIndex >= questions.length - 1 ? 'See results' : 'Next question'}
              </button>
            </div>
          )}
        </div>
      )}

      {phase === 'summary' && (
        <div className="flex flex-col items-center gap-4 py-4 text-center">
          <div className="text-5xl">{score === questions.length ? '🎉' : '📚'}</div>
          <h3 className="text-lg font-semibold text-slate-900">Quiz complete</h3>
          <p className="text-sm text-slate-600">
            You got <span className="font-semibold text-slate-900">{score}</span> out of{' '}
            <span className="font-semibold text-slate-900">{questions.length}</span> correct
          </p>
          <div className="flex gap-3">
            <button
              type="button"
              onClick={handleTryAgain}
              className="cursor-pointer rounded-lg border border-slate-200 px-4 py-2 text-sm text-slate-700 hover:bg-slate-50"
            >
              Try again
            </button>
            <button
              type="button"
              onClick={handleStartOver}
              className="cursor-pointer rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700"
            >
              Done
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
