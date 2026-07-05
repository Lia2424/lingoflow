"""Article extraction integration using trafilatura.

Fetches a URL, strips boilerplate, and returns structured metadata
suitable for storing in the content table.

Requires the ``trafilatura`` package (added to pyproject.toml).
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass

import httpx

logger = logging.getLogger(__name__)

# trafilatura is an optional heavy dependency.  Import lazily so the rest of
# the application still starts even if the package is missing (relevant for
# test environments that don't install it).
try:
    import trafilatura
    import trafilatura.settings

    _TRAFILATURA_AVAILABLE = True
except ImportError:  # pragma: no cover
    _TRAFILATURA_AVAILABLE = False


@dataclass
class ArticleMetadata:
    external_id: str  # "article:<sha256[:16] of url>"
    title: str
    url: str
    language: str | None
    description: str | None
    body: str | None  # main article text (not stored in content table yet)
    author: str | None


async def extract_metadata(url: str) -> ArticleMetadata:
    """Download *url* and extract article metadata with trafilatura.

    The returned :attr:`~ArticleMetadata.body` contains the main text content,
    which can be stored separately or used for AI processing.  The fields
    that map directly to ``content`` columns are ``title``, ``url``,
    ``language``, and ``description``.

    Raises:
        RuntimeError: If trafilatura is not installed.
        httpx.HTTPError: If the HTTP request fails.
    """
    if not _TRAFILATURA_AVAILABLE:
        raise RuntimeError(
            "trafilatura is not installed. "
            "Add it to pyproject.toml dependencies."
        )

    async with httpx.AsyncClient(
        timeout=20.0,
        follow_redirects=True,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (compatible; LingoFlow/0.1; "
                "+https://github.com/lingoflow)"
            )
        },
    ) as client:
        response = await client.get(url)
        response.raise_for_status()
        html = response.text

    # trafilatura.bare_extraction returns a dict or None
    result = trafilatura.bare_extraction(
        html,
        url=url,
        include_tables=False,
        include_comments=False,
        with_metadata=True,
        output_format="python",
    )

    if not result:
        # Fall back to basic HTML meta tag extraction
        return _fallback_extract(url, html)

    title: str = result.get("title") or _url_to_title(url)
    language: str | None = result.get("language") or None
    description: str | None = result.get("description") or None
    body: str | None = result.get("text") or None
    author: str | None = result.get("author") or None

    return ArticleMetadata(
        external_id=f"article:{_url_hash(url)}",
        title=title,
        url=url,
        language=language,
        description=description,
        body=body,
        author=author,
    )


def _url_hash(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()[:16]


def _url_to_title(url: str) -> str:
    """Best-effort title from the URL path when no title is found."""
    from urllib.parse import urlparse

    path = urlparse(url).path.rstrip("/")
    slug = path.split("/")[-1] if path else url
    return slug.replace("-", " ").replace("_", " ").title() or url


def _fallback_extract(url: str, html: str) -> ArticleMetadata:
    """Minimal HTML meta-tag extraction when trafilatura returns nothing."""
    import re

    def _meta(name: str) -> str | None:
        patterns = [
            rf'<meta\s+name=["\']og:{name}["\']\s+content=["\'](.*?)["\']',
            rf'<meta\s+property=["\']og:{name}["\']\s+content=["\'](.*?)["\']',
            rf'<meta\s+name=["\']{name}["\']\s+content=["\'](.*?)["\']',
        ]
        for pat in patterns:
            m = re.search(pat, html, re.IGNORECASE | re.DOTALL)
            if m:
                return m.group(1).strip()
        return None

    title_match = re.search(
        r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL
    )
    raw_title = title_match.group(1).strip() if title_match else None
    title = raw_title or _meta("title") or _url_to_title(url)

    return ArticleMetadata(
        external_id=f"article:{_url_hash(url)}",
        title=title,
        url=url,
        language=_meta("language"),
        description=_meta("description"),
        body=None,
        author=_meta("author"),
    )
