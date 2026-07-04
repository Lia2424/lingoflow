import { useState } from 'react'

import { NavLink } from 'react-router-dom'

import UserMenu from './UserMenu'

const NAV_LINKS = [
  { to: '/', label: 'Discovery', end: true },
  { to: '/vocabulary', label: 'Vocabulary', end: false },
  { to: '/vocabulary/review', label: 'Review', end: true },
]

const activeCls = 'text-slate-900 font-semibold'
const inactiveCls = 'text-slate-500 hover:text-slate-800'
const baseDesktopCls = 'text-sm transition-colors'
const baseMobileCls =
  'block rounded-lg px-3 py-2 text-base transition-colors'
const activeMobileCls = 'bg-slate-100 font-semibold text-slate-900'
const inactiveMobileCls = 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'

export default function NavBar() {
  const [menuOpen, setMenuOpen] = useState(false)

  return (
    <header className="sticky top-0 z-40 border-b border-slate-200 bg-white">
      <nav className="mx-auto flex h-14 max-w-7xl items-center justify-between px-4 sm:px-6">
        {/* Left — wordmark */}
        <NavLink
          to="/"
          className="flex items-center gap-1.5 text-base font-bold tracking-tight text-slate-900"
          onClick={() => setMenuOpen(false)}
        >
          <span className="rounded-md bg-slate-900 px-1.5 py-0.5 text-xs font-bold text-white">
            LF
          </span>
          LingoFlow
        </NavLink>

        {/* Center — desktop nav links */}
        <div className="hidden items-center gap-6 sm:flex">
          {NAV_LINKS.map(({ to, label, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                `${baseDesktopCls} ${isActive ? activeCls : inactiveCls}`
              }
            >
              {label}
            </NavLink>
          ))}
        </div>

        {/* Right — avatar + hamburger */}
        <div className="flex items-center gap-3">
          <UserMenu />

          {/* Hamburger (mobile only) */}
          <button
            type="button"
            className="rounded-md p-1.5 text-slate-500 hover:bg-slate-100 sm:hidden"
            aria-label={menuOpen ? 'Close menu' : 'Open menu'}
            onClick={() => setMenuOpen((v) => !v)}
          >
            {menuOpen ? (
              <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            ) : (
              <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
              </svg>
            )}
          </button>
        </div>
      </nav>

      {/* Mobile menu drawer */}
      {menuOpen && (
        <div className="border-t border-slate-100 bg-white px-4 pb-4 pt-2 sm:hidden">
          {NAV_LINKS.map(({ to, label, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              onClick={() => setMenuOpen(false)}
              className={({ isActive }) =>
                `${baseMobileCls} ${isActive ? activeMobileCls : inactiveMobileCls}`
              }
            >
              {label}
            </NavLink>
          ))}
        </div>
      )}
    </header>
  )
}
