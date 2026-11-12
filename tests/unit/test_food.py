"""Tests for food spawning and consumption."""

import pytest

from src.game.food import Food
from src.game.grid import Grid


class TestFood:
    """Test Food creation and spawn logic."""

    def test_food_spawn_on_empty_cell(self) -> None:
        """Food must spawn on a cell NOT in occupied set (per FR-006, FR-007)."""
        occupied = {(5, 5), (10, 10), (15, 15)}
        food = Food.spawn(
            occupied_cells=frozenset(occupied),
            grid_width=20,
            grid_height=20,
        )
        assert food.position not in occupied

    def test_food_spawn_never_on_snake(self) -> None:
        """In multiple runs, food must never spawn on occupied cells."""
        occupied = {(5, 5), (10, 10)}
        for _ in range(100):
            food = Food.spawn(
                occupied_cells=frozenset(occupied),
                grid_width=20,
                grid_height=20,
            )
            assert food.position not in occupied

    def test_food_spawn_single_cell_remaining(self) -> None:
        """When only one empty cell remains, food must spawn there (per spec acceptance scenario 3)."""
        occupied = {(x, y) for x in range(20) for y in range(20)} - {(5, 5)}
        food = Food.spawn(
            occupied_cells=frozenset(occupied),
            grid_width=20,
            grid_height=20,
        )
        assert food.position == (5, 5)

    def test_food_spawn_no_empty_cells_raises(self) -> None:
        """Food spawn must raise ValueError when grid is full."""
        occupied = {(x, y) for x in range(20) for y in range(20)}
        with pytest.raises(ValueError, match="no empty cells"):
            Food.spawn(
                occupied_cells=frozenset(occupied),
                grid_width=20,
                grid_height=20,
            )

    def test_food_spawn_deterministic_with_rng(self) -> None:
        """Same seed must produce same food position."""
        occupied = {(5, 5), (10, 10)}
        rng1 = __import__("random").Random(123)
        rng2 = __import__("random").Random(123)

        f1 = Food.spawn(
            occupied_cells=frozenset(occupied),
            grid_width=20,
            grid_height=20,
            rng=rng1,
        )
        f2 = Food.spawn(
            occupied_cells=frozenset(occupied),
            grid_width=20,
            grid_height=20,
            rng=rng2,
        )
        assert f1.position == f2.position

    def test_food_is_at(self) -> None:
        """is_at must return True when positions match."""
        assert Food.is_at((5, 5), (5, 5)) is True
        assert Food.is_at((5, 5), (10, 10)) is False

    def test_food_is_frozen(self) -> None:
        """Food must be immutable (frozen dataclass)."""
        f = Food(position=(5, 5))
        with pytest.raises(Exception):
            f.position = (10, 10)  # type: ignore[assignment]
