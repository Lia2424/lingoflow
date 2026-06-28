import { create } from 'zustand'
import { persist } from 'zustand/middleware'

import type { CEFRLevel, ContentType } from '@/types'

interface PreferencesState {
  selectedCEFR: CEFRLevel | null
  selectedTypes: ContentType[]
  selectedLanguage: string | null
  setSelectedCEFR: (level: CEFRLevel | null) => void
  setSelectedTypes: (types: ContentType[]) => void
  setSelectedLanguage: (language: string | null) => void
  resetFilters: () => void
}

export const usePreferencesStore = create<PreferencesState>()(
  persist(
    (set) => ({
      selectedCEFR: null,
      selectedTypes: [],
      selectedLanguage: null,
      setSelectedCEFR: (level) => set({ selectedCEFR: level }),
      setSelectedTypes: (types) => set({ selectedTypes: types }),
      setSelectedLanguage: (language) => set({ selectedLanguage: language }),
      resetFilters: () =>
        set({ selectedCEFR: null, selectedTypes: [], selectedLanguage: null }),
    }),
    { name: 'lingoflow-preferences' },
  ),
)
