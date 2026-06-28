/**
 * Format a duration in seconds to a human-readable string.
 * e.g. 3725 => "1h 2m"
 */
export function formatDuration(seconds: number): string {
  if (seconds < 60) return `${seconds}s`
  const minutes = Math.floor(seconds / 60)
  const hours = Math.floor(minutes / 60)
  if (hours === 0) return `${minutes}m`
  return `${hours}h ${minutes % 60}m`
}

/**
 * Format a content type slug to a display label.
 */
export function formatContentType(type: string): string {
  const labels: Record<string, string> = {
    article: 'Article',
    podcast: 'Podcast',
    video: 'Video',
    music: 'Music',
    tv_show: 'TV Show',
  }
  return labels[type] ?? type
}

/**
 * Format a relative timestamp.
 * Uses Intl.RelativeTimeFormat for locale-aware output.
 */
export function formatRelativeTime(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const diffMs = date.getTime() - now.getTime()
  const diffDays = Math.round(diffMs / (1000 * 60 * 60 * 24))

  const rtf = new Intl.RelativeTimeFormat('en', { numeric: 'auto' })

  if (Math.abs(diffDays) < 1) {
    const diffHours = Math.round(diffMs / (1000 * 60 * 60))
    return rtf.format(diffHours, 'hour')
  }
  if (Math.abs(diffDays) < 30) return rtf.format(diffDays, 'day')
  const diffMonths = Math.round(diffDays / 30)
  return rtf.format(diffMonths, 'month')
}
