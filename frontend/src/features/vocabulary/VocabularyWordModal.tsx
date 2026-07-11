import { useState } from 'react'

import { useMutation, useQueryClient } from '@tanstack/react-query'

import { LANGUAGES } from '@/lib/languages'
import {
  addVocabularyEntry,
  suggestVocabularyDefinition,
  updateVocabularyEntry,
} from '@/services/vocabulary'
import type { VocabularyEntry } from '@/types'

interface VocabularyWordModalProps {
  onClose: () => void
  entry?: VocabularyEntry
  contentId?: string
  initialLanguage?: string
  autoFocusWord?: boolean
}

function getErrorMessage(err: unknown, fallback: string): string {
  return (
    (err as { response?: { data?: { detail?: string } } })?.response?.data
      ?.detail ?? fallback
  )
}

export default function VocabularyWordModal({
  onClose,
  entry,
  contentId,
  initialLanguage = 'es',
  autoFocusWord = false,
}: VocabularyWordModalProps) {
  const queryClient = useQueryClient()
  const isEditing = Boolean(entry)

  const [word, setWord] = useState(entry?.word ?? '')
  const [language, setLanguage] = useState(entry?.language ?? initialLanguage)
  const [definition, setDefinition] = useState(entry?.definition ?? '')
  const [translation, setTranslation] = useState(entry?.translation ?? '')
  const [notes, setNotes] = useState(entry?.notes ?? '')
  const [entryId, setEntryId] = useState<string | null>(entry?.id ?? null)
  const [saveError, setSaveError] = useState<string | null>(null)
  const [suggestError, setSuggestError] = useState<string | null>(null)
  const [isSuggesting, setIsSuggesting] = useState(false)

  const { mutate: save, isPending: isSaving } = useMutation({
    mutationFn: async () => {
      const payload = {
        word: word.trim(),
        language,
        definition: definition || null,
        translation: translation || null,
        notes: notes || null,
        content_id: contentId ?? null,
      }

      if (entryId) {
        return updateVocabularyEntry(entryId, {
          word: payload.word,
          language: payload.language,
          definition: payload.definition,
          translation: payload.translation,
          notes: payload.notes,
        })
      }

      return addVocabularyEntry(payload)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vocabulary'] })
      onClose()
    },
    onError: (err: unknown) => {
      setSaveError(getErrorMessage(err, 'Failed to save word. Please try again.'))
    },
  })

  async function handleSuggest() {
    if (!word.trim() || isSuggesting || isSaving) return

    setSuggestError(null)
    setIsSuggesting(true)

    try {
      let id = entryId
      if (!id) {
        const entry = await addVocabularyEntry({
          word: word.trim(),
          language,
          definition: definition || null,
          translation: translation || null,
          notes: notes || null,
          content_id: contentId ?? null,
        })
        id = entry.id
        setEntryId(id)
      }

      const suggestion = await suggestVocabularyDefinition(id)
      setDefinition(suggestion.definition)
      setTranslation(suggestion.translation)
    } catch (err: unknown) {
      setSuggestError(
        getErrorMessage(err, 'AI suggestion unavailable. Please try again.'),
      )
    } finally {
      setIsSuggesting(false)
    }
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setSaveError(null)
    if (!word.trim()) return
    save()
  }

  const inputClass =
    'w-full rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-800 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-400'

  const isBusy = isSaving || isSuggesting

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="w-full max-w-md rounded-2xl bg-white shadow-xl">
        <div className="flex items-center justify-between border-b border-slate-100 px-5 py-4">
          <h2 className="text-base font-semibold text-slate-900">
            {isEditing ? 'Edit word' : 'Save a word'}
          </h2>
          <button
            type="button"
            onClick={onClose}
            className="cursor-pointer text-slate-400 hover:text-slate-600"
            aria-label="Close"
          >
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4 p-5">
          {saveError && (
            <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">
              {saveError}
            </p>
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
                autoFocus={autoFocusWord && !isEditing}
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
                className="cursor-pointer rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-700 focus:outline-none focus:ring-2 focus:ring-slate-400"
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
            <button
              type="button"
              onClick={handleSuggest}
              disabled={isBusy || !word.trim()}
              className="flex cursor-pointer items-center gap-2 rounded-lg border border-violet-200 bg-violet-50 px-3 py-2 text-sm font-medium text-violet-700 hover:bg-violet-100 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isSuggesting ? (
                <>
                  <span
                    className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-violet-300 border-t-violet-700"
                    aria-hidden="true"
                  />
                  Suggesting…
                </>
              ) : (
                '✨ Suggest definition'
              )}
            </button>
            {suggestError && (
              <p className="mt-2 rounded-lg bg-amber-50 px-3 py-2 text-sm text-amber-800">
                {suggestError}
              </p>
            )}
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
              className="cursor-pointer rounded-lg border border-slate-200 px-4 py-2 text-sm text-slate-600 hover:bg-slate-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isBusy || !word.trim()}
              className="cursor-pointer rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isSaving ? 'Saving…' : isEditing ? 'Save changes' : 'Save word'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
