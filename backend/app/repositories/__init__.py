# Data access layer. One repository per aggregate root.
# Repositories:
#   - Accept an AsyncSession via constructor injection.
#   - Return ORM model instances (never raw dicts or tuples).
#   - Contain all SQLAlchemy query logic.
#
# from app.repositories.user import UserRepository
# from app.repositories.content import ContentRepository
# from app.repositories.vocabulary import VocabularyRepository
