# Implementation Plan: Core Snake Movement, Food Spawning, and Score Tracking

**Branch**: `001-snake-core-movement` | **Date**: 2026-11-12 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-snake-core-movement/spec.md`

## Summary

Build the core Snake game: movement on a 20×20 grid, food spawning, and score tracking. The architecture follows a pure core / thin shell pattern — all game rules live in an independent, testable module with no rendering or I/O dependencies. Pygame handles only the display and input adapters.

On Game Over, the game enters a waiting state and requires the Enter key to restart — no auto-restart, no exit. Snake starts at 3 segments, centered on the grid, moving right. Speed is constant at ~10 ticks/sec throughout gameplay. Input is restricted to arrow keys only.

## Technical Context

**Language/Version**: Python 3.12

**Primary Dependencies**: Pygame (rendering + input adapter), pytest (testing)

**Storage**: N/A — no persistent storage; state is in-memory and replayable via seed.

**Testing**: pytest — pure unit tests for core logic (no Pygame), minimal integration tests for render/input adapters.

**Target Platform**: Desktop (macOS, Linux, Windows) — single-player with keyboard input.

**Project Type**: Desktop game (Pygame application with pure-core architecture)

**Performance Goals**: ~10 game ticks/second for simulation loop; render loop runs independently at display refresh rate (target ≥60 fps).

**Constraints**: Pure core must have zero dependencies on Pygame, OS, or display APIs. Deterministic RNG via injected `random.Random(seed)` — no global `random.seed()`, no `time.time()`, no `os.urandom()` in core logic in core logic. Arrow keys only for input. Constant tick rate (~10 ticks/sec) throughout gameplay.

**Scale/Scope**: 20×20 grid (400 cells), single snake (3–400 segments), single food item, single player.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Compliance | Notes |
|-----------|-----------|-------|
| I. Núcleo Puro, Casca Fina | ✅ Pass | Core logic (`src/game/`) isolated from Pygame. Render and input are thin adapters. |
| II. Test-First | ✅ Pass | Plan tasks begin with red tests. Nothing committed until tests pass. |
| III. Simulação Determinística | ✅ Pass | RNG injected via `random.Random(seed)` in GameState constructor. |
| IV. Sem Complexidade Prematura | ✅ Pass | Single game type, no abstractions beyond what spec requires. |
| V. Jogável em Todo Checkpoint | ✅ Pass | Each phase produces a runnable state (terminal ASCII initially, then Pygame). |

**Gate Result**: PASS — all principles satisfied.

## Project Structure

### Documentation (this feature)

```text
specs/001-snake-core-movement/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
snake/
├── src/
│   ├── game/
│   │   ├── __init__.py
│   │   ├── core.py              # GameState, tick(), direction_change(), move()
│   │   ├── grid.py              # Grid dimensions, cell validation
│   │   ├── snake.py             # Snake segments, direction, grow, collision
│   │   ├── food.py              # Food spawn logic with RNG
│   │   └── collision.py         # Wall/self collision detection
│   ├── render/
│   │   ├── __init__.py
│   │   └── pygame_renderer.py   # Pygame-specific display adapter
│   ├── input/
│   │   ├── __init__.py
│   │   └── pygame_input.py      # Pygame event → direction command adapter
│   └── main.py                  # Entry point: wires core + render + input
├── tests/
│   ├── unit/
│   │   ├── test_grid.py
│   │   ├── test_snake.py
│   │   ├── test_food.py
│   │   ├── test_collision.py
│   │   └── test_core.py
│   └── integration/
│       ├── test_pygame_renderer.py
│       └── test_pygame_input.py
└── pyproject.toml               # Project config, dependencies, pytest config
```

**Structure Decision**: Pure-core / thin-shell architecture. The `src/game/` package contains all game rules and is importable without Pygame installed. `src/render/` and `src/input/` are thin Pygame adapters. `src/main.py` wires them together at runtime. Tests follow the same split: unit tests for core (no Pygame), integration tests for adapters (Pygame event mock).

## Clarifications Integrated

- Game Over: Enter key to restart (no auto-restart, no exit)
- Growth: Classic tail-delay pattern (tail stays for one tick after eating)
- Input: Arrow keys only (no WASD, no configurable keybinds)
- Speed: Constant 10 ticks/sec throughout gameplay
- Initial state: 3 segments, centered on grid, moving right

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations — all tasks follow constitution principles.
