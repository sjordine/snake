"""Collision detection for Snake game."""


def check_wall_collision(
    new_head: tuple[int, int],
    grid_width: int = 20,
    grid_height: int = 20,
) -> bool:
    """Check if new_head is outside grid boundaries.

    Constraint: new head outside [0, width-1] x [0, height-1] triggers game over (per FR-010).

    Args:
        new_head: The proposed new head position (x, y).
        grid_width: Number of columns (default 20).
        grid_height: Number of rows (default 20).

    Returns:
        True if the new head is outside the grid.
    """
    x, y = new_head
    return not (0 <= x < grid_width and 0 <= y < grid_height)


def check_self_collision(
    new_head: tuple[int, int],
    snake_segments: tuple[tuple[int, int], ...],
    tail_removed: bool = True,
) -> bool:
    """Check if new_head collides with any snake body segment.

    Constraint: new head in snake segments excluding tail if not growing (per data-model.md).

    Args:
        new_head: The proposed new head position (x, y).
        snake_segments: Current segments tuple (head first).
        tail_removed: Whether the tail will be removed this tick.
                      If True, tail is excluded from collision check
                      (snake moves away, so tail position is safe).

    Returns:
        True if the new head is on a body segment.
    """
    # If tail is being removed, it won't occupy that cell anymore
    if tail_removed and len(snake_segments) > 1:
        segments_to_check = snake_segments[:-1]
    else:
        segments_to_check = snake_segments

    return new_head in segments_to_check
