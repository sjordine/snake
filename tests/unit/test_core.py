"""Tests for Score foundational type."""

import pytest

from src.game.core import Score


class TestScore:
    """Test Score creation and increment logic."""

    def test_score_starts_at_zero(self) -> None:
        """Score must start at 0 (per FR-009)."""
        s = Score()
        assert s.value == 0

    def test_score_custom_value(self) -> None:
        """Score must accept custom non-negative values."""
        s = Score(value=5)
        assert s.value == 5

    def test_negative_score_rejects(self) -> None:
        """Score must reject negative values (per data-model.md: value >= 0)."""
        with pytest.raises(ValueError, match="non-negative"):
            Score(value=-1)

    def test_score_increments_by_one(self) -> None:
        """Score must increment by exactly 1 per food eaten (per FR-008)."""
        s = Score()
        s2 = s.increment()
        assert s2.value == 1
        assert s.value == 0  # original unchanged (frozen)

    def test_score_100_eats(self) -> None:
        """Score must be exactly 100 after 100 increments (per SC-003)."""
        s = Score()
        for _ in range(100):
            s = s.increment()
        assert s.value == 100

    def test_score_persists_across_operations(self) -> None:
        """Score must persist its value (immutable)."""
        s = Score(value=42)
        s2 = Score()  # unrelated score
        assert s2.value == 0
        assert s.value == 42  # original unchanged

    def test_score_is_positive_after_increment(self) -> None:
        """is_positive must be True after at least one increment."""
        s = Score()
        assert s.is_positive is False
        s2 = s.increment()
        assert s2.is_positive is True
