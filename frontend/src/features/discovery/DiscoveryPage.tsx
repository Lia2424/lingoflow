import { useEffect, useRef, useState } from 'react'

import { useQueries } from '@tanstack/react-query'

import { LANGUAGES } from '@/lib/languages'
import { usePreferencesStore } from '@/stores/preferencesStore'
import type { CEFRLevel, ContentItem, SourceType } from '@/types'

import { fetchContent } from '@/services/content'

import ContentCard from './ContentCard'
import ContentCardSkeleton from './ContentCardSkeleton'

// ── Constants ─────────────────────────────────────────────────────────────────

const CEFR_LEVELS: CEFRLevel[] = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']

const ROWS: { type: SourceType; label: string; emoji: string }[] = [
  { type: 'youtube', label: 'YouTube', emoji: '▶️' },
  { type: 'podcast', label: 'Podcasts', emoji: '🎙️' },
  { type: 'music', label: 'Music', emoji: '🎵' },
  { type: 'tv_show', label: 'TV Shows', emoji: '📺' },
  { type: 'article', label: 'Articles', emoji: '📰' },
  { type: 'other', label: 'Other', emoji: '🔗' },
]

const ROW_SIZE = 12

// ── Filter bar ────────────────────────────────────────────────────────────────

interface FilterSelectProps {
  label: string
  value: string
  onChange: (v: string) => void
  children: React.ReactNode
}

function FilterSelect({ label, value, onChange, children }: FilterSelectProps) {
  return (
    <label className="flex flex-col gap-1 text-xs font-medium text-slate-500">
      {label}
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 shadow-sm focus:outline-none focus:ring-2 focus:ring-slate-400"
      >
        {children}
      </select>
    </label>
  )
}

// ── Content row ───────────────────────────────────────────────────────────────

const SCROLL_AMOUNT = 320

interface ContentRowProps {
  label: string
  emoji: string
  items: ContentItem[]
  isLoading: boolean
}

function ContentRow({ label, emoji, items, isLoading }: ContentRowProps) {
  const trackRef = useRef<HTMLDivElement>(null)
  const [canScroll, setCanScroll] = useState(false)

  useEffect(() => {
    const el = trackRef.current
    if (!el) return
    const check = () => setCanScroll(el.scrollWidth > el.clientWidth)
    check()
    const ro = new ResizeObserver(check)
    ro.observe(el)
    return () => ro.disconnect()
  }, [items])

  if (!isLoading && items.length === 0) return null

  function scroll(dir: 'left' | 'right') {
    trackRef.current?.scrollBy({
      left: dir === 'right' ? SCROLL_AMOUNT : -SCROLL_AMOUNT,
      behavior: 'smooth',
    })
  }

  return (
    <section className="py-6">
      {/* Row header */}
      <div className="mb-3 flex items-center gap-2 px-4 sm:px-6">
        <span className="text-xl" aria-hidden="true">{emoji}</span>
        <h2 className="text-lg font-bold text-slate-900">{label}</h2>
      </div>

      {/* Scroll area with arrow buttons */}
      <div className="group relative">
        {/* Left arrow */}
        <button
          type="button"
          onClick={() => scroll('left')}
          aria-label={`Scroll ${label} left`}
          className={`absolute left-1 top-1/2 z-10 -translate-y-1/2 rounded-full bg-white/90 p-2 shadow-md ring-1 ring-slate-200 transition-opacity hover:bg-white focus-visible:opacity-100 ${canScroll ? 'opacity-0 group-hover:opacity-100' : 'hidden'}`}
        >
          <svg className="h-4 w-4 text-slate-700" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
          </svg>
        </button>

        {/* Horizontal scroll track */}
        <div
          ref={trackRef}
          className="flex gap-4 overflow-x-auto pb-3 scrollbar-hide"
          style={{ paddingLeft: '1rem', paddingRight: '1rem' }}
        >
          {isLoading
            ? Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="w-64 shrink-0 sm:w-72 h-72">
                  <ContentCardSkeleton />
                </div>
              ))
            : items.map((item) => (
                <div key={item.id} className="w-64 shrink-0 sm:w-72 h-72">
                  <ContentCard item={item} />
                </div>
              ))}
        </div>

        {/* Right arrow */}
        <button
          type="button"
          onClick={() => scroll('right')}
          aria-label={`Scroll ${label} right`}
          className={`absolute right-1 top-1/2 z-10 -translate-y-1/2 rounded-full bg-white/90 p-2 shadow-md ring-1 ring-slate-200 transition-opacity hover:bg-white focus-visible:opacity-100 ${canScroll ? 'opacity-0 group-hover:opacity-100' : 'hidden'}`}
        >
          <svg className="h-4 w-4 text-slate-700" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
          </svg>
        </button>
      </div>
    </section>
  )
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default function DiscoveryPage() {
  const { selectedLanguage, selectedCEFR } = usePreferencesStore()

  const [language, setLanguage] = useState<string>(selectedLanguage ?? '')
  const [cefrLevel, setCefrLevel] = useState<string>(selectedCEFR ?? '')

  const sharedFilters = {
    language: language || undefined,
    cefr_level: (cefrLevel as CEFRLevel) || undefined,
    page_size: ROW_SIZE,
  }

  // One query per source type — all run in parallel
  const results = useQueries({
    queries: ROWS.map((row) => ({
      queryKey: ['content', { ...sharedFilters, source_type: row.type }],
      queryFn: () =>
        fetchContent({ ...sharedFilters, source_type: row.type, page: 1 }),
    })),
  })

  const allLoading = results.every((r) => r.isLoading)
  const anyItems = results.some((r) => (r.data?.items.length ?? 0) > 0)

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Filter bar */}
      <div className="border-b border-slate-200 bg-white px-4 py-3 sm:px-6">
        <div className="flex flex-wrap items-end gap-3">
          <FilterSelect label="Language" value={language} onChange={setLanguage}>
            <option value="">All languages</option>
            {LANGUAGES.map((l) => (
              <option key={l.code} value={l.code}>
                {l.name}
              </option>
            ))}
          </FilterSelect>

          <FilterSelect label="CEFR Level" value={cefrLevel} onChange={setCefrLevel}>
            <option value="">All levels</option>
            {CEFR_LEVELS.map((lvl) => (
              <option key={lvl} value={lvl}>
                {lvl}
              </option>
            ))}
          </FilterSelect>

          {(language || cefrLevel) && (
            <button
              type="button"
              onClick={() => {
                setLanguage('')
                setCefrLevel('')
              }}
              className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-500 shadow-sm hover:bg-slate-50"
            >
              Clear filters
            </button>
          )}
        </div>
      </div>

      {/* Rows */}
      <div className="divide-y divide-slate-100">
        {ROWS.map((row, i) => (
          <ContentRow
            key={row.type}
            label={row.label}
            emoji={row.emoji}
            items={results[i].data?.items ?? []}
            isLoading={results[i].isLoading}
          />
        ))}
      </div>

      {/* Global empty state — shown only when all queries finished with zero results */}
      {!allLoading && !anyItems && (
        <div className="flex flex-col items-center justify-center py-24 text-center">
          <div className="mb-4 text-5xl">🔍</div>
          <h2 className="text-lg font-semibold text-slate-700">No content found</h2>
          <p className="mt-1 text-sm text-slate-500">
            Try adjusting your filters or check back later.
          </p>
        </div>
      )}
    </div>
  )
}
