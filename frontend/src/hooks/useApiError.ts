import axios from 'axios'

/**
 * Extracts a human-readable error message from an Axios error.
 * Handles FastAPI's two error shapes:
 *   - 422: { detail: [{ loc, msg, type }] }
 *   - 4xx: { detail: "string" }
 */
export function parseApiError(error: unknown): string {
  if (!axios.isAxiosError(error)) return 'Something went wrong. Please try again.'

  const detail = error.response?.data?.detail

  if (typeof detail === 'string') return detail

  if (Array.isArray(detail) && detail.length > 0) {
    return detail.map((d: { msg: string }) => d.msg).join(', ')
  }

  return error.message ?? 'Something went wrong. Please try again.'
}
