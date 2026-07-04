"""Shared helpers for mapping Python enums to PostgreSQL enum types."""

import enum
from collections.abc import Iterable


def enum_values(enum_cls: type[enum.Enum]) -> Iterable[str]:
    """
    Use as `values_callable` on SQLAlchemy's Enum type so the database
    stores each member's *value* (e.g. "youtube") instead of its *name*
    (e.g. "YOUTUBE"), which SQLAlchemy sends by default.
    """
    return [member.value for member in enum_cls]
