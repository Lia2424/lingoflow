# Business logic layer. Services:
#   - Accept domain objects (not raw DB rows or HTTP request bodies).
#   - Delegate all DB access to repositories.
#   - Are independently unit-testable (no SQLAlchemy in method signatures).
#
# from app.services.auth import AuthService
# from app.services.content import ContentService
# from app.services.ai import AIService
# from app.services.recommendation import RecommendationService
