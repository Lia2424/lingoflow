import type { SourceType } from '@/types'

export const SOURCE_LABELS: Record<SourceType, string> = {
  article: 'Article',
  podcast: 'Podcast',
  youtube: 'YouTube',
  music: 'Music',
  tv_show: 'TV Show',
  other: 'Other',
}

export const SOURCE_COLORS: Record<SourceType, string> = {
  article: 'bg-blue-100 text-blue-700',
  podcast: 'bg-purple-100 text-purple-700',
  youtube: 'bg-red-100 text-red-700',
  music: 'bg-green-100 text-green-700',
  tv_show: 'bg-orange-100 text-orange-700',
  other: 'bg-slate-100 text-slate-600',
}

export const SOURCE_GRADIENTS: Record<SourceType, string> = {
  article: 'from-blue-400 to-blue-600',
  podcast: 'from-purple-400 to-purple-600',
  youtube: 'from-red-400 to-red-600',
  music: 'from-green-400 to-green-600',
  tv_show: 'from-orange-400 to-orange-600',
  other: 'from-slate-400 to-slate-600',
}

export const CEFR_COLORS: Record<string, string> = {
  A1: 'bg-emerald-100 text-emerald-700',
  A2: 'bg-emerald-100 text-emerald-700',
  B1: 'bg-amber-100 text-amber-700',
  B2: 'bg-amber-100 text-amber-700',
  C1: 'bg-rose-100 text-rose-700',
  C2: 'bg-rose-100 text-rose-700',
}
