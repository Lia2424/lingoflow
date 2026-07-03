import apiClient from '@/lib/axios'
import type { User } from '@/types'

export interface UpdateMePayload {
  username?: string
  native_language?: string
  target_language?: string
  cefr_level?: string
}

export async function fetchMe(): Promise<User> {
  const { data } = await apiClient.get<User>('/users/me')
  return data
}

export async function updateMe(payload: UpdateMePayload): Promise<User> {
  const { data } = await apiClient.patch<User>('/users/me', payload)
  return data
}
