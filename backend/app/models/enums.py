import enum


class CEFRLevel(str, enum.Enum):
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"


class ContentType(str, enum.Enum):
    ARTICLE = "article"
    PODCAST = "podcast"
    VIDEO = "video"
    MUSIC = "music"
    TV_SHOW = "tv_show"


class VocabularyStatus(str, enum.Enum):
    NEW = "new"
    LEARNING = "learning"
    KNOWN = "known"


class InteractionStatus(str, enum.Enum):
    SAVED = "saved"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    LIKED = "liked"
