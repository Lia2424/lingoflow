import apiClient from '@/lib/axios'
import type { User } from '@/types'

export interface RegisterPayload {
  email: string
  username: string
  password: string
  native_language: string
  target_language: string
}

export interface LoginPayload {
  email: string
  password: string
}

export interface TokenResponse {
  access_token: string
  token_type: 'bearer'
  user: User
}

export async function register(payload: RegisterPayload): Promise<TokenResponse> {
  const { data } = await apiClient.post<TokenResponse>('/auth/register', payload)
  return data
}

export async function login(payload: LoginPayload): Promise<TokenResponse> {
  const { data } = await apiClient.post<TokenResponse>('/auth/login', payload)
  return data
}

export async function logout(): Promise<void> {
  await apiClient.post('/auth/logout')
}

export async function refreshToken(): Promise<Pick<TokenResponse, 'access_token'>> {
  const { data } = await apiClient.post<Pick<TokenResponse, 'access_token'>>('/auth/refresh')
  return data
}
