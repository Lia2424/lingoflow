import { useMemo, useState } from 'react'

import { LANGUAGES } from '@/lib/languages'

interface LanguageSelectProps {
  value: string
  onChange: (code: string) => void
  excludeCode?: string
  label: string
  id: string
}

export default function LanguageSelect({
  value,
  onChange,
  excludeCode,
  label,
  id,
}: LanguageSelectProps) {
  const [query, setQuery] = useState('')

  const options = useMemo(
    () =>
      LANGUAGES.filter(
        (l) =>
          l.code !== excludeCode &&
          (query === '' ||
            l.name.toLowerCase().includes(query.toLowerCase()) ||
            l.nativeName.toLowerCase().includes(query.toLowerCase())),
      ),
    [excludeCode, query],
  )

  const selected = LANGUAGES.find((l) => l.code === value)

  return (
    <div className="space-y-2">
      <label htmlFor={id} className="text-sm font-medium text-slate-700">
        {label}
      </label>

      <input
        type="text"
        placeholder="Search languages…"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        className="w-full rounded-md border border-slate-200 bg-white px-3 py-2 text-sm placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-400"
        aria-label={`Search ${label}`}
      />

      <div
        id={id}
        role="listbox"
        aria-label={label}
        className="max-h-48 overflow-y-auto rounded-md border border-slate-200 bg-white"
      >
        {options.length === 0 && (
          <p className="px-3 py-4 text-center text-sm text-slate-400">No languages found</p>
        )}
        {options.map((lang) => (
          <button
            key={lang.code}
            type="button"
            role="option"
            aria-selected={lang.code === value}
            onClick={() => onChange(lang.code)}
            className={`flex w-full items-center justify-between px-3 py-2.5 text-left text-sm transition-colors hover:bg-slate-50 ${
              lang.code === value ? 'bg-slate-100 font-medium text-slate-900' : 'text-slate-700'
            }`}
          >
            <span>{lang.name}</span>
            <span className="text-xs text-slate-400">{lang.nativeName}</span>
          </button>
        ))}
      </div>

      {selected && (
        <p className="text-xs text-slate-500">
          Selected: <span className="font-medium">{selected.name}</span>
        </p>
      )}
    </div>
  )
}
