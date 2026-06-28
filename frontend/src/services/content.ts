import apiClient from '@/lib/axios'
import type { CEFRLevel, ContentItem, ContentType, PaginatedResponse } from '@/types'

export interface ContentFilters {
  language?: string
  cefr?: CEFRLevel
  type?: ContentType
  q?: string
  cursor?: string
  limit?: number
}

export async function fetchContent(
  filters: ContentFilters = {},
): Promise<PaginatedResponse<ContentItem>> {
  const { data } = await apiClient.get<PaginatedResponse<ContentItem>>('/content', {
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
  payload: { status: string; progress_percent?: number },
): Promise<void> {
  await apiClient.post(`/content/${contentId}/interact`, payload)
}
