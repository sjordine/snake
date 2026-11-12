"""Snake entity and Direction constants."""

from dataclasses import dataclass

# Direction vectors as (dx, dy) tuples
# x increases to the right, y increases downward
UP: tuple[int, int] = (0, -1)
DOWN: tuple[int, int] = (0, 1)
LEFT: tuple[int, int] = (-1, 0)
RIGHT: tuple[int, int] = (1, 0)

VALID_DIRECTIONS: frozenset[tuple[int, int]] = frozenset([UP, DOWN, LEFT, RIGHT])


def opposite(d: tuple[int, int]) -> tuple[int, int]:
    """Return the opposite direction of d.

    Constraints:
    - Exactly one of dx, dy is non-zero (unit vector constraint).
    - No diagonal movement: abs(dx) + abs(dy) == 1.
    """
    return (-d[0], -d[1])


def validate_direction(d: tuple[int, int]) -> None:
    """Validate that d is a valid direction (unit vector, no diagonal).

    Raises ValueError if the direction is invalid.
    """
    if d not in VALID_DIRECTIONS:
        raise ValueError(
            f"Invalid direction {d}. Must be one of UP, DOWN, LEFT, RIGHT."
        )


@dataclass(frozen=True)
class Snake:
    """A snake entity with segments, direction, and length.

    Constraints (per data-model.md):
    - segments: tuple[tuple[int, int], ...] (head first, index 0).
    - No duplicate coordinates.
    - Head within grid boundaries (validated externally).
    - Adjacent segments Manhattan-distance 1 apart (connected chain).
    - segments non-empty (length >= 1).
    """

    segments: tuple[tuple[int, int], ...]
    direction: tuple[int, int]

    @property
    def length(self) -> int:
        """Number of segments."""
        return len(self.segments)

    @property
    def head(self) -> tuple[int, int]:
        """Head position (first segment)."""
        return self.segments[0]

    def __post_init__(self) -> None:
        # Non-empty check
        if len(self.segments) < 1:
            raise ValueError("Snake must have at least one segment")

        # No duplicate coordinates
        if len(set(self.segments)) != len(self.segments):
            raise ValueError("Snake segments must have unique coordinates")

        # Adjacent segments must be Manhattan-distance 1 apart
        for i in range(len(self.segments) - 1):
            dx = abs(self.segments[i][0] - self.segments[i + 1][0])
            dy = abs(self.segments[i][1] - self.segments[i + 1][1])
            if dx + dy != 1:
                raise ValueError(
                    f"Snake segments not connected: "
                    f"{self.segments[i]} and {self.segments[i + 1]}"
                )

        # Validate direction is a valid direction tuple
        validate_direction(self.direction)
