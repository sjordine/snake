# Quickstart Validation Guide: Core Snake Movement

**Feature**: 001-snake-core-movement  
**Date**: 2026-11-12  
**Purpose**: Runnable validation scenarios to prove the feature works end-to-end.

---

## Prerequisites

- Python 3.12+ installed
- Virtual environment activated: `source .venv/bin/activate`
- Dependencies installed: `pip install pygame pytest`

---

## Scenario 1: Core Movement (Terminal Quickstart)

**Goal**: Verify snake moves one cell per tick in response to direction changes.

**Setup**:
```bash
cd snake/
python -m src.main --renderer=terminal
```

**Steps**:
1. Game starts with snake at center, 3 segments, moving right.
2. Press `↑` — observe snake head moves up by one cell on next tick.
3. Press `→` (while moving up) — observe snake continues (right is valid, not a reversal into itself).
4. Press `←` (while moving right) — observe direction is ignored (cannot reverse).
5. Press `↓` — observe snake moves down one cell.

**Expected outcome**: Snake moves exactly one cell per tick. Invalid reversals are ignored. Movement is visible in terminal output.

**Validation**: Core `src/game/core.py` can be tested headlessly:
```bash
pytest tests/unit/test_core.py -v
```

---

## Scenario 2: Food Spawning and Eating

**Goal**: Verify food spawns on empty cells, eating food increments score and spawns new food.

**Setup**:
```bash
pytest tests/unit/test_food.py -v
pytest tests/unit/test_core.py::test_tick_eats_food -v
```

**Steps** (automated test):
1. Create GameState with seed=42.
2. Verify food spawns on an empty cell (not on snake segments).
3. Move snake to food position.
4. Verify score incremented from 0 to 1.
5. Verify new food spawned at a different empty cell.
6. Eat food 100 times — verify score is exactly 100.

**Expected outcome**: Food never spawns on snake. Score increments by exactly 1 per food eaten (see SC-003 in spec).

---

## Scenario 3: Collision and Game Over

**Goal**: Verify snake dies on wall collision and on self-collision.

**Setup**:
```bash
pytest tests/unit/test_collision.py -v
pytest tests/unit/test_core.py::test_tick_wall_collision -v
pytest tests/unit/test_core.py::test_tick_self_collision -v
```

**Steps** (automated test):
1. Move snake to right edge, continue moving right → wall collision → `game_over = True`.
2. Create a long snake that loops back on itself → self collision → `game_over = True`.
3. After `game_over = True`, subsequent `tick()` calls should not change state.

**Expected outcome**: Game transitions to game over state immediately. No further ticks produce state changes.

---

## Scenario 4: Deterministic Replay

**Goal**: Verify same seed + same inputs produce identical state across runs (SC-004).

**Setup**:
```bash
pytest tests/unit/test_core.py::test_deterministic_replay -v
```

**Steps** (automated test):
1. Create GameState with seed=123.
2. Apply a fixed sequence of 50 direction changes.
3. Run twice.
4. Compare final GameState — must be identical.

**Expected outcome**: 10 consecutive runs with same seed + inputs produce identical final state.

---

## Scenario 5: Full Pygame Run

**Goal**: Verify the game is playable in a Pygame window.

**Setup**:
```bash
python -m src.main --renderer=pygame
```

**Steps**:
1. Pygame window opens with 20×20 grid rendered.
2. Snake visible as colored segments, food as distinct colored cell.
3. Score displayed on screen.
4. Arrow key controls work: snake moves, turns, eats food, grows.
5. Wall collision shows game-over state.

**Expected outcome**: Game is playable from start to game over with Pygame rendering (fulfills Principle V).

---

## Validation Summary

| Scenario | Requirement | Method |
|----------|-------------|--------|
| Movement | FR-002, FR-003, FR-004 | Terminal + unit test |
| Food spawn | FR-005, FR-006, FR-007 | Unit test |
| Score | FR-008, FR-009 | Unit test |
| Collision | FR-010 | Unit test |
| Determinism | FR-011, SC-004 | Unit test |
| Pygame render | Playable at checkpoint | Manual test |
