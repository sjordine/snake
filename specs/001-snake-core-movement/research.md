# Research: Core Snake Movement

**Feature**: 001-snake-core-movement  
**Date**: 2026-11-12  
**Status**: Complete — all unknowns resolved

---

## Decision: Pure-core / thin-shell architecture (src/game/ + src/render/ + src/input/)

**Rationale**: The constitution (Principle I) mandates that all game rules live in an independent, testable module. Pygame is a display/input concern, not a game logic concern. Separating by responsibility (game rules vs. display vs. input) keeps the core importable without any GUI dependency, enabling pure unit tests.

**Alternatives considered**:
- All-in-one monolithic module — rejected: couples logic to Pygame, prevents headless testing.
- OOP classes for everything — rejected under Principle IV (YAGNI): functional data classes are simpler for this scope.

---

## Decision: Functional data classes (dataclass/frozen) for core entities

**Rationale**: Snake, Grid, Food, and GameState are immutable data shapes that transform deterministically. `@dataclass(frozen=True)` or equivalent record types provide value equality, explicit fields, and no hidden state mutations. Direction changes produce a new GameState rather than mutating the old one — this is both simpler to test and naturally compatible with deterministic replay.

**Alternatives considered**:
- Mutable class with methods — rejected: harder to reason about, harder to test determinism.
- Named tuples — rejected: less expressive, no method extension without subclassing.

---

## Decision: Injected `random.Random(seed)` for deterministic food spawn

**Rationale**: The constitution (Principle III) requires that all randomness flow through an injected RNG instance. This makes every game state replayable given the same seed + input sequence. Using `random.Random(seed)` directly (instead of global `random.seed()`) avoids thread-safety issues and side effects.

**Alternatives considered**:
- Global `random.seed()` — rejected: violates constitution, hard to isolate in tests.
- Custom PRNG — rejected under Principle IV: over-engineering for a single RNG use.

---

## Decision: Pygame event loop with decoupled tick clock

**Rationale**: Pygame's event handling (keyboard input) runs at the OS event rate, but game logic (snake movement) runs at a fixed tick rate (~10 ticks/sec). Decoupling these — Pygame polls events and queues direction commands, while a separate timer fires game ticks — ensures consistent gameplay speed regardless of frame rate. Pygame's `pygame.time.get_ticks()` or `pygame.time.set_timer()` can provide the tick clock.

**Alternatives considered**:
- Tight coupling: one Pygame event = one game tick — rejected: input rate varies, gameplay becomes unpredictable.
- Separate threading — rejected under Principle IV: adds complexity (race conditions, locks) for no real benefit.

---

## Decision: Snake as ordered list of (x, y) tuples (head first)

**Rationale**: The snake is a sequence of grid coordinates. An ordered list (Python `tuple` of `tuple`s) gives:
- O(1) head access (for movement/collision)
- O(1) tail removal via slicing (`snake[:-1]`)
- O(1) new head prepending (`(new_head, *snake)`)
- Immutable data shape (frozen) for pure function composition

**Alternatives considered**:
- `collections.deque` — rejected: mutable, not needed for O(1) append/remove.
- Single integer encoding (x * width + y) — rejected: less readable, no performance gain at 20×20.

---

## Decision: Terminal ASCII quickstart, Pygame render as adapter

**Rationale**: Constitution Principle V requires the game to be playable at every checkpoint. A terminal ASCII renderer (prints grid state with `print()`) is the simplest runnable surface. Pygame rendering is then a drop-in replacement adapter, swapping in when ready. Both renderers accept the same GameState and produce output.

**Alternatives considered**:
- Pygame from day one — rejected: introduces GUI dependency before core is solid, slows iteration.
- Web render (e.g., Flask + HTML canvas) — rejected: adds server stack for no benefit.
