import apiClient from '@/lib/axios'
import type { SRSLevel, VocabularyEntry, VocabularyListResponse } from '@/types'

// ── Request shapes ────────────────────────────────────────────────────────────

export interface VocabularyFilters {
  language?: string
  srs_level?: SRSLevel
  page?: number
  page_size?: number
}

export interface CreateVocabularyPayload {
  word: string
  language: string
  definition?: string | null
  translation?: string | null
  notes?: string | null
  content_id?: string | null
}

export interface UpdateVocabularyPayload {
  definition?: string | null
  translation?: string | null
  notes?: string | null
}

export interface ReviewPayload {
  correct: boolean
}

// ── API calls ─────────────────────────────────────────────────────────────────

export async function fetchVocabulary(
  filters: VocabularyFilters = {},
): Promise<VocabularyListResponse> {
  const { data } = await apiClient.get<VocabularyListResponse>('/vocabulary', {
    params: filters,
  })
  return data
}

export async function fetchVocabularyById(id: string): Promise<VocabularyEntry> {
  const { data } = await apiClient.get<VocabularyEntry>(`/vocabulary/${id}`)
  return data
}

export async function addVocabularyEntry(
  payload: CreateVocabularyPayload,
): Promise<VocabularyEntry> {
  const { data } = await apiClient.post<VocabularyEntry>('/vocabulary', payload)
  return data
}

export async function updateVocabularyEntry(
  id: string,
  payload: UpdateVocabularyPayload,
): Promise<VocabularyEntry> {
  const { data } = await apiClient.patch<VocabularyEntry>(`/vocabulary/${id}`, payload)
  return data
}

export async function deleteVocabularyEntry(id: string): Promise<void> {
  await apiClient.delete(`/vocabulary/${id}`)
}

export async function fetchReviewQueue(): Promise<VocabularyEntry[]> {
  const { data } = await apiClient.get<VocabularyEntry[]>('/vocabulary/review')
  return data
}

export async function submitReview(
  id: string,
  payload: ReviewPayload,
): Promise<VocabularyEntry> {
  const { data } = await apiClient.post<VocabularyEntry>(
    `/vocabulary/${id}/review`,
    payload,
  )
  return data
}
