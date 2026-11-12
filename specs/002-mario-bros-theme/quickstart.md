# Quickstart: Mario Bros. Theme Validation Guide

## Overview

This guide provides runnable scenarios to validate the Mario Bros. visual theme feature end-to-end. Each scenario proves a requirement from the feature spec ([spec.md](../002-mario-bros-theme/spec.md)).

## Prerequisites

- Python 3.12+ installed
- Project dependencies installed: `pip install -e ".[dev]"`
- Pygame installed: `pip install pygame`
- Running on a system with a display (for Pygame renderer) or a terminal with 256-color support (for Terminal renderer)

---

## Scenario 1: Run Game with Default Theme (Smoke Test)

**Proves**: Game runs before theme changes, existing behavior preserved.

**Steps**:
```bash
cd /Users/sergioordine/Development/SDD/third_day/snake
python -m src.main --renderer=pygame
```

**Expected**:
- Pygame window opens at 500×500 pixels
- Background is dark gray (not blue)
- Snake is green with a lighter green head
- Food is red
- Score HUD text is light gray
- Snake moves when arrow keys or WASD are pressed

**Terminal variant**:
```bash
python -m src.main --renderer=terminal
```
**Expected**: Same visual elements with ANSI colors in terminal.

---

## Scenario 2: Toggle to Mario Theme During Gameplay

**Proves**: FR-005 (user-accessible toggle), FR-001 (background changes to sky blue), User Story 1 acceptance.

**Steps**:
1. Start game as in Scenario 1
2. Press `T` key while playing

**Expected**:
- **Background** changes to sky blue `(42, 42, 224)`
- **Snake body** changes to overall blue `(0, 94, 195)` with blue inner highlight
- **Snake head** changes to Mario red `(235, 33, 33)` with skin-tone eyes
- **Food** changes to gold coin `(255, 215, 0)` with white highlight line
- **HUD text** changes to white `(255, 255, 255)`
- **Grid lines** change to brick brown `(184, 109, 27)`
- Game continues playing normally — no crash, no freeze, no state corruption

**Terminal variant**:
```bash
python -m src.main --renderer=terminal
# Press T during play
```
**Expected**: Colors shift to Mario palette via 256-color ANSI codes. Snake head turns red (Mario red), food turns yellow (gold), background turns blue.

---

## Scenario 3: Toggle Back to Default Theme

**Proves**: Theme toggle is reversible (bidirectional), no permanent state change.

**Steps**:
1. Start game
2. Press `T` to activate Mario theme
3. Press `T` again

**Expected**:
- All elements return to their original default colors
- Game continues playing normally
- Colors are identical to the pre-Mario state

---

## Scenario 4: Mario Snake Head Has Face Detail

**Proves**: FR-002 (snake head incorporates a Mario character element), User Story 2 acceptance scenario 2.

**Steps**:
1. Start game with Mario theme (press `T` before or after launch)
2. Observe snake head during gameplay

**Expected**:
- Snake head is Mario red `(235, 33, 33)`
- Two small square pixels of skin tone `(255, 180, 120)` are visible on the head
- Eyes are positioned symmetrically near the top of the head
- Each eye is approximately `cell_size // 5` pixels wide (2–5 pixels at standard 25px cell size)

---

## Scenario 5: Food Renders as Coin

**Proves**: FR-003 (food renders as coin, mushroom, or power-up), User Story 3 acceptance.

**Steps**:
1. Start game with Mario theme (press `T`)
2. Observe food item

**Expected**:
- Food renders as a gold ellipse `(255, 215, 0)` filling the cell
- A white highlight line `(255, 255, 255)` crosses the center horizontally
- Food changes position when eaten (game core behavior unchanged)

---

## Scenario 6: Game Over Screen Uses Mario Theme

**Proves**: FR-001 (game-over screen uses Mario colors), User Story 1 acceptance scenario 3.

**Steps**:
1. Start game with Mario theme
2. Crash the snake into a wall or itself to trigger game over

**Expected**:
- Black semi-transparent overlay `(0, 0, 0, 180)` appears
- "GAME OVER" text appears in Mario red `(235, 33, 33)`
- Score display uses HUD white text
- Pressing `R` restarts the game

---

## Scenario 7: Core Gameplay Unchanged (Determinism)

**Proves**: Principle III (Simulação Determinística), Principle V (Jogável em Todo Checkpoint).

**Steps**:
1. Start game with default theme, inject seed: `python -m src.main --seed=42 --renderer=pygame`
2. Play until food eaten, note score
3. Restart with same seed: `python -m src.main --seed=42 --renderer=pygame`
4. Press `T` to activate Mario theme immediately
5. Play the same sequence of moves
6. Compare final scores

**Expected**:
- Both runs produce identical scores and snake positions at every tick
- Mario theme does not alter deterministic RNG or game tick behavior
- The only difference is visual — pixel colors

**Terminal variant** (headless validation):
```bash
# Verify core is untouched — run existing unit tests
python -m pytest tests/unit/test_core.py tests/unit/test_snake.py tests/unit/test_food.py -v
```
**Expected**: All existing tests pass — no regression in game logic.

---

## Scenario 8: Theme Toggle Does Not Conflict with Other Keys

**Proves**: Integration safety — `T` key doesn't interfere with existing bindings.

**Steps**:
1. Start game with Mario theme
2. Press: `T`, `W`/`↑`, `T`, `S`/`↓`, `T`, `R`, `T`

**Expected**:
- `T` toggles theme only (does not move snake)
- `W`/`↑` turns up, `S`/`↓` turns down (direction unchanged)
- `R` restarts game (restart functional)
- Theme state persists across restart only if implementation stores it in renderer

---

## Automation: Run All Tests

```bash
# Unit tests for theme config and palette
python -m pytest tests/unit/test_theme_config.py tests/unit/test_palette.py -v

# Integration tests for renderer theme application
python -m pytest tests/integration/test_pygame_renderer.py -v -k theme

# Full regression suite — ensure nothing broke
python -m pytest -v
```

**Expected**: All tests pass, including newly added theme tests and all pre-existing tests.
