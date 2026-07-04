import { useState } from 'react'

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'

import { fetchReviewQueue, submitReview } from '@/services/vocabulary'
import type { VocabularyEntry } from '@/types'

import FlashCard from './FlashCard'

// ── Progress bar ──────────────────────────────────────────────────────────────

interface ProgressBarProps {
  current: number
  total: number
}

function ProgressBar({ current, total }: ProgressBarProps) {
  const pct = total === 0 ? 100 : Math.round((current / total) * 100)
  return (
    <div className="w-full">
      <div className="mb-1 flex justify-between text-xs text-slate-400">
        <span>{current} of {total} reviewed</span>
        <span>{pct}%</span>
      </div>
      <div className="h-2 w-full overflow-hidden rounded-full bg-slate-200">
        <div
          className="h-full rounded-full bg-emerald-500 transition-all duration-300"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  )
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default function ReviewPage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const { data: queue, isLoading } = useQuery({
    queryKey: ['vocabulary', 'review'],
    queryFn: fetchReviewQueue,
    // Don't re-fetch mid-session — the queue is consumed locally
    staleTime: Infinity,
  })

  // Local copy of the queue so we can pop cards off without a refetch
  const [remaining, setRemaining] = useState<VocabularyEntry[] | null>(null)
  const [reviewed, setReviewed] = useState(0)

  // Initialise `remaining` once the query resolves (runs once)
  const entries = remaining ?? queue ?? []
  const total = (remaining ?? queue ?? []).length + reviewed
  const current = entries[0] ?? null

  function initIfNeeded(fetched: VocabularyEntry[]) {
    if (remaining === null) setRemaining(fetched)
  }
  if (queue && remaining === null) initIfNeeded(queue)

  const { mutate: grade, isPending } = useMutation({
    mutationFn: ({ id, correct }: { id: string; correct: boolean }) =>
      submitReview(id, { correct }),
    onSuccess: () => {
      setRemaining((prev) => (prev ? prev.slice(1) : []))
      setReviewed((n) => n + 1)
      // Invalidate list so SRS levels refresh if the user navigates back
      queryClient.invalidateQueries({ queryKey: ['vocabulary'] })
    },
  })

  // ── Loading ────────────────────────────────────────────────────────────────
  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-slate-200 border-t-slate-600" />
      </div>
    )
  }

  // ── All done ───────────────────────────────────────────────────────────────
  if (entries.length === 0) {
    const hadCards = total > 0
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-slate-50 px-4 text-center">
        <div className="text-6xl">{hadCards ? '🎉' : '📖'}</div>
        <h1 className="text-2xl font-bold text-slate-900">
          {hadCards ? 'All caught up!' : 'Nothing to review'}
        </h1>
        <p className="max-w-xs text-sm text-slate-500">
          {hadCards
            ? `You reviewed ${reviewed} ${reviewed === 1 ? 'word' : 'words'}. Come back when the next batch is due.`
            : 'No words are due right now. Add more words or check back later.'}
        </p>
        {hadCards && (
          <div className="mt-2 w-full max-w-xs">
            <ProgressBar current={reviewed} total={reviewed} />
          </div>
        )}
        <div className="mt-2 flex gap-3">
          <button
            type="button"
            onClick={() => navigate('/vocabulary')}
            className="rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm text-slate-700 hover:bg-slate-50"
          >
            My vocabulary
          </button>
          <button
            type="button"
            onClick={() => navigate('/')}
            className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700"
          >
            Discover content
          </button>
        </div>
      </div>
    )
  }

  // ── Active session ─────────────────────────────────────────────────────────
  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <div className="border-b border-slate-200 bg-white px-4 py-4 sm:px-6">
        <div className="mx-auto flex max-w-lg items-center justify-between">
          <button
            type="button"
            onClick={() => navigate('/vocabulary')}
            className="text-sm text-slate-500 hover:text-slate-700"
          >
            ← Exit
          </button>
          <h1 className="text-sm font-semibold text-slate-700">Flashcard Review</h1>
          <span className="text-sm text-slate-400">
            {entries.length} left
          </span>
        </div>
      </div>

      {/* Progress + card */}
      <div className="mx-auto flex max-w-lg flex-col gap-8 px-4 py-10 sm:px-6">
        <ProgressBar current={reviewed} total={total} />

        <FlashCard
          key={current.id}
          entry={current}
          onCorrect={() => grade({ id: current.id, correct: true })}
          onIncorrect={() => grade({ id: current.id, correct: false })}
          isSubmitting={isPending}
        />
      </div>
    </div>
  )
}
