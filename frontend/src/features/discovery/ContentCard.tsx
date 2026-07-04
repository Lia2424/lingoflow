import { useNavigate } from 'react-router-dom'

import { CEFR_COLORS, SOURCE_COLORS, SOURCE_GRADIENTS, SOURCE_LABELS } from '@/lib/contentDisplay'
import type { ContentItem } from '@/types'

// ── Helpers ──────────────────────────────────────────────────────────────────

function formatDuration(seconds: number | null): string | null {
  if (seconds == null) return null
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return m >= 60
    ? `${Math.floor(m / 60)}h ${m % 60}m`
    : s === 0
      ? `${m} min`
      : `${m}:${String(s).padStart(2, '0')}`
}

// ── Component ─────────────────────────────────────────────────────────────────

interface ContentCardProps {
  item: ContentItem
}

export default function ContentCard({ item }: ContentCardProps) {
  const navigate = useNavigate()
  const duration = formatDuration(item.duration_seconds)

  return (
    <button
      type="button"
      onClick={() => navigate(`/content/${item.id}`)}
      className="group flex w-full flex-col overflow-hidden rounded-xl border border-slate-200 bg-white text-left shadow-sm transition-shadow hover:shadow-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-400"
    >
      {/* Thumbnail */}
      <div className="relative aspect-video w-full overflow-hidden bg-slate-100">
        {item.thumbnail_url ? (
          <img
            src={item.thumbnail_url}
            alt={item.title}
            className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
            loading="lazy"
          />
        ) : (
          <div
            className={`flex h-full w-full items-center justify-center bg-gradient-to-br ${SOURCE_GRADIENTS[item.source_type]}`}
          >
            <span className="text-4xl text-white/80 select-none">
              {SOURCE_LABELS[item.source_type][0]}
            </span>
          </div>
        )}
        {duration && (
          <span className="absolute bottom-2 right-2 rounded bg-black/60 px-1.5 py-0.5 text-xs font-medium text-white">
            {duration}
          </span>
        )}
      </div>

      {/* Body */}
      <div className="flex flex-1 flex-col gap-2 p-3">
        {/* Badges */}
        <div className="flex flex-wrap gap-1.5">
          <span
            className={`rounded-full px-2 py-0.5 text-xs font-medium ${SOURCE_COLORS[item.source_type]}`}
          >
            {SOURCE_LABELS[item.source_type]}
          </span>
          <span
            className={`rounded-full px-2 py-0.5 text-xs font-medium ${CEFR_COLORS[item.cefr_level]}`}
          >
            {item.cefr_level}
          </span>
          <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-500 uppercase">
            {item.language}
          </span>
        </div>

        {/* Title */}
        <p className="line-clamp-2 text-sm font-semibold text-slate-800 leading-snug">
          {item.title}
        </p>

        {/* Description */}
        {item.description && (
          <p className="line-clamp-2 text-xs text-slate-500">{item.description}</p>
        )}
      </div>
    </button>
  )
}
