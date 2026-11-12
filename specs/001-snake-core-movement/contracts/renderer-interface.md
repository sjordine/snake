# Contract: Core Renderer Interface

**Feature**: 001-snake-core-movement  
**Date**: 2026-11-12  
**Purpose**: Define the contract between the pure game core and any rendering adapter. This ensures that renderers (terminal ASCII, Pygame, web canvas, etc.) can all accept the same GameState without core knowledge of the display technology.

---

## Renderer Protocol

All renderers MUST implement this interface:

```python
class Renderer:
    """
    Renders a GameState to a visual output.

    Contract: Pure core produces GameState; renderer consumes it.
    Renderer MUST have zero dependencies on game logic.
    """

    def render(self, state: GameState) -> None:
        """
        Draw the current game state to the display surface.

        Args:
            state: The current GameState produced by core tick().

        Contract:
            - Must render: grid boundaries, snake segments, food position, score, game-over state.
            - Must be a pure visual operation — no side effects on GameState.
            - Must complete within one frame budget (~16ms at 60fps for Pygame).
        """
        ...

    def should_tick(self) -> bool:
        """
        Determine if a game tick should be processed this frame.

        Returns:
            True if the tick clock has elapsed and a new tick should be computed.

        Contract:
            - Independent of rendering; controlled by tick interval (~100ms for 10 ticks/sec).
            - Pygame renderer uses pygame.time.get_ticks() to implement this.
        """
        ...

    def poll_events(self) -> Optional[Direction]:
        """
        Poll for pending player input and return the desired direction change.

        Returns:
            A Direction (UP/DOWN/LEFT/RIGHT) if input was consumed, or None if no new input.

        Contract:
            - Must only return one direction change per call (no input stacking).
            - Must ignore invalid reversals (renderers do NOT validate; caller does).
            - Pygame renderer polls pygame.event.get() for KEYDOWN events.
        """
        ...
```

---

## GameState Data Contract

The GameState passed to `render()` has this exact shape:

```python
@dataclass(frozen=True)
class GameState:
    grid: Grid           # width: int, height: int
    snake: Snake         # segments: tuple[(int,int), ...], direction: Direction
    food: Food           # position: (int, int)
    score: int           # non-negative integer
    game_over: bool      # True if snake is dead
    rng: random.Random   # injected for deterministic food spawn
```

**Contract rules**:
- GameState is immutable — renderer MUST NOT modify it.
- Renderer MUST NOT import game module internals — only consumes public fields.
- All coordinate values use (column, row) / (x, y) ordering: x=0 is left column, y=0 is top row.

---

## Renderer Selection Contract

The entry point (`main.py`) selects the renderer at startup:

```
--renderer=terminal → TerminalRenderer
--renderer=pygame   → PygameRenderer (default)
```

This is a simple factory pattern — no interfaces, no observers, no DI container (Principle IV: YAGNI).
