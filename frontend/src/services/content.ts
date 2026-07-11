import apiClient from '@/lib/axios'
import type { CEFRLevel, ContentItem, ContentQuestion, PagedResponse, SourceType } from '@/types'

export interface ContentFilters {
  language?: string
  cefr_level?: CEFRLevel
  source_type?: SourceType
  page?: number
  page_size?: number
}

export async function fetchContent(
  filters: ContentFilters = {},
): Promise<PagedResponse<ContentItem>> {
  const { data } = await apiClient.get<PagedResponse<ContentItem>>('/content', {
    params: filters,
  })
  return data
}

export async function fetchContentById(id: string): Promise<ContentItem> {
  const { data } = await apiClient.get<ContentItem>(`/content/${id}`)
  return data
}

export async function interactWithContent(
  contentId: string,
  payload: { status: string; rating?: number | null },
): Promise<void> {
  await apiClient.post(`/content/${contentId}/interact`, payload)
}

export async function fetchContentQuestions(
  contentId: string,
  n = 5,
): Promise<ContentQuestion[]> {
  const { data } = await apiClient.get<ContentQuestion[]>(
    `/content/${contentId}/questions`,
    { params: { n }, timeout: 120_000 },
  )
  return data
}
