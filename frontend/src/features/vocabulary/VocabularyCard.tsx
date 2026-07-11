import type { SRSLevel, VocabularyEntry } from '@/types'

// ── Helpers ───────────────────────────────────────────────────────────────────

const SRS_LABELS: Record<SRSLevel, string> = {
  0: 'New',
  1: 'Level 1',
  2: 'Level 2',
  3: 'Level 3',
  4: 'Level 4',
  5: 'Mastered',
}

const SRS_COLORS: Record<SRSLevel, string> = {
  0: 'bg-slate-200 text-slate-600',
  1: 'bg-red-100 text-red-600',
  2: 'bg-orange-100 text-orange-600',
  3: 'bg-amber-100 text-amber-600',
  4: 'bg-emerald-100 text-emerald-700',
  5: 'bg-emerald-600 text-white',
}

function daysUntilReview(nextReviewAt: string | null): string {
  if (!nextReviewAt) return 'Due now'
  const diff = new Date(nextReviewAt).getTime() - Date.now()
  const days = Math.ceil(diff / (1000 * 60 * 60 * 24))
  if (days <= 0) return 'Due now'
  if (days === 1) return 'Due tomorrow'
  return `Due in ${days} days`
}

// ── Component ─────────────────────────────────────────────────────────────────

interface VocabularyCardProps {
  entry: VocabularyEntry
  onEdit: (entry: VocabularyEntry) => void
  onDelete: (id: string) => void
  isDeleting: boolean
}

export default function VocabularyCard({
  entry,
  onEdit,
  onDelete,
  isDeleting,
}: VocabularyCardProps) {
  const level = entry.srs_level as SRSLevel

  return (
    <div className="flex flex-col gap-3 rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      {/* Top row: word + badges */}
      <div className="flex items-start justify-between gap-2">
        <p className="text-base font-semibold text-slate-900 leading-snug">
          {entry.word}
        </p>
        <div className="flex shrink-0 flex-wrap justify-end gap-1.5">
          <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-500 uppercase">
            {entry.language}
          </span>
          <span
            className={`rounded-full px-2 py-0.5 text-xs font-medium ${SRS_COLORS[level]}`}
          >
            {SRS_LABELS[level]}
          </span>
        </div>
      </div>

      {/* Definition / translation */}
      {(entry.definition || entry.translation) && (
        <div className="space-y-0.5">
          {entry.definition && (
            <p className="text-sm text-slate-700">{entry.definition}</p>
          )}
          {entry.translation && (
            <p className="text-xs text-slate-400 italic">{entry.translation}</p>
          )}
        </div>
      )}

      {/* Notes */}
      {entry.notes && (
        <p className="text-xs text-slate-500 border-t border-slate-100 pt-2">
          {entry.notes}
        </p>
      )}

      {/* Footer: due date + actions */}
      <div className="flex items-center justify-between border-t border-slate-100 pt-2">
        <span className="text-xs text-slate-400">{daysUntilReview(entry.next_review_at)}</span>
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={() => onEdit(entry)}
            className="text-xs text-slate-500 hover:text-slate-700 transition-colors"
          >
            Edit
          </button>
          <button
            type="button"
            disabled={isDeleting}
            onClick={() => onDelete(entry.id)}
            className="text-xs text-red-400 hover:text-red-600 disabled:opacity-40 transition-colors"
          >
            Remove
          </button>
        </div>
      </div>
    </div>
  )
}
