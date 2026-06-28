import type { CEFRLevel } from '@/types'

export const CEFR_LEVELS: CEFRLevel[] = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']

export const CEFR_LABELS: Record<CEFRLevel, string> = {
  A1: 'Beginner',
  A2: 'Elementary',
  B1: 'Intermediate',
  B2: 'Upper Intermediate',
  C1: 'Advanced',
  C2: 'Mastery',
}

export function cefrLabel(level: CEFRLevel): string {
  return CEFR_LABELS[level]
}

export function cefrColor(level: CEFRLevel): string {
  const colors: Record<CEFRLevel, string> = {
    A1: 'bg-green-100 text-green-800',
    A2: 'bg-emerald-100 text-emerald-800',
    B1: 'bg-blue-100 text-blue-800',
    B2: 'bg-indigo-100 text-indigo-800',
    C1: 'bg-purple-100 text-purple-800',
    C2: 'bg-rose-100 text-rose-800',
  }
  return colors[level]
}
