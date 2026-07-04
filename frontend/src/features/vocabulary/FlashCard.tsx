import { useState } from 'react'

import type { VocabularyEntry } from '@/types'

interface FlashCardProps {
  entry: VocabularyEntry
  onCorrect: () => void
  onIncorrect: () => void
  isSubmitting: boolean
}

export default function FlashCard({
  entry,
  onCorrect,
  onIncorrect,
  isSubmitting,
}: FlashCardProps) {
  const [revealed, setRevealed] = useState(false)

  function handleReveal() {
    setRevealed(true)
  }

  function handleGrade(correct: boolean) {
    if (correct) onCorrect()
    else onIncorrect()
    // No need to reset `revealed` here — the parent keys FlashCard by entry.id,
    // so the component unmounts and remounts for each new card automatically.
  }

  return (
    <div className="flex flex-col items-center gap-6">
      {/* Card */}
      <div
        className="relative w-full max-w-md"
        style={{ perspective: '1000px' }}
      >
        <div
          className="relative w-full transition-transform duration-500"
          style={{
            transformStyle: 'preserve-3d',
            transform: revealed ? 'rotateY(180deg)' : 'rotateY(0deg)',
            minHeight: '220px',
          }}
        >
          {/* Front — word */}
          <div
            className="absolute inset-0 flex flex-col items-center justify-center rounded-2xl border border-slate-200 bg-white p-8 shadow-md"
            style={{ backfaceVisibility: 'hidden' }}
          >
            <span className="mb-2 text-xs font-medium uppercase tracking-wider text-slate-400">
              {entry.language}
            </span>
            <p className="text-3xl font-bold text-slate-900">{entry.word}</p>
            {entry.notes && (
              <p className="mt-3 text-xs text-slate-400 italic">{entry.notes}</p>
            )}
          </div>

          {/* Back — definition + translation */}
          <div
            className="absolute inset-0 flex flex-col items-center justify-center gap-3 rounded-2xl border border-slate-200 bg-white p-8 shadow-md"
            style={{
              backfaceVisibility: 'hidden',
              transform: 'rotateY(180deg)',
            }}
          >
            <span className="text-xs font-medium uppercase tracking-wider text-slate-400">
              {entry.language}
            </span>
            <p className="text-3xl font-bold text-slate-900">{entry.word}</p>
            {entry.definition && (
              <p className="mt-1 text-center text-base text-slate-700">
                {entry.definition}
              </p>
            )}
            {entry.translation && (
              <p className="text-sm italic text-slate-400">{entry.translation}</p>
            )}
          </div>
        </div>
      </div>

      {/* Actions */}
      {!revealed ? (
        <button
          type="button"
          onClick={handleReveal}
          className="rounded-xl bg-slate-900 px-8 py-3 text-sm font-medium text-white shadow-sm hover:bg-slate-700 transition-colors"
        >
          Reveal answer
        </button>
      ) : (
        <div className="flex gap-4">
          <button
            type="button"
            disabled={isSubmitting}
            onClick={() => handleGrade(false)}
            className="rounded-xl border-2 border-red-200 bg-red-50 px-8 py-3 text-sm font-semibold text-red-600 hover:bg-red-100 disabled:opacity-50 transition-colors"
          >
            ✗ Missed it
          </button>
          <button
            type="button"
            disabled={isSubmitting}
            onClick={() => handleGrade(true)}
            className="rounded-xl border-2 border-emerald-200 bg-emerald-50 px-8 py-3 text-sm font-semibold text-emerald-700 hover:bg-emerald-100 disabled:opacity-50 transition-colors"
          >
            ✓ Got it
          </button>
        </div>
      )}
    </div>
  )
}
