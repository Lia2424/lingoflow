import { useNavigate } from 'react-router-dom'

import type { ContentItem, SourceType } from '@/types'

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

const SOURCE_LABELS: Record<SourceType, string> = {
  article: 'Article',
  podcast: 'Podcast',
  youtube: 'YouTube',
  music: 'Music',
  tv_show: 'TV Show',
  other: 'Other',
}

const SOURCE_COLORS: Record<SourceType, string> = {
  article: 'bg-blue-100 text-blue-700',
  podcast: 'bg-purple-100 text-purple-700',
  youtube: 'bg-red-100 text-red-700',
  music: 'bg-green-100 text-green-700',
  tv_show: 'bg-orange-100 text-orange-700',
  other: 'bg-slate-100 text-slate-600',
}

const SOURCE_GRADIENTS: Record<SourceType, string> = {
  article: 'from-blue-400 to-blue-600',
  podcast: 'from-purple-400 to-purple-600',
  youtube: 'from-red-400 to-red-600',
  music: 'from-green-400 to-green-600',
  tv_show: 'from-orange-400 to-orange-600',
  other: 'from-slate-400 to-slate-600',
}

const CEFR_COLORS: Record<string, string> = {
  A1: 'bg-emerald-100 text-emerald-700',
  A2: 'bg-emerald-100 text-emerald-700',
  B1: 'bg-amber-100 text-amber-700',
  B2: 'bg-amber-100 text-amber-700',
  C1: 'bg-rose-100 text-rose-700',
  C2: 'bg-rose-100 text-rose-700',
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
