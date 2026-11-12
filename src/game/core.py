"""Score tracking and core game state for Snake."""

from dataclasses import dataclass
import random

from .grid import GRID_WIDTH, GRID_HEIGHT, Grid
from .snake import RIGHT
from .food import Food
from .collision import check_wall_collision, check_self_collision


@dataclass(frozen=True)
class Score:
    """A non-negative integer tracking food consumed.

    Constraints:
    - value >= 0 at all times (per data-model.md).
    - Increments by exactly 1 per food eaten (per FR-008).
    - Persists across game ticks without reset (per FR-009).
    """

    value: int = 0

    def __post_init__(self) -> None:
        if self.value < 0:
            raise ValueError("Score value must be non-negative (>= 0)")

    @property
    def is_positive(self) -> bool:
        """Return True if score is greater than zero."""
        return self.value > 0

    def increment(self) -> "Score":
        """Return a new Score incremented by exactly 1.

        Constraint: increments by exactly 1 per food eaten (per FR-008).
        """
        return Score(value=self.value + 1)


@dataclass
class GameState:
    """The aggregate state combining all game entities.

    This is the primary type returned by the pure core simulation.
    Immutable in spirit — every tick produces a NEW GameState;
    the old one is never mutated.

    Constraints:
    - When game_over = True, no further tick() calls should produce state changes.
    - occupied derived from snake segments must always be consistent.
    - All coordinate values use (column, row) / (x, y) ordering:
      x=0 is left column, y=0 is top row.
    """

    grid: Grid
    snake_segments: tuple[tuple[int, int], ...]  # head first, index 0
    snake_direction: tuple[int, int]
    food_position: tuple[int, int]
    score: int
    game_over: bool
    rng: random.Random  # injected for deterministic food spawn

    @property
    def snake_length(self) -> int:
        """Number of snake segments."""
        return len(self.snake_segments)

    @property
    def head(self) -> tuple[int, int]:
        """Current snake head position (first segment)."""
        return self.snake_segments[0]

    @property
    def occupied(self) -> frozenset[tuple[int, int]]:
        """Set of grid coordinates occupied by the snake (derived)."""
        return frozenset(self.snake_segments)

    @classmethod
    def initial(
        cls,
        seed: int = 42,
        grid_width: int = 20,
        grid_height: int = 20,
        start_length: int = 3,
    ) -> "GameState":
        """Create the initial game state.

        Args:
            seed: Random seed for deterministic food spawn.
            grid_width: Grid column count (default 20).
            grid_height: Grid row count (default 20).
            start_length: Initial snake length (default 3, centered).

        Returns:
            A GameState with snake centered, moving right, food spawned, score=0.
        """
        grid = Grid(width=grid_width, height=grid_height)
        rng = random.Random(seed)

        # Center the snake: head at center, body extending to the left
        head_x = grid_width // 2
        head_y = grid_height // 2
        segments: tuple[tuple[int, int], ...] = tuple(
            (head_x - i, head_y) for i in range(start_length)
        )

        # Validate initial snake: adjacent segments must be Manhattan-distance 1
        for i in range(len(segments) - 1):
            dx = abs(segments[i][0] - segments[i + 1][0])
            dy = abs(segments[i][1] - segments[i + 1][1])
            if dx + dy != 1:
                raise ValueError(
                    f"Initial snake segments not connected: "
                    f"{segments[i]} and {segments[i + 1]}"
                )

        # No duplicate coordinates
        if len(set(segments)) != len(segments):
            raise ValueError("Initial snake has duplicate segment coordinates")

        # Head within grid boundaries
        hx, hy = segments[0]
        if not (0 <= hx < grid_width and 0 <= hy < grid_height):
            raise ValueError(f"Initial head position ({hx}, {hy}) outside grid")

        food = Food.spawn(
            occupied_cells=frozenset(segments),
            grid_width=grid_width,
            grid_height=grid_height,
            rng=rng,
        )

        return cls(
            grid=grid,
            snake_segments=segments,
            snake_direction=RIGHT,
            food_position=food.position,
            score=0,
            game_over=False,
            rng=rng,
        )


def tick(
    state: GameState,
    new_direction: tuple[int, int],
) -> GameState:
    """Advance the game by one tick.

    Pure function: produces a NEW GameState without mutating the input.

    Algorithm (per data-model.md GameState core simulation method):
    1. Validate and apply direction change (FR-003, FR-004).
    2. Compute new head position from head + direction.
    3. Check wall collision: if new head outside grid → game_over = True, return.
    4. Check self collision: if new head in snake segments (excluding tail if not growing) → game_over = True, return.
    5. Check food collision: if new head == food position → ate_food = True.
    6. Move snake: new head prepended; if not ate_food, tail removed.
    7. If ate_food: score +1; spawn new food using rng.
    8. Return new GameState with updated values.

    Constraints:
    - Direction change only if NOT reversing current direction (FR-004).
    - New head advances one cell per tick (FR-002).
    - Adjacent segments remain Manhattan-distance 1 apart after move.
    - When game_over = True, subsequent tick() calls produce no state changes (per data-model.md).

    Args:
        state: The current GameState.
        new_direction: Desired direction from player input (dx, dy).

    Returns:
        A new GameState reflecting the tick outcome.
    """
    # If game is already over, no state changes (per data-model.md validation rule)
    if state.game_over:
        return state

    from .snake import opposite

    # 1. Validate direction change: reject reversals (FR-004)
    if new_direction == opposite(state.snake_direction):
        # Invalid reversal — keep current direction
        current_direction = state.snake_direction
    else:
        current_direction = new_direction

    # 2. Compute new head position
    head_x, head_y = state.head
    dx, dy = current_direction
    new_head = (head_x + dx, head_y + dy)

    # 3. Check wall collision (FR-010)
    if check_wall_collision(new_head, state.grid.width, state.grid.height):
        return GameState(
            grid=state.grid,
            snake_segments=state.snake_segments,
            snake_direction=state.snake_direction,
            food_position=state.food_position,
            score=state.score,
            game_over=True,
            rng=state.rng,
        )

    # 4. Check self collision
    # Tail is NOT removed yet (food collision checked before removal)
    ate_food = Food.is_at(state.food_position, new_head)
    tail_removed = not ate_food
    if check_self_collision(
        new_head, state.snake_segments, tail_removed=tail_removed
    ):
        return GameState(
            grid=state.grid,
            snake_segments=state.snake_segments,
            snake_direction=state.snake_direction,
            food_position=state.food_position,
            score=state.score,
            game_over=True,
            rng=state.rng,
        )

    # 5. Check food collision — already computed above
    # 6. Move snake: prepend new head
    new_segments = (new_head, *state.snake_segments)
    if not ate_food:
        # Remove tail
        new_segments = new_segments[:-1]

    # 7. If ate food: score +1, spawn new food
    new_score = state.score
    new_food_position = state.food_position
    if ate_food:
        new_score = state.score + 1
        new_food_position = Food.spawn(
            occupied_cells=frozenset(new_segments),
            grid_width=state.grid.width,
            grid_height=state.grid.height,
            rng=state.rng,
        ).position

    # 8. Return new GameState
    return GameState(
        grid=state.grid,
        snake_segments=new_segments,
        snake_direction=current_direction,
        food_position=new_food_position,
        score=new_score,
        game_over=False,
        rng=state.rng,
    )
