import { create } from 'zustand'
import { persist } from 'zustand/middleware'

import type { CEFRLevel } from '@/types'

interface PreferencesState {
  selectedLanguage: string | null
  selectedCEFR: CEFRLevel | null
  setPreferences: (language: string, cefr: CEFRLevel) => void
  clearPreferences: () => void
}

export const usePreferencesStore = create<PreferencesState>()(
  persist(
    (set) => ({
      selectedLanguage: null,
      selectedCEFR: null,
      setPreferences: (language, cefr) =>
        set({ selectedLanguage: language, selectedCEFR: cefr }),
      clearPreferences: () => set({ selectedLanguage: null, selectedCEFR: null }),
    }),
    { name: 'lingoflow-preferences' },
  ),
)
