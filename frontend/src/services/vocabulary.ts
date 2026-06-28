import apiClient from '@/lib/axios'
import type { PaginatedResponse, UserVocabularyEntry, VocabularyStatus } from '@/types'

export async function fetchUserVocabulary(): Promise<PaginatedResponse<UserVocabularyEntry>> {
  const { data } = await apiClient.get<PaginatedResponse<UserVocabularyEntry>>('/vocabulary')
  return data
}

export async function saveWord(vocabularyId: string): Promise<UserVocabularyEntry> {
  const { data } = await apiClient.post<UserVocabularyEntry>('/vocabulary', {
    vocabulary_id: vocabularyId,
  })
  return data
}

export async function removeWord(id: string): Promise<void> {
  await apiClient.delete(`/vocabulary/${id}`)
}

export async function fetchVocabularyForContent(
  contentId: string,
): Promise<UserVocabularyEntry[]> {
  const { data } = await apiClient.get<UserVocabularyEntry[]>(
    `/vocabulary/content/${contentId}`,
  )
  return data
}

export async function updateWordStatus(
  id: string,
  status: VocabularyStatus,
): Promise<UserVocabularyEntry> {
  const { data } = await apiClient.patch<UserVocabularyEntry>(`/vocabulary/${id}`, { status })
  return data
}
