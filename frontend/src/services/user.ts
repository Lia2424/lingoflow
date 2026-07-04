import apiClient from '@/lib/axios'
import type { User } from '@/types'

// ── Request shapes ────────────────────────────────────────────────────────────

export interface UpdateProfilePayload {
  username?: string
  native_language?: string
  target_language?: string
  cefr_level?: string
}

export interface ChangePasswordPayload {
  current_password: string
  new_password: string
}

export interface DeleteAccountPayload {
  password: string
}

// ── API calls ─────────────────────────────────────────────────────────────────

export async function fetchMe(): Promise<User> {
  const { data } = await apiClient.get<User>('/users/me')
  return data
}

export async function updateProfile(payload: UpdateProfilePayload): Promise<User> {
  const { data } = await apiClient.patch<User>('/users/me', payload)
  return data
}

export async function changePassword(payload: ChangePasswordPayload): Promise<void> {
  await apiClient.post('/users/me/change-password', payload)
}

export async function deleteAccount(payload: DeleteAccountPayload): Promise<void> {
  await apiClient.delete('/users/me', { data: payload })
}
