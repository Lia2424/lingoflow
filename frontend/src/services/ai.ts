import apiClient from '@/lib/axios'
import type { CEFREstimate, Quiz, SentenceExplanation } from '@/types'

export async function explainSentence(payload: {
  sentence: string
  content_id: string
}): Promise<SentenceExplanation> {
  const { data } = await apiClient.post<SentenceExplanation>('/ai/explain', payload)
  return data
}

export async function estimateDifficulty(text: string): Promise<CEFREstimate> {
  const { data } = await apiClient.post<CEFREstimate>('/ai/difficulty', { text })
  return data
}

export async function getOrGenerateQuiz(contentId: string): Promise<Quiz> {
  const { data } = await apiClient.get<Quiz>(`/ai/quiz/${contentId}`)
  return data
}
