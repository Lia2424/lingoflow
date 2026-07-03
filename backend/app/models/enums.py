import enum


class CEFRLevel(enum.StrEnum):
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"


class ContentType(enum.StrEnum):
    ARTICLE = "article"
    PODCAST = "podcast"
    VIDEO = "video"
    MUSIC = "music"
    TV_SHOW = "tv_show"


class VocabularyStatus(enum.StrEnum):
    NEW = "new"
    LEARNING = "learning"
    KNOWN = "known"


class InteractionStatus(enum.StrEnum):
    SAVED = "saved"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    LIKED = "liked"
