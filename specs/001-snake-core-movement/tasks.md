---

description: "Task list for Core Snake Movement implementation"

---

# Tasks: Core Snake Movement, Food Spawning, and Score Tracking

**Feature Branch**: `001-snake-core-movement`
**Date**: 2026-11-12
**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)
**Constitution**: [constitution.md](../../.specify/memory/constitution.md)

**Tests**: Enabled — Constitution Principle II (Test-First, NON-NEGOTIABLE) requires every feature change to begin with a failing `pytest`. All core tasks follow Red → Green → Refactor.

---

## Phase 1: Setup

Project initialization and directory structure.

- [X] T001 Create `pyproject.toml` with project metadata, dependencies (`pygame`, `pytest`), and pytest configuration with `pythonpath = ["src"]`
- [X] T002 [P] Create directory structure: `src/game/`, `src/render/`, `src/input/`, `tests/unit/`, `tests/integration/`
- [X] T003 [P] Create `__init__.py` files for `src/game/`, `src/render/`, `src/input/`, `tests/unit/`, `tests/integration/`

---

## Phase 2: Foundational Types

Implement immutable data classes for all core entities. No game logic yet — types only.

- [X] T004 Create `src/game/grid.py` — `@dataclass(frozen=True)` Grid with fields `width: int` (constraint: always 20 per FR-001), `height: int` (constraint: always 20 per FR-001), `occupied: frozenset[tuple[int, int]]`. Include constants `GRID_WIDTH = 20`, `GRID_HEIGHT = 20`. Validate that occupied coordinates are within `[0, width-1] × [0, height-1]`.
- [X] T005 Create `src/game/snake.py` — Direction as `tuple[int, int]` with module-level constants `UP = (0, -1)`, `DOWN = (0, 1)`, `LEFT = (-1, 0)`, `RIGHT = (1, 0)`. Constraint: exactly one of dx, dy is non-zero (`abs(dx) + abs(dy) == 1`, per data-model.md).
- [X] T006 Create `src/game/snake.py` — `@dataclass(frozen=True)` Snake with `segments: tuple[tuple[int, int], ...]` (head first, index 0), `direction: tuple[int, int]`, `length: int` (derived as `len(segments)`). Constraints: segments non-empty (length ≥ 1), no duplicate coordinates, head within grid boundaries, adjacent segments Manhattan-distance 1 apart (connected chain).
- [X] T007 Create `src/game/food.py` — `@dataclass(frozen=True)` Food with `position: tuple[int, int]`. Constraint: position must be within grid boundaries and NOT in occupied cells (per FR-007: food never spawns on snake).
- [X] T008 Create `src/game/core.py` — `@dataclass(frozen=True)` Score with `value: int`. Constraint: value ≥ 0 at all times (per data-model.md), increments by exactly 1 per food eaten (per FR-008).
- [X] T009 Create `src/game/core.py` — `@dataclass(frozen=True)` GameState with `grid: Grid`, `snake: Snake`, `food: Food`, `score: int`, `game_over: bool`, `rng: random.Random`. This is the primary aggregate type returned by the pure core simulation (per data-model.md).

---

## Phase 3: User Story 1 — Control Snake Movement (P1)

The player controls snake movement with arrow keys. Movement, direction changes, reversal prevention, and collision detection.

**Independent Test**: A snake moves one cell per tick in all four directions. Invalid reversals are ignored. Wall and self-collision trigger game over.

### Tests (Red)

- [X] T010 [US1] Write `tests/unit/test_snake.py` — test Snake creation with valid segments, valid direction, head-first ordering, connected chain constraint (`abs(seg0.x - seg1.x) + abs(seg0.y - seg1.y) == 1`)
- [X] T011 [US1] Write `tests/unit/test_core.py::test_tick_moves_snake_one_cell` — verify snake head advances by one cell per tick in current direction (per FR-002: snake moves one cell per tick)
- [X] T012 [US1] Write `tests/unit/test_core.py::test_tick_direction_change` — verify direction change takes effect on next tick (per FR-003: player can change direction via keyboard input)
- [X] T013 [US1] Write `tests/unit/test_core.py::test_tick_reversal_ignored` — verify pressing left while moving right does NOT change direction (per FR-004: snake cannot reverse into itself; per spec acceptance scenario: pressing left while moving right is ignored)
- [X] T014 [US1] Write `tests/unit/test_core.py::test_tick_wall_collision` — verify `game_over = True` when head moves outside grid boundaries (per FR-010: snake dies when head moves outside grid; per data-model.md: head must be within `[0, width-1] × [0, height-1]`)
- [X] T015 [US1] Write `tests/unit/test_core.py::test_tick_self_collision` — verify `game_over = True` when head moves into any body segment (per spec edge case: snake cannot reverse into itself)
- [X] T016 [US1] Write `tests/unit/test_core.py::test_tick_tail_removed_on_move` — verify tail segment is removed when snake moves without eating (per spec acceptance scenario 4: head moves to (2,1), tail at (2,4) is removed)

