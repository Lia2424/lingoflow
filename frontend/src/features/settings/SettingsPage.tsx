import { useState } from 'react'

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'

import { LANGUAGES } from '@/lib/languages'
import {
  changePassword,
  deleteAccount,
  fetchMe,
  updateProfile,
} from '@/services/user'
import { useAuthStore } from '@/stores/authStore'
import type { CEFRLevel, User } from '@/types'

// ── Shared helpers ────────────────────────────────────────────────────────────

const CEFR_LEVELS: CEFRLevel[] = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']

const inputCls =
  'w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm text-slate-800 ' +
  'placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-400 ' +
  'disabled:cursor-not-allowed disabled:opacity-50'

const labelCls = 'block text-xs font-medium text-slate-500'

function apiErrorMessage(err: unknown, fallback: string): string {
  return (
    (err as { response?: { data?: { detail?: string } } })?.response?.data
      ?.detail ?? fallback
  )
}

// ── Section card wrapper ──────────────────────────────────────────────────────

interface SectionProps {
  title: string
  description: string
  children: React.ReactNode
  danger?: boolean
}

function Section({ title, description, children, danger }: SectionProps) {
  return (
    <div
      className={`rounded-2xl border bg-white p-6 shadow-sm ${
        danger ? 'border-red-200' : 'border-slate-200'
      }`}
    >
      <h2
        className={`text-base font-semibold ${
          danger ? 'text-red-700' : 'text-slate-900'
        }`}
      >
        {title}
      </h2>
      <p className="mt-0.5 text-sm text-slate-500">{description}</p>
      <div className="mt-5">{children}</div>
    </div>
  )
}

// ── Inline feedback ───────────────────────────────────────────────────────────

interface FeedbackProps {
  success?: string | null
  error?: string | null
}

function Feedback({ success, error }: FeedbackProps) {
  if (success)
    return (
      <p className="rounded-lg bg-emerald-50 px-3 py-2 text-sm text-emerald-700">
        {success}
      </p>
    )
  if (error)
    return (
      <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">{error}</p>
    )
  return null
}

// ── Profile section ───────────────────────────────────────────────────────────

