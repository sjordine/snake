"""Food item on the grid with deterministic spawn."""

from dataclasses import dataclass
from typing import Optional
import random

from .grid import Grid


@dataclass(frozen=True)
class Food:
    """A single food item at a grid coordinate.

    Constraints:
    - position must be within grid boundaries.
    - position must NOT be in the snake's occupied set (per FR-007).
    - Spawned by selecting uniformly from empty cells using injected RNG.
    """

    position: tuple[int, int]

    @staticmethod
    def spawn(
        occupied_cells: frozenset[tuple[int, int]],
        grid_width: int = 20,
        grid_height: int = 20,
        rng: Optional[random.Random] = None,
    ) -> "Food":
        """Spawn food at a random empty cell.

        Uses injected RNG for deterministic food spawn (per Principle III).
        Constraint: food never spawns on a cell occupied by the snake (FR-007).

        Args:
            occupied_cells: Set of grid coordinates occupied by the snake.
            grid_width: Number of columns (default 20).
            grid_height: Number of rows (default 20).
            rng: Injected random.Random instance for determinism. Uses
                 random.Random() (system entropy) if not provided.

        Returns:
            A Food instance positioned at an empty cell.

        Raises:
            ValueError: If there are no empty cells available.
        """
        empty_cells = [
            (x, y)
            for x in range(grid_width)
            for y in range(grid_height)
            if (x, y) not in occupied_cells
        ]
        if not empty_cells:
            raise ValueError("Cannot spawn food: no empty cells available")

        if rng is None:
            rng = random.Random()
        index = rng.randint(0, len(empty_cells) - 1)
        return Food(position=empty_cells[index])

    @staticmethod
    def is_at(food_pos: tuple[int, int], head_pos: tuple[int, int]) -> bool:
        """Check if food position matches a given position.

        Returns:
            True if the food has been reached/eaten.
        """
        return food_pos == head_pos
