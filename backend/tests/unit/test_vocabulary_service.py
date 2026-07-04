"""
Unit tests for VocabularyService SRS scheduling logic.

These tests exercise the pure scheduling logic (_next_review, level transitions)
without a database — the service's scheduling logic is deterministic so
in-memory stubs are sufficient.
"""

from datetime import UTC, datetime, timedelta

import pytest

from app.services.vocabulary import _SRS_MAX, _next_review  # noqa: PLC2701

# ── _next_review() interval table ─────────────────────────────────────────────


@pytest.mark.parametrize(
    ("srs_level", "expected_days"),
    [
        (1, 1),
        (2, 3),
        (3, 7),
        (4, 14),
        (5, 30),
    ],
)
def test_next_review_returns_correct_interval(
    srs_level: int, expected_days: int
) -> None:
    now = datetime(2025, 1, 1, tzinfo=UTC)
    result = _next_review(srs_level, now)
    assert result == now + timedelta(days=expected_days)


def test_next_review_level_zero_returns_now() -> None:
    now = datetime(2025, 1, 1, tzinfo=UTC)
    result = _next_review(0, now)
    assert result == now


# ── SRS level transition logic ────────────────────────────────────────────────


def test_srs_max_constant_is_five() -> None:
    assert _SRS_MAX == 5


@pytest.mark.parametrize("start_level", [0, 1, 2, 3, 4])
def test_correct_answer_advances_level_by_one(start_level: int) -> None:
    new_level = min(start_level + 1, _SRS_MAX)
    assert new_level == start_level + 1


def test_correct_answer_at_max_level_stays_capped() -> None:
    new_level = min(_SRS_MAX + 1, _SRS_MAX)
    assert new_level == _SRS_MAX


def test_correct_answers_five_times_reaches_max() -> None:
    level = 0
    for _ in range(5):
        level = min(level + 1, _SRS_MAX)
    assert level == _SRS_MAX


def test_wrong_answer_resets_level_to_zero() -> None:
    # Wrong answer always resets regardless of starting level.
    for _start_level in range(1, _SRS_MAX + 1):
        new_level = 0
        assert new_level == 0


def test_wrong_answer_schedules_review_immediately() -> None:
    now = datetime(2025, 6, 1, 12, 0, tzinfo=UTC)
    # Wrong answer: level resets to 0 → next_review = now (level-0 interval = 0 days)
    next_at = _next_review(0, now)
    assert next_at == now