### Implementation (Green)

- [X] T017 [US1] Implement `src/game/collision.py` — `check_wall_collision(new_head: tuple[int, int], grid: Grid) -> bool` (constraint: new head outside `[0, width-1] × [0, height-1]`), `check_self_collision(new_head: tuple[int, int], snake: Snake, tail_removed: bool) -> bool` (constraint: new head in snake segments excluding tail if not growing)
- [X] T018 [US1] Implement `src/game/core.py` — `tick(state: GameState, new_direction: tuple[int, int]) -> GameState` function with: direction change validation (invalid reversals ignored per FR-004), new head computation, wall collision check, self collision check, snake move (prepending new head, removing tail if not growing). Constraints: direction change only if not reversing current direction, adjacent segments remain Manhattan-distance 1 apart after move.
- [X] T019 [US1] Implement `src/game/core.py` — game over handling: when `game_over = True`, subsequent `tick()` calls produce no state changes (per data-model.md validation rule).

---

## Phase 4: User Story 2 — Spawn Food on Grid (P1)

Food appears on empty cells, is consumed when snake reaches it, and respawns on a different empty cell.

**Independent Test**: Food spawns on an empty cell (never on snake), snake eats it, new food spawns elsewhere.

### Tests (Red)

- [X] T020 [US2] Write `tests/unit/test_food.py::test_food_spawn_on_empty_cell` — verify food spawns on a cell NOT in occupied set (per FR-006: food spawns on random empty cell; per FR-007: food never spawns on snake)
- [X] T021 [US2] Write `tests/unit/test_food.py::test_food_spawn_never_on_snake` — verify invariant: food position is always excluded from `occupied` cells (constraint: position must NOT be in snake's occupied set per data-model.md)
- [X] T022 [US2] Write `tests/unit/test_food.py::test_food_spawn_single_cell_remaining` — verify food spawns on the single remaining empty cell when grid is nearly full (per spec acceptance scenario 3)
- [X] T023 [US2] Write `tests/unit/test_core.py::test_tick_eats_food` — verify food is consumed when head reaches food position, snake grows by one segment (per FR-005: snake grows by one segment when eating food)
- [X] T024 [US2] Write `tests/unit/test_core.py::test_tick_new_food_after_eat` — verify new food spawns at a different empty cell after old food is consumed

### Implementation (Green)

- [X] T025 [US2] Implement `src/game/food.py` — `spawn(occupied_cells: frozenset[tuple[int, int]], grid_width: int, grid_height: int, rng: random.Random) -> Food` function: compute all empty cells as `[(x, y) for x in range(width) for y in range(height) if (x, y) not in occupied]`, select one uniformly using `rng.randint(0, len(empty) - 1)`. Constraint: `rng` must be injected, never use global `random` module (per research.md decision and constitution Principle III).
- [X] T026 [US2] Implement `src/game/core.py` — integrate food spawn into `tick()`: when `new_head == food.position`, mark ate_food = True, set new food position via `spawn()`, increment score (cross-cutting with US3).

---

## Phase 5: User Story 3 — Score Tracking (P1)

Score starts at zero, increments by one per food eaten, persists across ticks.

**Independent Test**: Score starts at 0, becomes 1 after eating food, becomes 7 after eating two more from 5.

### Tests (Red)

- [X] T027 [US3] Write `tests/unit/test_core.py::test_score_starts_at_zero` — verify initial score is 0 (per FR-009: score starts at zero; per data-model.md: value ≥ 0)
- [X] T028 [US3] Write `tests/unit/test_core.py::test_score_increments_by_one` — verify score becomes 1 after eating one food (per FR-008: score increments by one when snake eats food; per data-model.md: increments by exactly 1)
- [X] T029 [US3] Write `tests/unit/test_core.py::test_score_persists_across_ticks` — verify score value persists across non-food ticks (per FR-009: score persists across game ticks)
- [X] T030 [US3] Write `tests/unit/test_core.py::test_score_100_eats` — verify score is exactly 100 after eating 100 food items (per SC-003: score increments by exactly 1 per food eaten, verified across 100 consecutive events)

### Implementation (Green)

- [X] T031 [US3] Implement `src/game/core.py` — integrate score increment into `tick()`: when food is eaten, new score = `old_score + 1`. Constraint: score value is always ≥ 0, increments by exactly 1 (per data-model.md Score validation rules).

---

## Phase 6: Determinism & Integration Tests

Constitution Principle III compliance and end-to-end validation.

- [X] T032 Write `tests/unit/test_core.py::test_deterministic_replay` — verify 10 consecutive runs with same seed + same input sequence produce identical final GameState (per SC-004: identical results across 10 consecutive runs)
- [X] T033 Write `tests/unit/test_core.py::test_game_over_stops_ticks` — verify that `tick()` on an already-over GameState produces an identical GameState (no mutations after game over)
- [X] T034 Write `tests/integration/test_pygame_renderer.py` — verify renderer renders grid boundaries, snake segments, food position, score, and game-over state (per renderer-interface.md contract: render must display all required elements)
- [X] T035 Write `tests/integration/test_pygame_input.py` — verify input adapter converts pygame KEYDOWN events to Direction enum values (per renderer-interface.md contract: poll_events returns Direction or None)

---

## Phase 7: Polish & Renderer

Terminal ASCII renderer for playable-at-every-checkpoint compliance. Pygame renderer for final deliverable.

- [X] T036 Create `src/render/terminal_renderer.py` — `TerminalRenderer.render(state: GameState) -> None`: prints ASCII grid to stdout with snake as `#`, food as `*`, empty cells as `.`, score displayed below grid. Constraint: pure print operation, no side effects on GameState (per renderer-interface.md contract).
- [X] T037 Create `src/render/pygame_renderer.py` — `PygameRenderer.render(state: GameState) -> None`: renders 20×20 grid with colored snake segments, colored food, score HUD, game-over overlay. Constraint: completes within one frame budget (~16ms at 60fps per renderer-interface.md contract).
- [X] T038 Create `src/input/pygame_input.py` — `PygameInput.poll_events() -> Optional[tuple[int, int]]`: polls `pygame.event.get()` for KEYDOWN events, maps Arrow keys to direction tuples. Constraint: returns one direction change per call (no input stacking per spec edge case).
- [X] T039 Create `src/main.py` — entry point wiring: creates GameState from seed, instantiates renderer and input, runs main loop with decoupled tick clock (~10 ticks/sec via `pygame.time.get_ticks()` per research.md decision), accepts `--renderer=terminal` or `--renderer=pygame` (per renderer-interface.md contract).
- [X] T040 Create `tests/unit/test_core.py::test_initial_state_construction` — verify initial GameState with seed, 3-segment snake centered on grid, moving right, with food on a random empty cell and score = 0. This validates the start state for Principle V (playable at checkpoint).

---

## Dependency Graph

```
Phase 1 (Setup)
    └── Phase 2 (Foundational Types)
            └── Phase 3 (US1: Movement)
                    └── Phase 4 (US2: Food)
                            └── Phase 5 (US3: Score)
                                    └── Phase 6 (Determinism)
                                            └── Phase 7 (Polish)
```

**Story Dependencies**:
- US1 → US2 (food spawn needs grid + snake occupied cells from US2 types)
- US1 → US3 (score increment happens in tick() alongside food collision)
- US2 and US3 are independent once foundational types and tick() skeleton exist

**Parallel Opportunities**:
- T002 and T003 (directory creation, __init__.py files) — different files
- T004 (Grid), T005 (Direction) — different files, no dependencies
- T010–T016 (US1 tests) — all different test functions, can be written in parallel
- T020–T024 (US2 tests) — all different test functions, can be written in parallel
- T027–T030 (US3 tests) — all different test functions, can be written in parallel

---

## Implementation Strategy

**MVP Scope**: User Story 1 (Movement) + foundational types. This produces a snake that can be moved on a grid with arrow keys, with reversal prevention and game over on collision — the minimum viable Snake game.

**Delivery Order**:
1. Phase 1–2: Project setup + data types (everything is a frozen dataclass, zero logic)
2. Phase 3: US1 — core movement with `tick()`, collision, game over. **Game is playable at this point with `--renderer=terminal`.**
3. Phase 4: US2 — food spawning and eating integrated into tick()
4. Phase 5: US3 — score tracking integrated into tick()
5. Phase 6–7: Determinism verification, integration tests, Pygame renderer, entry point

**Constitution Compliance**:
- Principle I (Núcleo Puro): All logic in `src/game/` with zero Pygame imports
- Principle II (Test-First): Every implementation task preceded by a test task (Red → Green → Refactor)
- Principle III (Determinism): `rng: random.Random` injected in GameState, used exclusively for food spawn
- Principle IV (Sem Complexidade Prematura): Simple factory pattern for renderer selection, no DI container, no observers
- Principle V (Jogável em Todo Checkpoint): Terminal renderer in Phase 7 enables playable state after Phase 3

---

## Task Summary

| Phase | Description | Task Count |
|-------|-------------|-----------|
| 1 | Setup | 3 |
| 2 | Foundational Types | 6 |
| 3 | US1 — Movement | 10 |
| 4 | US2 — Food | 7 |
| 5 | US3 — Score | 5 |
| 6 | Determinism & Integration | 4 |
| 7 | Polish & Renderer | 5 |
| **Total** | | **40** |

**Test Tasks**: 21 (52.5% of all tasks — Constitution Principle II compliance)
**Implementation Tasks**: 19