function ProfileSection() {
  const queryClient = useQueryClient()
  const updateUser = useAuthStore((s) => s.updateUser)
  const { data: me, isLoading } = useQuery({
    queryKey: ['me'],
    queryFn: fetchMe,
  })

  const [username, setUsername] = useState('')
  const [targetLang, setTargetLang] = useState('')
  const [nativeLang, setNativeLang] = useState('')
  const [cefr, setCefr] = useState('')
  const [initialised, setInitialised] = useState(false)
  const [success, setSuccess] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  // Seed form once data arrives (similar pattern to ReviewPage queue seeding)
  if (me && !initialised) {
    setUsername(me.username)
    setTargetLang(me.target_language)
    setNativeLang(me.native_language)
    setCefr(me.cefr_level)
    setInitialised(true)
  }

  const { mutate, isPending } = useMutation({
    mutationFn: () =>
      updateProfile({
        username: username.trim() || undefined,
        target_language: targetLang || undefined,
        native_language: nativeLang || undefined,
        cefr_level: cefr || undefined,
      }),
    onSuccess: (updated: User) => {
      queryClient.setQueryData(['me'], updated)
      // Sync the auth store so NavBar/UserMenu reflect the new username immediately
      updateUser({
        username: updated.username,
        native_language: updated.native_language,
        target_language: updated.target_language,
        cefr_level: updated.cefr_level,
      })
      setSuccess('Profile updated.')
      setError(null)
    },
    onError: (err: unknown) => {
      setError(apiErrorMessage(err, 'Failed to update profile. Please try again.'))
      setSuccess(null)
    },
  })

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setSuccess(null)
    setError(null)
    mutate()
  }

  return (
    <Section title="Profile" description="Update your display name and language settings.">
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label className={labelCls}>Username</label>
            <input
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              disabled={isLoading || isPending}
              minLength={2}
              maxLength={50}
              required
              className={`mt-1 ${inputCls}`}
            />
          </div>
          <div>
            <label className={labelCls}>Email</label>
            <input
              value={me?.email ?? ''}
              disabled
              readOnly
              className={`mt-1 ${inputCls}`}
            />
          </div>
          <div>
            <label className={labelCls}>Target language</label>
            <select
              value={targetLang}
              onChange={(e) => setTargetLang(e.target.value)}
              disabled={isLoading || isPending}
              className={`mt-1 ${inputCls}`}
            >
              {LANGUAGES.map((l) => (
                <option key={l.code} value={l.code}>
                  {l.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className={labelCls}>Native language</label>
            <select
              value={nativeLang}
              onChange={(e) => setNativeLang(e.target.value)}
              disabled={isLoading || isPending}
              className={`mt-1 ${inputCls}`}
            >
              {LANGUAGES.map((l) => (
                <option key={l.code} value={l.code}>
                  {l.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className={labelCls}>CEFR level</label>
            <select
              value={cefr}
              onChange={(e) => setCefr(e.target.value)}
              disabled={isLoading || isPending}
              className={`mt-1 ${inputCls}`}
            >
              {CEFR_LEVELS.map((lvl) => (
                <option key={lvl} value={lvl}>
                  {lvl}
                </option>
              ))}
            </select>
          </div>
        </div>

        <Feedback success={success} error={error} />

        <div className="flex justify-end">
          <button
            type="submit"
            disabled={isPending || isLoading}
            className="rounded-lg bg-slate-900 px-5 py-2 text-sm font-medium text-white hover:bg-slate-700 disabled:opacity-50"
          >
            {isPending ? 'Saving…' : 'Save profile'}
          </button>
        </div>
      </form>
    </Section>
  )
}

// ── Security section ──────────────────────────────────────────────────────────

function SecuritySection() {
  const [current, setCurrent] = useState('')
  const [next, setNext] = useState('')
  const [confirm, setConfirm] = useState('')
  const [success, setSuccess] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const { mutate, isPending } = useMutation({
    mutationFn: () => changePassword({ current_password: current, new_password: next }),
    onSuccess: () => {
      setSuccess('Password changed successfully.')
      setError(null)
      setCurrent('')
      setNext('')
      setConfirm('')
    },
    onError: (err: unknown) => {
      setError(apiErrorMessage(err, 'Failed to change password. Please try again.'))
      setSuccess(null)
    },
  })

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setSuccess(null)
    setError(null)
    if (next !== confirm) {
      setError('New passwords do not match.')
      return
    }
    mutate()
  }

  return (
    <Section title="Security" description="Change your login password.">
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div>
          <label className={labelCls}>Current password</label>
          <input
            type="password"
            value={current}
            onChange={(e) => setCurrent(e.target.value)}
            required
            autoComplete="current-password"
            className={`mt-1 ${inputCls}`}
          />
        </div>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <div>
            <label className={labelCls}>New password</label>
            <input
              type="password"
              value={next}
              onChange={(e) => setNext(e.target.value)}
              required
              minLength={8}
              autoComplete="new-password"
              className={`mt-1 ${inputCls}`}
            />
          </div>
          <div>
            <label className={labelCls}>Confirm new password</label>
            <input
              type="password"
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
              required
              minLength={8}
              autoComplete="new-password"
              className={`mt-1 ${inputCls}`}
            />
          </div>
        </div>

        <Feedback success={success} error={error} />

        <div className="flex justify-end">
          <button
            type="submit"
            disabled={isPending}
            className="rounded-lg bg-slate-900 px-5 py-2 text-sm font-medium text-white hover:bg-slate-700 disabled:opacity-50"
          >
            {isPending ? 'Saving…' : 'Change password'}
          </button>
        </div>
      </form>
    </Section>
  )
}

// ── Danger zone ───────────────────────────────────────────────────────────────

function DangerZone() {
  const [showDialog, setShowDialog] = useState(false)
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const navigate = useNavigate()
  const clearAuth = useAuthStore((s) => s.clearAuth)

  const { mutate, isPending } = useMutation({
    mutationFn: () => deleteAccount({ password }),
    onSuccess: () => {
      clearAuth()
      navigate('/login', { replace: true })
    },
    onError: (err: unknown) => {
      setError(apiErrorMessage(err, 'Failed to delete account. Please try again.'))
    },
  })

  function handleOpen() {
    setPassword('')
    setError(null)
    setShowDialog(true)
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError(null)
    mutate()
  }

  return (
    <>
      <Section
        title="Danger zone"
        description="Permanently delete your account and all associated data. This cannot be undone."
        danger
      >
        <button
          type="button"
          onClick={handleOpen}
          className="rounded-lg border border-red-300 bg-red-50 px-4 py-2 text-sm font-medium text-red-700 hover:bg-red-100"
        >
          Delete my account
        </button>
      </Section>

      {/* Confirmation dialog */}
      {showDialog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
          <div className="w-full max-w-sm rounded-2xl bg-white p-6 shadow-xl">
            <h2 className="text-base font-semibold text-slate-900">
              Delete account?
            </h2>
            <p className="mt-1 text-sm text-slate-500">
              All your vocabulary, interactions, and progress will be permanently
              erased. Enter your password to confirm.
            </p>

            <form onSubmit={handleSubmit} className="mt-4 flex flex-col gap-3">
              <input
                type="password"
                placeholder="Your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                autoComplete="current-password"
                className={inputCls}
              />

              {error && (
                <p className="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">
                  {error}
                </p>
              )}

              <div className="flex justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowDialog(false)}
                  className="rounded-lg border border-slate-200 px-4 py-2 text-sm text-slate-600 hover:bg-slate-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isPending || !password}
                  className="rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700 disabled:opacity-50"
                >
                  {isPending ? 'Deleting…' : 'Delete forever'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  )
}

// ── Page ──────────────────────────────────────────────────────────────────────

export default function SettingsPage() {
  return (
    <div className="min-h-screen bg-slate-50">
      <div className="mx-auto max-w-2xl px-4 py-10 sm:px-6">
        <h1 className="mb-8 text-2xl font-bold text-slate-900">Settings</h1>
        <div className="flex flex-col gap-6">
          <ProfileSection />
          <SecuritySection />
          <DangerZone />
        </div>
      </div>
    </div>
  )
}
