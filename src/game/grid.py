"""Grid dimensions and occupancy for the Snake game."""

from dataclasses import dataclass


GRID_WIDTH: int = 20
GRID_HEIGHT: int = 20


@dataclass(frozen=True)
class Grid:
    """A fixed-dimension 2D cell map defining the playable area.

    Constraints:
    - width and height must be positive integers (always 20 per FR-001).
    - occupied must only contain coordinates within [0, width-1] x [0, height-1].
    - occupied is derived from snake segments; source of truth is the snake.
    """

    width: int = GRID_WIDTH
    height: int = GRID_HEIGHT
    occupied: frozenset[tuple[int, int]] = frozenset()

    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0:
            raise ValueError(f"Grid dimensions must be positive (got {self.width}x{self.height})")
        for x, y in self.occupied:
            if not (0 <= x < self.width and 0 <= y < self.height):
                raise ValueError(
                    f"Occupied coordinate ({x}, {y}) is outside grid bounds "
                    f"[0, {self.width - 1}] x [0, {self.height - 1}]"
                )

    @property
    def cell_count(self) -> int:
        """Total number of cells in the grid."""
        return self.width * self.height

    @property
    def empty_cells(self) -> frozenset[tuple[int, int]]:
        """All cells not occupied by the snake."""
        return frozenset(
            (x, y)
            for x in range(self.width)
            for y in range(self.height)
            if (x, y) not in self.occupied
        )
