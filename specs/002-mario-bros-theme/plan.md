# Implementation Plan: Mario Bros. Visual Theme

**Branch**: `002-mario-bros-theme` | **Date**: 2026-11-12 | **Spec**: [spec.md](../002-mario-bros-theme/spec.md)

**Input**: Feature specification from `/specs/002-mario-bros-theme/spec.md`

## Summary

Add a Mario Bros. visual theme to the Snake game that transforms all renderable elements — background, snake body, snake head, food, HUD, and game-over screen — to match the iconic aesthetic of the original 1985 Super Mario Bros. NES game. The theme applies only to the rendering layer (both Pygame and terminal renderers), leaving the pure game core (`game.core`) completely untouched per the project's "Núcleo Puro, Casca Fina" principle. A user-accessible toggle allows switching between the default theme and the Mario theme without restarting the game.

## Technical Context

**Language/Version**: Python 3.12 (per `pyproject.toml` `requires-python = ">=3.12"`)

**Primary Dependencies**: Pygame (for PygameRenderer), Python standard library only (for TerminalRenderer)

**Storage**: N/A — no persistent storage; all state is in-memory

**Testing**: pytest (per `pyproject.toml`, test paths `tests/`, Python path `src/`)

**Target Platform**: Desktop macOS (development), general POSIX desktop (terminal); Windows-compatible Pygame window

**Project Type**: Desktop game application (Snake clone with pure-core + thin-renderer architecture)

**Performance Goals**: 
- Pygame renderer completes one frame in ≤16ms at 60fps (existing constraint from `pygame_renderer.py`)
- Terminal renderer frame update is instantaneous (single flush operation)
- Theme toggle responds within 1 frame of toggle action

**Constraints**: 
- Game core (`game.core`) MUST remain 100% unchanged — no theme awareness in game logic
- All theme logic MUST live in the render layer only (adapters per constitution Principle I)
- No external assets (images, fonts, audio) — all visuals created programmatically via pygame primitives or ANSI escape codes
- Theme toggle must work during gameplay without state corruption
- Deterministic simulation (injected RNG) must not be affected by theme changes

**Scale/Scope**: Single-player desktop game; one theme variant (Mario Bros.) plus the existing default theme

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Check | Status |
|-----------|-------|--------|
| **I. Núcleo Puro, Casca Fina** — Theme logic lives entirely in render adapters; `game.core` is unchanged | PASS | Theme colors and visuals are configured only in `render/` modules. Game core receives no new parameters. |
| **II. Test-First** — Tests for theme rendering written before implementation | PASS | Tests will be added for theme color configuration and renderer theme application. |
| **III. Simulação Determinística** — Theme does not affect RNG, game state, or tick behavior | PASS | Theme is purely visual; RNG injection and game tick are unaffected. |
| **IV. Sem Complexidade Prematura** — No unnecessary abstractions; theme uses simple configuration | PASS | Theme is implemented as a color palette + style config dictionary, not an abstract strategy pattern or observer system. Single `ThemeConfig` dataclass. |
| **V. Jogável em Todo Checkpoint** — Game remains fully playable with theme active | PASS | Core gameplay unchanged; theme is cosmetic. Game loops identically with or without theme. |

**Verdict**: All gates pass. No complexity justification needed.

## Project Structure

### Documentation (this feature)

```text
specs/002-mario-bros-theme/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   └── theme-api.md     # Theme configuration and renderer contract
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── game/
│   ├── core.py          # ← UNCHANGED: No theme awareness
│   ├── snake.py
│   ├── food.py
│   ├── collision.py
│   ├── grid.py
│   └── __init__.py
├── render/
│   ├── __init__.py
│   ├── terminal_renderer.py  # ← MODIFY: Accept theme parameter, use theme colors
│   ├── pygame_renderer.py    # ← MODIFY: Accept theme parameter, use theme colors
│   └── themes/
│       ├── __init__.py       # ← NEW
│       ├── palette.py        # ← NEW: Color palettes for default and Mario themes
│       └── config.py         # ← NEW: Theme configuration dataclass
├── input/
│   ├── pygame_input.py
│   ├── terminal_input.py
│   └── __init__.py
├── audio/
│   ├── music.py
│   └── __init__.py
└── main.py            # ← MODIFY: Wire theme toggle, pass theme to renderers

tests/
├── unit/
│   ├── test_core.py
│   ├── test_snake.py
│   ├── test_food.py
│   ├── test_collision.py
│   ├── test_grid.py
│   ├── test_tick.py
│   ├── test_music.py
│   ├── test_palette.py         # ← NEW: Unit tests for palette colors
│   └── test_theme_config.py    # ← NEW: Unit tests for theme config
├── integration/
│   ├── test_pygame_renderer.py   # ← MODIFY: Add theme rendering tests
│   └── test_pygame_input.py
```

**Structure Decision**: The existing structure follows the pure-core/thin-renderer pattern. The theme feature adds a `render/themes/` subpackage with `palette.py` (color constants organized by theme) and `config.py` (theme configuration dataclass). Both existing renderers accept a `theme` parameter and select colors from the palette. The game core remains untouched. No new abstraction patterns (strategy, observer) are introduced — only a simple configuration dataclass.

## Complexity Tracking

> Not applicable — all Constitution Check gates pass with no violations.
