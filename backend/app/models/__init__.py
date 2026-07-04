# Import all ORM models here so Alembic's autogenerate discovers them.
from app.models.content import Content  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.user_content_interaction import UserContentInteraction  # noqa: F401
from app.models.vocabulary import VocabularyEntry  # noqa: F401
