"""Tests for Snake and Direction foundational types."""

import pytest

from src.game.snake import (
    UP,
    DOWN,
    LEFT,
    RIGHT,
    VALID_DIRECTIONS,
    opposite,
    validate_direction,
    Snake,
)
from src.game.grid import Grid, GRID_WIDTH, GRID_HEIGHT


class TestSnake:
    """Test Snake dataclass creation and constraints."""

    def test_snake_creation_valid_segments(self) -> None:
        """Snake must accept valid segments and direction."""
        segments = ((5, 5), (5, 6), (5, 7))
        s = Snake(segments=segments, direction=UP)
        assert s.head == (5, 5)
        assert s.length == 3

    def test_snake_head_first_ordering(self) -> None:
        """First segment must be the head."""
        segments = ((10, 10), (10, 11), (10, 12))
        s = Snake(segments=segments, direction=DOWN)
        assert s.head == (10, 10)

    def test_snake_connected_chain_constraint(self) -> None:
        """Adjacent segments must be Manhattan-distance 1 apart."""
        # Valid: each segment is adjacent to the next
        segments = ((5, 5), (6, 5), (6, 6), (5, 6))
        s = Snake(segments=segments, direction=UP)
        assert s.length == 4

    def test_snake_empty_segments_rejects(self) -> None:
        """Snake must reject empty segments."""
        with pytest.raises(ValueError, match="at least one segment"):
            Snake(segments=(), direction=RIGHT)

    def test_snake_duplicate_coordinates_rejects(self) -> None:
        """Snake must reject duplicate segment coordinates."""
        segments = ((5, 5), (5, 5), (5, 6))
        with pytest.raises(ValueError, match="unique coordinates"):
            Snake(segments=segments, direction=RIGHT)

    def test_snake_disconnected_segments_rejects(self) -> None:
        """Snake must reject non-adjacent segments."""
        segments = ((5, 5), (5, 7), (5, 8))  # gap between seg 0 and 1
        with pytest.raises(ValueError, match="not connected"):
            Snake(segments=segments, direction=DOWN)

    def test_snake_invalid_direction_rejects(self) -> None:
        """Snake must reject invalid direction values."""
        segments = ((5, 5), (5, 6))
        with pytest.raises(ValueError, match="Invalid direction"):
            Snake(segments=segments, direction=(0, 0))

    def test_snake_is_frozen(self) -> None:
        """Snake must be immutable (frozen dataclass)."""
        segments = ((5, 5), (5, 6))
        s = Snake(segments=segments, direction=RIGHT)
        with pytest.raises(Exception):
            s.segments = ((10, 10), (10, 11))  # type: ignore[assignment]

    def test_snake_length_derived(self) -> None:
        """Length must be len(segments)."""
        for n in [1, 2, 3, 10, 100]:
            segments = ((i, 0) for i in range(n))
            segments = tuple((i, 0) for i in range(n))
            s = Snake(segments=segments, direction=RIGHT)
            assert s.length == n


class TestDirection:
    """Test direction constants and utilities."""

    def test_direction_constants(self) -> None:
        """Direction values must be unit vectors: exactly one non-zero component."""
        assert UP == (0, -1)
        assert DOWN == (0, 1)
        assert LEFT == (-1, 0)
        assert RIGHT == (1, 0)

    def test_all_valid_directions(self) -> None:
        """VALID_DIRECTIONS must contain exactly the 4 cardinal directions."""
        expected = {UP, DOWN, LEFT, RIGHT}
        assert VALID_DIRECTIONS == expected
        assert len(VALID_DIRECTIONS) == 4

    def test_opposite_up_is_down(self) -> None:
        assert opposite(UP) == DOWN

    def test_opposite_down_is_up(self) -> None:
        assert opposite(DOWN) == UP

    def test_opposite_left_is_right(self) -> None:
        assert opposite(LEFT) == RIGHT

    def test_opposite_right_is_left(self) -> None:
        assert opposite(RIGHT) == LEFT

    def test_opposite_is_reverse(self) -> None:
        """Opposite of a direction must be its negation."""
        for d in VALID_DIRECTIONS:
            assert opposite(d) == (-d[0], -d[1])

    def test_validate_valid_direction(self) -> None:
        """validate_direction must not raise for valid directions."""
        for d in VALID_DIRECTIONS:
            validate_direction(d)  # should not raise

    def test_validate_invalid_direction_raises(self) -> None:
        """validate_direction must raise ValueError for invalid directions."""
        invalid = [
            (0, 0),      # no movement
            (1, 1),      # diagonal
            (-1, -1),    # diagonal
            (2, 0),      # not unit
            (0, 2),      # not unit
            (1, -1),     # diagonal
        ]
        for d in invalid:
            with pytest.raises(ValueError, match="Invalid direction"):
                validate_direction(d)

    def test_unit_vector_constraint(self) -> None:
        """Each valid direction must satisfy abs(dx) + abs(dy) == 1."""
        for d in VALID_DIRECTIONS:
            assert abs(d[0]) + abs(d[1]) == 1
