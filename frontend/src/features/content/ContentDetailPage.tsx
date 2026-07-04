import { useState } from 'react'

import axios from 'axios'
import { useNavigate, useParams } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { CEFR_COLORS, SOURCE_COLORS, SOURCE_LABELS } from '@/lib/contentDisplay'
import type { InteractionStatus } from '@/types'
import { fetchContentById, interactWithContent } from '@/services/content'

import ContentDetailSkeleton from './ContentDetailSkeleton'

// ── Helpers ──────────────────────────────────────────────────────────────────

function getYouTubeId(url: string): string | null {
  const patterns = [
    /[?&]v=([^&]+)/,
    /youtu\.be\/([^?/]+)/,
    /\/embed\/([^?/]+)/,
    /\/shorts\/([^?/]+)/,
  ]
  for (const p of patterns) {
    const m = url.match(p)
    if (m) return m[1]
  }
  return null
}

function formatDate(iso: string | null): string {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}

// ── Action bar ────────────────────────────────────────────────────────────────

interface ActionBarProps {
  contentId: string
  currentStatus: InteractionStatus | null
  onStatusChange: (s: InteractionStatus | null) => void
}

function ActionBar({ contentId, currentStatus, onStatusChange }: ActionBarProps) {
  const queryClient = useQueryClient()

  const { mutate, isPending } = useMutation({
    mutationFn: (status: InteractionStatus) =>
      interactWithContent(contentId, { status }),
    onMutate: (status) => {
      // Capture the pre-click status as mutation context — reading
      // `currentStatus` inside onError instead would be stale, since by
      // the time onError fires the prop has already been optimistically
      // updated to the new value (TanStack Query always uses the latest
      // render's callbacks), making a "revert to currentStatus" a no-op.
      const previousStatus = currentStatus
      onStatusChange(status)
      return { previousStatus }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['content', contentId] })
    },
    onError: (_err, _vars, context) => {
      onStatusChange(context?.previousStatus ?? null)
    },
  })

  const btn = (
    label: string,
    status: InteractionStatus,
    activeClass: string,
  ) => {
    const isActive = currentStatus === status
    return (
      <button
        type="button"
        disabled={isPending}
        onClick={() => mutate(status)}
        className={`rounded-lg px-4 py-2 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-slate-400 disabled:opacity-50 ${
          isActive
            ? activeClass
            : 'border border-slate-200 bg-white text-slate-700 hover:bg-slate-50'
        }`}
      >
        {label}
      </button>
    )
  }

  return (
    <div className="flex flex-wrap gap-3">
      {btn('Save', 'saved', 'bg-slate-900 text-white')}
      {btn('Mark complete', 'completed', 'bg-emerald-600 text-white')}
      {btn('In progress', 'in_progress', 'bg-amber-500 text-white')}
    </div>
  )
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default function ContentDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()

  const [interactionStatus, setInteractionStatus] = useState<InteractionStatus | null>(null)

  const { data: item, isLoading, error } = useQuery({
    queryKey: ['content', id],
    queryFn: () => fetchContentById(id!),
    enabled: !!id,
    retry: (failCount, err) => {
      // Don't retry 404s
      if (axios.isAxiosError(err) && err.response?.status === 404) return false
      return failCount < 2
    },
  })

  // ── Loading ──────────────────────────────────────────────────────────────
  if (isLoading) return <ContentDetailSkeleton />

  // ── 404 ──────────────────────────────────────────────────────────────────
  const is404 = axios.isAxiosError(error) && error.response?.status === 404
  if (is404 || (!isLoading && !item)) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-3 bg-slate-50 text-center">
        <div className="text-5xl">🔍</div>
        <h1 className="text-xl font-semibold text-slate-800">Content not found</h1>
        <p className="text-sm text-slate-500">
          This item may have been removed or the link is invalid.
        </p>
        <button
          type="button"
          onClick={() => navigate('/')}
          className="mt-2 rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm hover:bg-slate-50"
        >
          Back to discovery
        </button>
      </div>
    )
  }

  // ── Generic error ─────────────────────────────────────────────────────────
  if (error) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-3 bg-slate-50 text-center">
        <p className="text-sm text-slate-500">Something went wrong. Please try again.</p>
        <button
          type="button"
          onClick={() => navigate(-1)}
          className="rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm text-slate-700 hover:bg-slate-50"
        >
          Go back
        </button>
      </div>
    )
  }

  if (!item) return null

  const ytId = item.source_type === 'youtube' ? getYouTubeId(item.url) : null

  return (
    <div className="min-h-screen bg-slate-50">
      {/* ── Header ─────────────────────────────────────────────────────── */}
      <div className="border-b border-slate-200 bg-white px-4 py-6 sm:px-6">
        <div className="mx-auto max-w-4xl">
          {/* Back */}
          <button
            type="button"
            onClick={() => navigate(-1)}
            className="mb-4 flex items-center gap-1 text-sm text-slate-500 hover:text-slate-700"
          >
            ← Back
          </button>

          {/* Badges */}
          <div className="mb-3 flex flex-wrap gap-2">
            <span
              className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${SOURCE_COLORS[item.source_type]}`}
            >
              {SOURCE_LABELS[item.source_type]}
            </span>
            <span
              className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${CEFR_COLORS[item.cefr_level]}`}
            >
              {item.cefr_level}
            </span>
            <span className="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-500 uppercase">
              {item.language}
            </span>
          </div>

          {/* Title */}
          <h1 className="text-2xl font-bold text-slate-900 sm:text-3xl">{item.title}</h1>

          {/* Published date */}
          {item.published_at && (
            <p className="mt-2 text-sm text-slate-500">{formatDate(item.published_at)}</p>
          )}
        </div>
      </div>

      {/* ── Body ───────────────────────────────────────────────────────── */}
      <div className="mx-auto max-w-4xl space-y-6 px-4 py-6 sm:px-6">
        {/* Media section */}
        {ytId ? (
          <div className="overflow-hidden rounded-xl shadow-sm">
            <div className="relative aspect-video w-full">
              <iframe
                src={`https://www.youtube-nocookie.com/embed/${ytId}`}
                title={item.title}
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
                className="absolute inset-0 h-full w-full border-0"
              />
            </div>
          </div>
        ) : (
          <div className="flex">
            <a
              href={item.url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-2.5 text-sm font-medium text-slate-700 shadow-sm transition-colors hover:bg-slate-50"
            >
              Open {SOURCE_LABELS[item.source_type]}
              <span aria-hidden="true">↗</span>
            </a>
          </div>
        )}

        {/* Description */}
        {item.description && (
          <div className="rounded-xl border border-slate-200 bg-white p-5">
            <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-slate-500">
              About
            </h2>
            <p className="text-sm leading-relaxed text-slate-700">{item.description}</p>
          </div>
        )}

        {/* Action bar */}
        <div className="rounded-xl border border-slate-200 bg-white p-5">
          <h2 className="mb-3 text-sm font-semibold uppercase tracking-wide text-slate-500">
            Track progress
          </h2>
          <ActionBar
            contentId={item.id}
            currentStatus={interactionStatus}
            onStatusChange={setInteractionStatus}
          />
        </div>
      </div>
    </div>
  )
}
