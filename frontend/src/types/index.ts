// ── Core domain enums ────────────────────────────────────────────────────────

export type CEFRLevel = 'A1' | 'A2' | 'B1' | 'B2' | 'C1' | 'C2'

export type ContentType = 'article' | 'podcast' | 'video' | 'music' | 'tv_show'

export type VocabularyStatus = 'new' | 'learning' | 'known'

export type InteractionStatus = 'saved' | 'in_progress' | 'completed' | 'liked'

// ── Shared API shapes ─────────────────────────────────────────────────────────

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
  content_type: ContentType
  language: string
  cefr_level: CEFRLevel
  difficulty_score: number
  duration_seconds: number | null
  thumbnail_url: string | null
  published_at: string
  tags: string[]
}

export interface ContentInteraction {
  content_id: string
  status: InteractionStatus
  progress_percent: number
  last_interacted_at: string
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
