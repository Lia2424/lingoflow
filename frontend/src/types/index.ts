// ── Core domain enums ────────────────────────────────────────────────────────

export type CEFRLevel = 'A1' | 'A2' | 'B1' | 'B2' | 'C1' | 'C2'

export type SourceType = 'article' | 'podcast' | 'youtube' | 'music' | 'tv_show' | 'other'

/** @deprecated Use SourceType — kept for backward compat with old service calls */
export type ContentType = SourceType

export type VocabularyStatus = 'new' | 'learning' | 'known'

export type InteractionStatus = 'saved' | 'in_progress' | 'completed' | 'liked'

// ── Shared API shapes ─────────────────────────────────────────────────────────

/** Page-based pagination (matches backend ContentListResponse). */
export interface PagedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

/** @deprecated Use PagedResponse — cursor pagination is not yet implemented. */
export interface PaginatedResponse<T> {
  items: T[]
  next_cursor: string | null
  total: number
}

// ── User ──────────────────────────────────────────────────────────────────────

export interface User {
  id: string
  email: string
  username: string
  native_language: string
  target_language: string
  cefr_level: CEFRLevel
  created_at: string
}

export interface UserStats {
  words_learned: number
  content_completed: number
  current_streak_days: number
  cefr_progress_percent: number
}

// ── Content ───────────────────────────────────────────────────────────────────

export interface ContentItem {
  id: string
  title: string
  url: string
  source_type: SourceType
  language: string
  cefr_level: CEFRLevel
  thumbnail_url: string | null
  description: string | null
  duration_seconds: number | null
  published_at: string | null
  created_at: string
}

export interface ContentInteraction {
  content_id: string
  status: InteractionStatus
  rating: number | null
}

// ── Vocabulary ────────────────────────────────────────────────────────────────

export interface VocabularyEntry {
  id: string
  word: string
  language: string
  definition: string
  part_of_speech: string
  cefr_level: CEFRLevel
  examples: string[]
}

export interface UserVocabularyEntry extends VocabularyEntry {
  status: VocabularyStatus
  review_count: number
  next_review_at: string | null
}

// ── AI ────────────────────────────────────────────────────────────────────────

export interface CEFREstimate {
  level: CEFRLevel
  confidence: number
  reasoning: string
}

export interface SentenceExplanation {
  translation: string
  grammar_notes: string[]
  vocabulary_highlights: Array<{
    word: string
    definition: string
    cefr_level: CEFRLevel
  }>
}

export interface QuizQuestion {
  id: string
  type: 'multiple_choice' | 'fill_in_the_blank'
  prompt: string
  options?: string[]
  correct_answer: string
}

export interface Quiz {
  id: string
  content_id: string
  questions: QuizQuestion[]
}

// ── Immersion Plan ────────────────────────────────────────────────────────────

export interface ImmersionPlan {
  id: string
  generated_at: string
  expires_at: string
  status: 'active' | 'expired'
  plan_data: {
    summary: string
    weekly_goals: string[]
    recommended_content: ContentItem[]
    focus_areas: string[]
  }
}
