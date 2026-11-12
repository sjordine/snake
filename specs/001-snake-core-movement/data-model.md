# Data Model: Core Snake Movement

**Feature**: 001-snake-core-movement  
**Date**: 2026-11-12  
**Source**: [spec.md](spec.md)

---

## Entities

### Grid

A fixed-dimension 2D cell map that defines the playable area.

| Field | Type | Description |
|-------|------|-------------|
| `width` | `int` | Number of columns (always 20 per FR-001). |
| `height` | `int` | Number of rows (always 20 per FR-001). |
| `occupied` | `set[tuple[int, int]]` | Set of grid coordinates currently occupied by the snake. |

**Validation**:
- `width` and `height` must be positive integers.
- `occupied` must only contain coordinates within `[0, width-1] × [0, height-1]`.
- After any update, `occupied` must match the actual snake segments (source of truth is the snake; occupied is derived).

**Relationships**:
- Referenced by `GameState` for boundary checks.
- Referenced by `Food` spawn logic to find empty cells.

---

### Direction

A unit vector representing the snake's movement direction.

| Field | Type | Description |
|-------|------|-------------|
| `dx` | `int` | X component: +1 (right), -1 (left), 0 (none). |
| `dy` | `int` | Y component: +1 (down), -1 (up), 0 (none). |

**Possible values**: `RIGHT = (1, 0)`, `LEFT = (-1, 0)`, `UP = (0, -1)`, `DOWN = (0, 1)`

**Validation**:
- Exactly one of `dx`, `dy` is non-zero (unit vector constraint).
- No diagonal movement: `abs(dx) + abs(dy) == 1`.

---

### Snake

The snake is an ordered sequence of grid coordinates, head-first.

| Field | Type | Description |
|-------|------|-------------|
| `segments` | `tuple[tuple[int, int], ...]` | Ordered list of (x, y) coordinates. Index 0 is the head. |
| `direction` | `Direction` | Current movement direction. |
| `length` | `int` | Number of segments (len(segments)). |

**Validation**:
- `segments` must be non-empty (length ≥ 1).
- No duplicate coordinates in `segments` (the snake cannot cross itself normally).
- Head must be within grid boundaries.
- Adjacent segments must be Manhattan-distance 1 apart (connected chain).

**Immutable operations** (return new Snake):
- `move(new_head, ate_food)`: Returns new Snake with head moved to `new_head`. If `ate_food` is False, tail segment is removed. If True, tail is preserved (grow).
- `change_direction(new_dir)`: Returns new Snake with updated direction. If `new_dir` reverses current direction, returns unchanged (ignored per FR-004).

---

### Food

A single food item at a grid coordinate.

| Field | Type | Description |
|-------|------|-------------|
| `position` | `tuple[int, int]` | Grid coordinate (x, y) where food is located. |

**Validation**:
- `position` must be within grid boundaries.
- `position` must NOT be in the snake's `occupied` set (per FR-007).
- Spawned by selecting uniformly from `all_empty_cells` using injected RNG.

**State transitions**:
- `spawn(occupied_cells, rng) → Food`: Chooses random empty cell.
- `consume(food_position, snake_head) → bool`: Returns True if head reached food.

---

### Score

A non-negative integer tracking food consumed.

| Field | Type | Description |
|-------|------|-------------|
| `value` | `int` | Total food consumed. Starts at 0. |

**Validation**:
- `value` ≥ 0 at all times.
- Increments by exactly 1 per food eaten (per FR-008).
- Persists across game ticks without reset (per FR-009).

---

### GameState

The aggregate state combining all entities. This is the primary type returned by the pure core simulation.

| Field | Type | Description |
|-------|------|-------------|
| `grid` | `Grid` | The playing area dimensions. |
| `snake` | `Snake` | Snake segments, direction, length. |
| `food` | `Food` | Current food position. |
| `score` | `Score` | Current score value. |
| `game_over` | `bool` | Game over flag (wall collision or self-collision). |
| `rng` | `random.Random` | Injected RNG instance for deterministic food spawn. |

**Core simulation method** — `tick(game_state, new_direction) → GameState`:
1. Validate and apply direction change (FR-003, FR-004).
2. Compute new head position from head + direction.
3. Check wall collision: if new head outside grid → `game_over = True`, return.
4. Check self collision: if new head in snake segments (excluding tail if not growing) → `game_over = True`, return.
5. Check food collision: if new head == food position → ate_food = True.
6. Move snake: new head prepended; if not ate_food, tail removed.
7. If ate_food: score +1; spawn new food using `rng`.
8. Return new GameState with updated values.

**Validation**:
- When `game_over = True`, no further `tick()` calls should produce state changes (or they should be no-ops).
- `occupied` derived from snake segments must always be consistent.

---

## Relationships Diagram

```
GameState
├── grid (Grid)
│   └── occupied ← derived from snake.segments
├── snake (Snake)
│   ├── segments → tuple[(x, y), ...]
│   └── direction → (dx, dy)
├── food (Food)
│   └── position → (x, y)
├── score (Score)
├── game_over → bool
└── rng → Random(seed)
```

## Immutable Data Flow

```
InitialState ──tick(direct)──> GameState₁ ──tick(direct)──> GameState₂ ──...
    │                             │                          │
    └── segments                  └── segments               └── segments
    └── food      ─consume─────> └── food                     └── food
    └── score                     └── score +1               └── score +1
```

Each tick produces a new GameState; no mutations occur in-place. This is the deterministic replay model required by Principle III.
