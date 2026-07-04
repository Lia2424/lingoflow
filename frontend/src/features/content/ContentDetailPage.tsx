import { useState } from 'react'

import axios from 'axios'
import { useNavigate, useParams } from 'react-router-dom'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { CEFR_COLORS, SOURCE_COLORS, SOURCE_LABELS } from '@/lib/contentDisplay'
import { addVocabularyEntry } from '@/services/vocabulary'
import { LANGUAGES } from '@/lib/languages'
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

// ── Save-word modal ───────────────────────────────────────────────────────────

interface SaveWordModalProps {
  contentId: string
  defaultLanguage: string
  onClose: () => void
}

function SaveWordModal({ contentId, defaultLanguage, onClose }: SaveWordModalProps) {
  const queryClient = useQueryClient()

  const [word, setWord] = useState('')
  const [language, setLanguage] = useState(defaultLanguage)
  const [definition, setDefinition] = useState('')
  const [translation, setTranslation] = useState('')
  const [notes, setNotes] = useState('')
  const [error, setError] = useState<string | null>(null)

  const { mutate, isPending } = useMutation({
    mutationFn: () =>
      addVocabularyEntry({
        word: word.trim(),
        language,
        definition: definition || null,
        translation: translation || null,
        notes: notes || null,
        content_id: contentId,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vocabulary'] })
      onClose()
    },
    onError: (err: unknown) => {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data
          ?.detail ?? 'Failed to save word. Please try again.'
      setError(msg)
    },
  })

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    if (!word.trim()) return
    mutate()
  }

  const inputClass =
    'w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-400'

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="w-full max-w-md rounded-2xl bg-white shadow-xl">
        <div className="flex items-center justify-between border-b border-slate-100 px-5 py-4">
          <h2 className="text-base font-semibold text-slate-900">Save a word</h2>
          <button
            type="button"
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600"
            aria-label="Close"
          >
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4 p-5">
          {error && (
            <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">{error}</p>
          )}

          <div className="flex gap-3">
            <div className="flex-1">
              <label className="mb-1 block text-xs font-medium text-slate-500">
                Word <span className="text-red-400">*</span>
              </label>
              <input
                value={word}
                onChange={(e) => setWord(e.target.value)}
                placeholder="e.g. amistad"
                required
                maxLength={200}
                autoFocus
                className={inputClass}
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-500">
                Language <span className="text-red-400">*</span>
              </label>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-slate-400"
              >
                {LANGUAGES.map((l) => (
                  <option key={l.code} value={l.code}>
                    {l.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="mb-1 block text-xs font-medium text-slate-500">Definition</label>
            <input
              value={definition}
              onChange={(e) => setDefinition(e.target.value)}
              placeholder="e.g. friendship"
              maxLength={2000}
              className={inputClass}
            />
          </div>

          <div>
            <label className="mb-1 block text-xs font-medium text-slate-500">Translation</label>
            <input
              value={translation}
              onChange={(e) => setTranslation(e.target.value)}
              placeholder="e.g. friendship (EN)"
              maxLength={2000}
              className={inputClass}
            />
          </div>

          <div>
            <label className="mb-1 block text-xs font-medium text-slate-500">Notes</label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Any extra context…"
              rows={2}
              maxLength={2000}
              className={`${inputClass} resize-none`}
            />
          </div>

          <div className="flex justify-end gap-2 border-t border-slate-100 pt-3">
            <button
              type="button"
              onClick={onClose}
              className="rounded-lg border border-slate-200 px-4 py-2 text-sm text-slate-600 hover:bg-slate-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isPending || !word.trim()}
              className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700 disabled:opacity-50"
            >
              {isPending ? 'Saving…' : 'Save word'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
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
  const [showSaveWord, setShowSaveWord] = useState(false)

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

        {/* Save word */}
        <div className="rounded-xl border border-slate-200 bg-white p-5">
          <h2 className="mb-1 text-sm font-semibold uppercase tracking-wide text-slate-500">
            Vocabulary
          </h2>
          <p className="mb-3 text-xs text-slate-400">
            Encountered a word you want to remember? Save it to your vocabulary list.
          </p>
          <button
            type="button"
            onClick={() => setShowSaveWord(true)}
            className="rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm hover:bg-slate-50"
          >
            + Save a word
          </button>
        </div>
      </div>

      {showSaveWord && (
        <SaveWordModal
          contentId={item.id}
          defaultLanguage={item.language}
          onClose={() => setShowSaveWord(false)}
        />
      )}
    </div>
  )
}
