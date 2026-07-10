"""Unit tests for article integration helpers."""

from app.integrations.article import _fallback_extract, _url_hash, _url_to_title


def test_url_hash_is_stable() -> None:
    url = "https://example.com/article"
    assert _url_hash(url) == _url_hash(url)
    assert len(_url_hash(url)) == 16


def test_url_to_title_from_slug() -> None:
    title = _url_to_title("https://example.com/learn-spanish-fast")
    assert title == "Learn Spanish Fast"


def test_fallback_extract_reads_title_and_meta_tags() -> None:
    html = """
    <html>
      <head>
        <title>Fallback Title</title>
        <meta name="description" content="A short summary" />
        <meta name="language" content="es" />
        <meta name="author" content="Jane Doe" />
      </head>
      <body></body>
    </html>
    """

    metadata = _fallback_extract("https://example.com/story", html)

    assert metadata.title == "Fallback Title"
    assert metadata.description == "A short summary"
    assert metadata.language == "es"
    assert metadata.author == "Jane Doe"
    assert metadata.external_id.startswith("article:")
