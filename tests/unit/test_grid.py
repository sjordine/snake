"""Tests for Grid foundational type."""

import pytest

from src.game.grid import Grid, GRID_WIDTH, GRID_HEIGHT


class TestGrid:
    """Test Grid creation and validation."""

    def test_default_dimensions(self) -> None:
        """Grid defaults must be 20x20 (per FR-001)."""
        g = Grid()
        assert g.width == GRID_WIDTH
        assert g.height == GRID_HEIGHT
        assert g.width == 20
        assert g.height == 20

    def test_custom_dimensions(self) -> None:
        """Grid must accept custom positive dimensions."""
        g = Grid(width=10, height=10)
        assert g.width == 10
        assert g.height == 10

    def test_default_occupied_is_empty(self) -> None:
        """Default occupied set must be empty."""
        g = Grid()
        assert g.occupied == frozenset()

    def test_negative_dimensions_reject(self) -> None:
        """Grid must reject non-positive dimensions."""
        with pytest.raises(ValueError, match="must be positive"):
            Grid(width=0, height=20)
        with pytest.raises(ValueError, match="must be positive"):
            Grid(width=20, height=-1)

    def test_occupied_outside_bounds_reject(self) -> None:
        """Grid must reject occupied coordinates outside bounds."""
        occupied = {(20, 10)}  # x=20 is out of [0, 19] for width=20
        with pytest.raises(ValueError, match="outside grid bounds"):
            Grid(width=20, height=20, occupied=frozenset(occupied))

        occupied = {(10, 20)}  # y=20 is out of [0, 19] for height=20
        with pytest.raises(ValueError, match="outside grid bounds"):
            Grid(width=20, height=20, occupied=frozenset(occupied))

        occupied = {(-1, 0)}  # negative x
        with pytest.raises(ValueError, match="outside grid bounds"):
            Grid(width=20, height=20, occupied=frozenset(occupied))

    def test_occupied_inside_bounds_accepted(self) -> None:
        """Grid must accept occupied coordinates within bounds."""
        occupied = {(0, 0), (19, 19), (10, 5)}
        g = Grid(width=20, height=20, occupied=frozenset(occupied))
        assert g.occupied == frozenset(occupied)

    def test_cell_count(self) -> None:
        """cell_count must be width * height."""
        g = Grid(width=20, height=20)
        assert g.cell_count == 400

        g = Grid(width=10, height=10)
        assert g.cell_count == 100

    def test_empty_cells(self) -> None:
        """empty_cells must exclude occupied coordinates."""
        occupied = {(5, 5), (10, 10)}
        g = Grid(width=20, height=20, occupied=frozenset(occupied))
        empty = g.empty_cells
        assert (5, 5) not in empty
        assert (10, 10) not in empty
        assert len(empty) == 400 - 2

    def test_empty_cells_all_when_no_occupied(self) -> None:
        """When no cells are occupied, empty_cells must equal all cells."""
        g = Grid()
        assert g.empty_cells == frozenset(
            (x, y) for x in range(20) for y in range(20)
        )

    def test_grid_is_frozen(self) -> None:
        """Grid must be immutable (frozen dataclass)."""
        g = Grid()
        with pytest.raises(Exception):
            g.width = 10  # type: ignore[assignment]
