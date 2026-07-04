import { useState } from 'react'

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

import { LANGUAGES } from '@/lib/languages'
import {
  addVocabularyEntry,
  deleteVocabularyEntry,
  fetchVocabulary,
} from '@/services/vocabulary'
import type { SRSLevel } from '@/types'

import VocabularyCard from './VocabularyCard'
import VocabularyCardSkeleton from './VocabularyCardSkeleton'

// ── Constants ─────────────────────────────────────────────────────────────────

const PAGE_SIZE = 20
const SRS_LEVELS: SRSLevel[] = [0, 1, 2, 3, 4, 5]
const SRS_LEVEL_LABELS: Record<SRSLevel, string> = {
  0: 'New',
  1: 'Level 1',
  2: 'Level 2',
  3: 'Level 3',
  4: 'Level 4',
  5: 'Mastered',
}

// ── Filter select ─────────────────────────────────────────────────────────────

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

// ── Add-word modal ─────────────────────────────────────────────────────────────

interface AddWordModalProps {
  onClose: () => void
}

function AddWordModal({ onClose }: AddWordModalProps) {
  const queryClient = useQueryClient()

  const [word, setWord] = useState('')
  const [language, setLanguage] = useState('es')
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
            <label className="mb-1 block text-xs font-medium text-slate-500">
              Definition
            </label>
            <input
              value={definition}
              onChange={(e) => setDefinition(e.target.value)}
              placeholder="e.g. friendship"
              maxLength={2000}
              className={inputClass}
            />
          </div>

          <div>
            <label className="mb-1 block text-xs font-medium text-slate-500">
              Translation
            </label>
            <input
              value={translation}
              onChange={(e) => setTranslation(e.target.value)}
              placeholder="e.g. friendship (EN)"
              maxLength={2000}
              className={inputClass}
            />
          </div>

          <div>
            <label className="mb-1 block text-xs font-medium text-slate-500">
              Notes
            </label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Any extra context..."
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

// ── Delete confirmation dialog ─────────────────────────────────────────────────

interface DeleteDialogProps {
  word: string
  onConfirm: () => void
  onCancel: () => void
  isPending: boolean
  error?: string | null
}

function DeleteDialog({ word, onConfirm, onCancel, isPending, error }: DeleteDialogProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="w-full max-w-sm rounded-2xl bg-white p-6 shadow-xl">
        <h2 className="text-base font-semibold text-slate-900">Remove word?</h2>
        <p className="mt-1 text-sm text-slate-500">
          "<span className="font-medium text-slate-700">{word}</span>" will be removed
          from your vocabulary list. This cannot be undone.
        </p>
        {error && (
          <p className="mt-2 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">{error}</p>
        )}
        <div className="mt-4 flex justify-end gap-2">
          <button
            type="button"
            onClick={onCancel}
            className="rounded-lg border border-slate-200 px-4 py-2 text-sm text-slate-600 hover:bg-slate-50"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={onConfirm}
            disabled={isPending}
            className="rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700 disabled:opacity-50"
          >
            {isPending ? 'Removing…' : 'Remove'}
          </button>
        </div>
      </div>
    </div>
  )
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default function VocabularyPage() {
  const queryClient = useQueryClient()

  const [language, setLanguage] = useState('')
  const [srsLevel, setSrsLevel] = useState('')
  const [page, setPage] = useState(1)
  const [showAddModal, setShowAddModal] = useState(false)
  const [pendingDeleteId, setPendingDeleteId] = useState<string | null>(null)
  const [deleteError, setDeleteError] = useState<string | null>(null)

  const filters = {
    language: language || undefined,
    srs_level: srsLevel !== '' ? (Number(srsLevel) as SRSLevel) : undefined,
    page,
    page_size: PAGE_SIZE,
  }

  const { data, isLoading } = useQuery({
    queryKey: ['vocabulary', filters],
    queryFn: () => fetchVocabulary(filters),
  })

  const { mutate: deleteEntry, isPending: isDeleting } = useMutation({
    mutationFn: (id: string) => deleteVocabularyEntry(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vocabulary'] })
      setPendingDeleteId(null)
      setDeleteError(null)
    },
    onError: () => {
      setDeleteError('Could not remove the word. Please try again.')
    },
  })

  const items = data?.items ?? []
  const total = data?.total ?? 0
  const totalPages = Math.ceil(total / PAGE_SIZE)

  const pendingDeleteEntry = items.find((e) => e.id === pendingDeleteId)

  function handleFilterChange(setter: (v: string) => void) {
    return (v: string) => {
      setter(v)
      setPage(1)
    }
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <div className="border-b border-slate-200 bg-white px-4 py-4 sm:px-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-slate-900">Vocabulary</h1>
            <p className="mt-0.5 text-sm text-slate-500">
              Words you're learning across all languages
            </p>
          </div>
          <button
            type="button"
            onClick={() => setShowAddModal(true)}
            className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-slate-700"
          >
            + Add word
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="border-b border-slate-200 bg-white px-4 py-3 sm:px-6">
        <div className="flex flex-wrap items-end gap-3">
          <FilterSelect
            label="Language"
            value={language}
            onChange={handleFilterChange(setLanguage)}
          >
            <option value="">All languages</option>
            {LANGUAGES.map((l) => (
              <option key={l.code} value={l.code}>
                {l.name}
              </option>
            ))}
          </FilterSelect>

          <FilterSelect
            label="SRS Level"
            value={srsLevel}
            onChange={handleFilterChange(setSrsLevel)}
          >
            <option value="">All levels</option>
            {SRS_LEVELS.map((lvl) => (
              <option key={lvl} value={lvl}>
                {SRS_LEVEL_LABELS[lvl]}
              </option>
            ))}
          </FilterSelect>

          {(language || srsLevel !== '') && (
            <button
              type="button"
              onClick={() => {
                setLanguage('')
                setSrsLevel('')
                setPage(1)
              }}
              className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-500 shadow-sm hover:bg-slate-50"
            >
              Clear filters
            </button>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="px-4 py-6 sm:px-6">
        {/* Result count */}
        {!isLoading && total > 0 && (
          <p className="mb-4 text-sm text-slate-500">
            {total.toLocaleString()} {total === 1 ? 'word' : 'words'}
          </p>
        )}

        {/* Skeleton */}
        {isLoading && (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 6 }).map((_, i) => (
              <VocabularyCardSkeleton key={i} />
            ))}
          </div>
        )}

        {/* Empty state */}
        {!isLoading && items.length === 0 && (
          <div className="flex flex-col items-center justify-center py-24 text-center">
            <div className="mb-4 text-5xl">📖</div>
            <h2 className="text-lg font-semibold text-slate-700">No words yet</h2>
            <p className="mt-1 text-sm text-slate-500">
              Save words while reading or watching content to build your list.
            </p>
            <button
              type="button"
              onClick={() => setShowAddModal(true)}
              className="mt-4 rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700"
            >
              Add your first word
            </button>
          </div>
        )}

        {/* Cards */}
        {items.length > 0 && (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {items.map((entry) => (
              <VocabularyCard
                key={entry.id}
                entry={entry}
                onDelete={(id) => setPendingDeleteId(id)}
                isDeleting={isDeleting && pendingDeleteId === entry.id}
              />
            ))}
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="mt-8 flex items-center justify-center gap-3">
            <button
              type="button"
              disabled={page === 1}
              onClick={() => setPage((p) => p - 1)}
              className="rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm text-slate-600 hover:bg-slate-50 disabled:opacity-40"
            >
              ← Previous
            </button>
            <span className="text-sm text-slate-500">
              Page {page} of {totalPages}
            </span>
            <button
              type="button"
              disabled={page >= totalPages}
              onClick={() => setPage((p) => p + 1)}
              className="rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm text-slate-600 hover:bg-slate-50 disabled:opacity-40"
            >
              Next →
            </button>
          </div>
        )}
      </div>

      {/* Modals */}
      {showAddModal && <AddWordModal onClose={() => setShowAddModal(false)} />}

      {pendingDeleteEntry && (
        <DeleteDialog
          word={pendingDeleteEntry.word}
          onConfirm={() => deleteEntry(pendingDeleteId!)}
          onCancel={() => { setPendingDeleteId(null); setDeleteError(null) }}
          isPending={isDeleting}
          error={deleteError}
        />
      )}
    </div>
  )
}
