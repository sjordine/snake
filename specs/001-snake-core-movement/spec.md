# Feature Specification: Core Snake Movement, Food Spawning, and Score Tracking

**Feature Branch**: `001-snake-core-movement`

**Created**: 2026-11-12

**Status**: Draft

**Input**: User description: "Build the core Snake movement, food spawning, and score tracking"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Control Snake Movement (Priority: P1)

The player controls a snake on a grid, directing it to move up, down, left, or right using keyboard input. The snake moves one cell per tick and cannot reverse into itself.

**Why this priority**: Movement is the foundational interaction. Without movement, the game does not exist. This is the minimum viable mechanic.

**Independent Test**: A snake can be moved across the grid in all four directions without spawning food or scoring — the player can observe the snake translating across cells as expected.

**Acceptance Scenarios**:

1. **Given** the snake is at the center of the grid, **When** the player presses the up arrow, **Then** the snake's head moves one cell upward.
2. **Given** the snake is moving right, **When** the player presses the down arrow, **Then** the snake reverses into itself and the game transitions to Game Over.
3. **Given** the snake is at the top row, **When** the player presses the up arrow, **Then** the game transitions to Game Over.
4. **Given** the snake occupies cells [(2,2), (2,3), (2,4)], **When** the player presses left, **Then** the head moves to (2,1) and the tail segment at (2,4) is removed.

---

### User Story 2 - Spawn Food on Grid (Priority: P1)

Food appears on an empty cell of the grid. When the snake's head reaches a food cell, the food is consumed. A new food item is then spawned on a different empty cell.

**Why this priority**: Food is the second pillar of the core loop. Without food, there is no goal, no scoring, and no reason to move strategically.

**Independent Test**: Food appears on an empty cell, the snake can eat it by moving to its cell, and a new food item appears elsewhere.

**Acceptance Scenarios**:

1. **Given** the grid is empty, **When** the game starts, **Then** food spawns at a random empty cell.
2. **Given** food is at (5,3), **When** the snake head moves to (5,3), **Then** the food is consumed, the score increases by 1, and new food spawns at a different empty cell.
3. **Given** the snake occupies all but one cell, **When** food spawns, **Then** food appears on the single remaining empty cell.

---

### User Story 3 - Score Tracking (Priority: P1)

The score starts at zero and increases by one each time the snake eats food. The score is tracked internally and available at any point during gameplay.

**Why this priority**: Score is the third pillar of the core loop. It gives the player feedback and a measure of progress.

**Independent Test**: Eating food increments the score by exactly 1; the score persists across moves and food spawns.

**Acceptance Scenarios**:

1. **Given** the game just started, **When** the player queries the score, **Then** it returns 0.
2. **Given** the score is 0, **When** the snake eats food, **Then** the score becomes 1.
3. **Given** the score is 5, **When** the snake eats two more food items, **Then** the score becomes 7.

---

### Edge Cases

- The snake cannot reverse direction into itself (moving right, pressing left must be ignored).
- Food never spawns on a cell occupied by the snake.
- When the grid is nearly full, food still spawns on the remaining empty cell.
- Rapid key presses are handled one per tick — no input stacking.
- On Game Over, the game enters a waiting state and requires a specific input (e.g., press Enter) from the player to restart; it does not auto-restart or exit.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The game MUST display a 20×20 grid on which the snake and food reside.
- **FR-002**: The snake MUST move one cell per tick in the current direction.
- **FR-003**: The player MUST be able to change the snake's direction using keyboard input (up, down, left, right).
- **FR-004**: The snake MUST NOT be able to reverse into itself; invalid direction changes are ignored.
- **FR-005**: The snake MUST grow by one segment when it eats food.
- **FR-006**: Food MUST spawn on a random empty cell of the grid.
- **FR-007**: Food MUST never spawn on a cell occupied by the snake.
- **FR-008**: The score MUST increment by one when the snake eats food.
- **FR-009**: The score MUST start at zero and persist across game ticks.
- **FR-010**: The snake MUST die (Game Over) when its head moves outside the grid boundaries.
- **FR-011**: The game MUST provide a deterministic simulation interface allowing state to be replayed from any seed.

### Key Entities

- **Grid**: A 2D cell map of fixed dimensions. Stores the set of occupied cells.
- **Snake**: A sequence of connected cells (head first). Has a direction and length.
- **Food**: A single cell position on the grid. Represents a consumed object.
- **Score**: A non-negative integer tracking food consumed.
- **GameState**: The aggregate state — grid, snake, food position, score, direction, game-over flag.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The snake responds to direction changes within one tick (no input lag).
- **SC-002**: Food spawns on an empty cell within 100% of cases — no spawning on snake segments.
- **SC-003**: Score increments by exactly 1 per food eaten, verified across 100 consecutive food events.
- **SC-004**: Any game state can be serialized and replayed from the same seed with identical results across 10 consecutive runs.

## Clarifications

### Session 2026-11-12

- Q: What should the grid dimensions be? → A: 20×20 cells

## Assumptions

- The grid size is 20×20 cells — not user-modifiable at runtime.
- The tick rate (speed) is fixed at ~10 ticks per second for the core loop.
- The player uses arrow keys on a physical keyboard.
- The game is single-player only.
- The display medium (terminal, Pygame window) is an adapter concern and does not affect core logic.
