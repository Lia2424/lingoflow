import { useCallback, useEffect, useRef, useState } from 'react'

import { useInfiniteQuery } from '@tanstack/react-query'

import { LANGUAGES } from '@/lib/languages'
import { usePreferencesStore } from '@/stores/preferencesStore'
import type { CEFRLevel, SourceType } from '@/types'

import { fetchContent } from '@/services/content'

import ContentCard from './ContentCard'
import ContentCardSkeleton from './ContentCardSkeleton'

// ── Constants ─────────────────────────────────────────────────────────────────

const CEFR_LEVELS: CEFRLevel[] = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']

const SOURCE_TYPES: { value: SourceType; label: string }[] = [
  { value: 'article', label: 'Article' },
  { value: 'podcast', label: 'Podcast' },
  { value: 'youtube', label: 'YouTube' },
  { value: 'music', label: 'Music' },
  { value: 'tv_show', label: 'TV Show' },
  { value: 'other', label: 'Other' },
]

const PAGE_SIZE = 20

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

// ── Page ──────────────────────────────────────────────────────────────────────

export default function DiscoveryPage() {
  const { selectedLanguage, selectedCEFR } = usePreferencesStore()

  const [language, setLanguage] = useState<string>(selectedLanguage ?? '')
  const [cefrLevel, setCefrLevel] = useState<string>(selectedCEFR ?? '')
  const [sourceType, setSourceType] = useState<string>('')

  // Active filters — derived so the query only re-runs when they actually change
  const filters = {
    language: language || undefined,
    cefr_level: (cefrLevel as CEFRLevel) || undefined,
    source_type: (sourceType as SourceType) || undefined,
  }

  const { data, isLoading, isFetchingNextPage, hasNextPage, fetchNextPage } = useInfiniteQuery({
    queryKey: ['content', filters],
    queryFn: ({ pageParam }) =>
      fetchContent({ ...filters, page: pageParam as number, page_size: PAGE_SIZE }),
    initialPageParam: 1,
    getNextPageParam: (lastPage, allPages) => {
      const totalPages = Math.ceil(lastPage.total / lastPage.page_size)
      return allPages.length < totalPages ? allPages.length + 1 : undefined
    },
  })

  // ── Intersection observer for auto-loading ───────────────────────────────
  const sentinelRef = useRef<HTMLDivElement>(null)

  const handleIntersection = useCallback(
    (entries: IntersectionObserverEntry[]) => {
      if (entries[0].isIntersecting && hasNextPage && !isFetchingNextPage) {
        fetchNextPage()
      }
    },
    [hasNextPage, isFetchingNextPage, fetchNextPage],
  )

  useEffect(() => {
    const el = sentinelRef.current
    if (!el) return
    const observer = new IntersectionObserver(handleIntersection, { threshold: 0.1 })
    observer.observe(el)
    return () => observer.disconnect()
  }, [handleIntersection])

  // ── Flatten pages ────────────────────────────────────────────────────────
  const items = data?.pages.flatMap((p) => p.items) ?? []
  const total = data?.pages[0]?.total ?? 0

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <div className="border-b border-slate-200 bg-white px-4 py-4 sm:px-6">
        <h1 className="text-xl font-bold text-slate-900">Discovery</h1>
        <p className="mt-0.5 text-sm text-slate-500">
          Immerse yourself in authentic content at your level
        </p>
      </div>

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

          <FilterSelect label="Type" value={sourceType} onChange={setSourceType}>
            <option value="">All types</option>
            {SOURCE_TYPES.map((t) => (
              <option key={t.value} value={t.value}>
                {t.label}
              </option>
            ))}
          </FilterSelect>

          {(language || cefrLevel || sourceType) && (
            <button
              type="button"
              onClick={() => {
                setLanguage('')
                setCefrLevel('')
                setSourceType('')
              }}
              className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-500 shadow-sm hover:bg-slate-50"
            >
              Clear filters
            </button>
          )}
        </div>
      </div>

      {/* Content grid */}
      <div className="px-4 py-6 sm:px-6">
        {/* Result count */}
        {!isLoading && items.length > 0 && (
          <p className="mb-4 text-sm text-slate-500">
            {total.toLocaleString()} {total === 1 ? 'item' : 'items'}
          </p>
        )}

        {/* Skeleton grid on first load */}
        {isLoading && (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {Array.from({ length: 8 }).map((_, i) => (
              <ContentCardSkeleton key={i} />
            ))}
          </div>
        )}

        {/* Empty state */}
        {!isLoading && items.length === 0 && (
          <div className="flex flex-col items-center justify-center py-24 text-center">
            <div className="mb-4 text-5xl">🔍</div>
            <h2 className="text-lg font-semibold text-slate-700">No content found</h2>
            <p className="mt-1 text-sm text-slate-500">
              Try adjusting your filters or check back later.
            </p>
          </div>
        )}

        {/* Content cards */}
        {items.length > 0 && (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {items.map((item) => (
              <ContentCard key={item.id} item={item} />
            ))}

            {/* Skeleton rows while fetching next page */}
            {isFetchingNextPage &&
              Array.from({ length: 4 }).map((_, i) => <ContentCardSkeleton key={`sk-${i}`} />)}
          </div>
        )}

        {/* Intersection sentinel — triggers next page fetch */}
        <div ref={sentinelRef} className="h-4" aria-hidden="true" />

        {/* End of results */}
        {!hasNextPage && items.length > 0 && (
          <p className="mt-8 text-center text-sm text-slate-400">
            You've seen all {total.toLocaleString()} items
          </p>
        )}
      </div>
    </div>
  )
}
