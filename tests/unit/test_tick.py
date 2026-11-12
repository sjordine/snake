"""Tests for tick() — movement, food eating, scoring, game over, determinism."""

import random

import pytest

from src.game.core import tick, GameState, Score
from src.game.grid import Grid
from src.game.snake import RIGHT, UP, LEFT, DOWN, Snake
from src.game.food import Food


class TestInitialState:
    """T040 — Initial GameState construction."""

    def test_initial_state_construction(self) -> None:
        """Verify initial GameState with seed, 3-segment snake centered, moving right, food on empty cell, score=0."""
        state = GameState.initial(seed=42)

        # 3 segments, centered on 20x20 grid
        assert state.snake_length == 3
        assert state.snake_direction == (1, 0)  # RIGHT

        # Head at center
        assert state.head == (10, 10)

        # Score starts at 0
        assert state.score == 0
        assert state.game_over is False

        # Food position is on an empty cell (not on snake)
        occupied = frozenset(state.snake_segments)
        assert state.food_position not in occupied

        # Food position is within grid
        gx, gy = state.food_position
        assert 0 <= gx < 20 and 0 <= gy < 20

        # Snake segments: head(10,10), body(9,10), body(8,10)
        assert state.snake_segments == ((10, 10), (9, 10), (8, 10))

    def test_initial_state_custom_seed(self) -> None:
        """Different seeds produce different food positions."""
        state1 = GameState.initial(seed=42)
        state2 = GameState.initial(seed=99)
        assert state1.food_position != state2.food_position

    def test_initial_state_custom_length(self) -> None:
        """Custom start length creates snake with that many segments."""
        state = GameState.initial(seed=42, start_length=5)
        assert state.snake_length == 5
        assert state.head == (10, 10)


class TestTickMovement:
    """T011 — Snake moves one cell per tick."""

    def test_tick_moves_snake_one_cell(self) -> None:
        """Snake head advances by one cell per tick in current direction (per FR-002)."""
        state = GameState.initial(seed=42)
        initial_head = state.head  # (10, 10)
        new_state = tick(state, RIGHT)

        assert new_state.head == (11, 10)
        assert new_state.snake_length == 3  # same length (no food eaten)

    def test_tick_moves_up(self) -> None:
        new_state = tick(GameState.initial(seed=42), UP)
        assert new_state.head == (10, 9)

    def test_tick_moves_down(self) -> None:
        new_state = tick(GameState.initial(seed=42), DOWN)
        assert new_state.head == (10, 11)

    def test_tick_moves_left(self) -> None:
        # LEFT while moving RIGHT is a reversal — ignored
        # Snake must keep moving RIGHT (per FR-004)
        new_state = tick(GameState.initial(seed=42), LEFT)
        assert new_state.head == (11, 10)
        assert new_state.snake_direction == (1, 0)  # still RIGHT


class TestTickDirectionChange:
    """T012 — Direction change takes effect on next tick."""

    def test_tick_direction_change(self) -> None:
        """Direction change takes effect on the NEXT tick (per FR-003)."""
        state = GameState.initial(seed=42)  # moving RIGHT

        # Change direction to UP
        new_state = tick(state, UP)
        assert new_state.snake_direction == (0, -1)  # UP applied
        assert new_state.head == (10, 9)  # moved up one cell

    def test_multiple_direction_changes(self) -> None:
        """Multiple direction changes applied sequentially."""
        state = GameState.initial(seed=42)

        # Move right once
        s1 = tick(state, RIGHT)
        assert s1.head == (11, 10)

        # Turn down
        s2 = tick(s1, DOWN)
        assert s2.head == (11, 11)
        assert s2.snake_direction == (0, 1)

        # Turn left
        s3 = tick(s2, LEFT)
        assert s3.head == (10, 11)
        assert s3.snake_direction == (-1, 0)


class TestTickReversalIgnored:
    """T013 — Invalid reversals are ignored (per FR-004)."""

    def test_tick_reversal_ignored(self) -> None:
        """Pressing left while moving right does NOT change direction (per FR-004)."""
        state = GameState.initial(seed=42)  # moving RIGHT
        new_state = tick(state, LEFT)

        # Direction unchanged
        assert new_state.snake_direction == (1, 0)  # still RIGHT
        # Head advances right
        assert new_state.head == (11, 10)

    def test_no_reversal_up_down(self) -> None:
        """Reversing UP→DOWN is also rejected."""
        state = GameState.initial(seed=42)
        s1 = tick(state, UP)
        assert s1.snake_direction == (0, -1)

        # Try to reverse to DOWN
        s2 = tick(s1, DOWN)
        assert s2.snake_direction == (0, -1)  # still UP
        assert s2.head == (10, 8)  # moved up again

    def test_valid_turn_not_reversal(self) -> None:
        """Turning 90 degrees is valid (not a reversal)."""
        state = GameState.initial(seed=42)  # RIGHT
        s1 = tick(state, UP)
        assert s1.snake_direction == (0, -1)  # turned to UP

        # Turn from UP to RIGHT (90° turn, valid)
        s2 = tick(s1, RIGHT)
        assert s2.snake_direction == (1, 0)  # turned to RIGHT


class TestTickWallCollision:
    """T014 — Game over on wall collision (per FR-010)."""

    def test_tick_wall_collision(self) -> None:
        """game_over = True when head moves outside grid boundaries (per FR-010)."""
        # Create a state with snake at the right edge
        grid = Grid(width=20, height=20)
        rng = random.Random(42)
        state = GameState(
            grid=grid,
            snake_segments=((19, 10), (18, 10), (17, 10)),
            snake_direction=(1, 0),  # RIGHT
            food_position=(5, 5),
            score=0,
            game_over=False,
            rng=rng,
        )

        new_state = tick(state, RIGHT)
        assert new_state.game_over is True
        # No state changes on wall collision
        assert new_state.snake_segments == state.snake_segments
        assert new_state.score == state.score

    def test_wall_collision_left_edge(self) -> None:
        grid = Grid(width=20, height=20)
        rng = random.Random(42)
        state = GameState(
            grid=grid,
            snake_segments=((0, 10), (1, 10), (2, 10)),
            snake_direction=(-1, 0),  # LEFT
            food_position=(5, 5),
            score=0,
            game_over=False,
            rng=rng,
        )
        new_state = tick(state, LEFT)
        assert new_state.game_over is True

    def test_wall_collision_top_edge(self) -> None:
        grid = Grid(width=20, height=20)
        rng = random.Random(42)
        state = GameState(
            grid=grid,
            snake_segments=((10, 0), (10, 1), (10, 2)),
            snake_direction=(0, -1),  # UP
            food_position=(5, 5),
            score=0,
            game_over=False,
            rng=rng,
        )
        new_state = tick(state, UP)
        assert new_state.game_over is True

    def test_wall_collision_bottom_edge(self) -> None:
        grid = Grid(width=20, height=20)
        rng = random.Random(42)
        state = GameState(
            grid=grid,
            snake_segments=((10, 19), (10, 18), (10, 17)),
            snake_direction=(0, 1),  # DOWN
            food_position=(5, 5),
            score=0,
            game_over=False,
            rng=rng,
        )
        new_state = tick(state, DOWN)
        assert new_state.game_over is True


class TestTickSelfCollision:
    """T015 — Game over on self collision."""

    def test_tick_self_collision(self) -> None:
        """game_over = True when head moves into body segment."""
        # Snake forms a U-shape: head(5,5)→(5,6)→(5,7)→(4,7)→(4,6)
        # If head turns and goes down to (5,6) — that's body
        grid = Grid(width=20, height=20)
        rng = random.Random(42)
        segments = ((5, 5), (5, 6), (5, 7), (4, 7), (4, 6))
        state = GameState(
            grid=grid,
            snake_segments=segments,
            snake_direction=(0, 1),  # DOWN
            food_position=(0, 0),
            score=0,
            game_over=False,
            rng=rng,
        )
        new_state = tick(state, DOWN)
        assert new_state.game_over is True

    def test_no_self_collision_safe_move(self) -> None:
        """No self collision when moving into clear space."""
        grid = Grid(width=20, height=20)
        rng = random.Random(42)
        state = GameState(
            grid=grid,
            snake_segments=((10, 10), (10, 11), (10, 12)),
            snake_direction=(1, 0),  # RIGHT
            food_position=(0, 0),
            score=0,
            game_over=False,
            rng=rng,
        )
        new_state = tick(state, RIGHT)
        assert new_state.game_over is False
        assert new_state.head == (11, 10)


class TestTailRemovedOnMove:
    """T016 — Tail segment removed when not growing."""

    def test_tick_tail_removed_on_move(self) -> None:
        """Tail is removed when snake moves without eating (per spec acceptance scenario 4)."""
        state = GameState.initial(seed=42)
        initial_segments = state.snake_segments
        assert len(initial_segments) == 3  # head, body, tail

        new_state = tick(state, RIGHT)
        assert len(new_state.snake_segments) == 3  # same length

        # New head at right
        assert new_state.head == (11, 10)
        # Tail (8, 10) should be gone
        assert (8, 10) not in new_state.snake_segments
        # Body shifted: (9,10)→(10,10), (10,10)→head
        assert new_state.snake_segments == ((11, 10), (10, 10), (9, 10))


class TestFoodEating:
    """T023, T024 — Food eating and respawning in tick()."""

    def test_tick_eats_food(self) -> None:
        """Food is consumed when head reaches food position; snake grows by one segment (per FR-005)."""
        grid = Grid(width=20, height=20)
        rng = random.Random(42)
        # Place snake head right next to food
        state = GameState(
            grid=grid,
            snake_segments=((5, 5), (4, 5), (3, 5)),
            snake_direction=(1, 0),  # RIGHT
            food_position=(6, 5),  # one cell ahead
            score=0,
            game_over=False,
            rng=rng,
        )

        new_state = tick(state, RIGHT)
        assert new_state.snake_length == 4  # grew by 1
        assert new_state.head == (6, 5)  # ate food
        assert new_state.score == 1  # score incremented

    def test_tick_new_food_after_eat(self) -> None:
        """New food spawns at a different empty cell after old food is consumed."""
        grid = Grid(width=20, height=20)
        rng = random.Random(42)
        state = GameState(
            grid=grid,
            snake_segments=((5, 5), (4, 5), (3, 5)),
            snake_direction=(1, 0),  # RIGHT
            food_position=(6, 5),
            score=0,
            game_over=False,
            rng=rng,
        )

        new_state = tick(state, RIGHT)
        # Old food gone
        assert new_state.food_position != (6, 5)
        # New food is on an empty cell (not on snake)
        assert new_state.food_position not in frozenset(new_state.snake_segments)
        # New food is within grid
        x, y = new_state.food_position
        assert 0 <= x < 20 and 0 <= y < 20

    def test_no_food_eat_when_no_collision(self) -> None:
        """Snake does not grow when not eating food."""
        state = GameState.initial(seed=42)
        initial_length = state.snake_length

        new_state = tick(state, RIGHT)
        assert new_state.snake_length == initial_length  # same
        assert new_state.score == 0  # no score change


class TestScoreTracking:
    """T027-T030 — Score starts at zero, increments, persists."""

    def test_score_starts_at_zero(self) -> None:
        """Initial score is 0 (per FR-009)."""
        state = GameState.initial(seed=42)
        assert state.score == 0

    def test_score_increments_by_one(self) -> None:
        """Score becomes 1 after eating one food (per FR-008)."""
        grid = Grid(width=20, height=20)
        rng = random.Random(42)
        state = GameState(
            grid=grid,
            snake_segments=((5, 5), (4, 5), (3, 5)),
            snake_direction=(1, 0),
            food_position=(6, 5),
            score=0,
            game_over=False,
            rng=rng,
        )
        new_state = tick(state, RIGHT)
        assert new_state.score == 1

    def test_score_persists_across_ticks(self) -> None:
        """Score persists across non-food ticks (per FR-009)."""
        grid = Grid(width=20, height=20)
        rng = random.Random(42)
        state = GameState(
            grid=grid,
            snake_segments=((5, 5), (4, 5), (3, 5)),
            snake_direction=(1, 0),
            food_position=(6, 5),
            score=0,
            game_over=False,
            rng=rng,
        )
        # Eat food
        s1 = tick(state, RIGHT)
        assert s1.score == 1

        # Move without eating
        s2 = tick(s1, RIGHT)
        assert s2.score == 1  # persists

        s3 = tick(s2, RIGHT)
        assert s3.score == 1  # still persists

    def test_score_100_eats(self) -> None:
        """Score is exactly 100 after eating 100 food items (per SC-003)."""
        # We simulate 100 food-eating ticks in a row, always chasing food
        # placed adjacent to the head in a valid empty cell.
        grid = Grid(width=20, height=20)
        rng = random.Random(123)
        state = GameState(
            grid=grid,
            snake_segments=((5, 5), (4, 5), (3, 5)),
            snake_direction=(1, 0),
            food_position=(6, 5),
            score=0,
            game_over=False,
            rng=rng,
        )

        for i in range(100):
            # Pick a direction that has an empty cell adjacent to the head
            hx, hy = state.head
            occupied = frozenset(state.snake_segments)
            for new_dir, dx, dy in [
                ((1, 0), 1, 0), ((0, 1), 0, 1), ((-1, 0), -1, 0), ((0, -1), 0, -1)
            ]:
                food = (hx + dx, hy + dy)
                if food not in occupied and (0 <= food[0] < 20 and 0 <= food[1] < 20):
                    break

            state = GameState(
                grid=grid,
                snake_segments=state.snake_segments,
                snake_direction=state.snake_direction,
                food_position=food,
                score=state.score,
                game_over=False,
                rng=state.rng,
            )
            state = tick(state, new_dir)
            assert state.game_over is False
            assert state.score == i + 1

        assert state.score == 100


class TestDeterministicReplay:
    """T032 — Same seed + same inputs produce identical results."""

    def test_deterministic_replay(self) -> None:
        """10 consecutive runs with same seed + same input sequence produce identical final GameState."""
        directions = [RIGHT, UP, RIGHT, RIGHT, DOWN, LEFT, UP, RIGHT, DOWN, DOWN]

        results = []
        for _ in range(10):
            state = GameState.initial(seed=42)
            for d in directions:
                state = tick(state, d)
            results.append(state)

        # All results must be identical
        for i in range(1, len(results)):
            assert results[i].head == results[0].head
            assert results[i].snake_segments == results[0].snake_segments
            assert results[i].food_position == results[0].food_position
            assert results[i].score == results[0].score
            assert results[i].game_over == results[0].game_over
            assert results[i].snake_length == results[0].snake_length


class TestGameOverStopsTicks:
    """T033 — Game over GameState produces identical state on further ticks."""

    def test_game_over_stops_ticks(self) -> None:
        """tick() on an already-over GameState produces an identical GameState."""
        # Force game over by moving into wall
        grid = Grid(width=20, height=20)
        rng = random.Random(42)
        state = GameState(
            grid=grid,
            snake_segments=((19, 10), (18, 10), (17, 10)),
            snake_direction=(1, 0),  # RIGHT
            food_position=(5, 5),
            score=0,
            game_over=False,
            rng=rng,
        )

        # First tick → game over
        over_state = tick(state, RIGHT)
        assert over_state.game_over is True

        # Subsequent ticks produce identical state
        for _ in range(5):
            over_state = tick(over_state, RIGHT)

        # Head, segments, score, food all unchanged
        assert over_state.game_over is True
        assert over_state.snake_segments == state.snake_segments
        assert over_state.score == state.score
        assert over_state.food_position == state.food_position

    def test_game_over_preserves_direction(self) -> None:
        """Direction is unchanged when game over."""
        grid = Grid(width=20, height=20)
        rng = random.Random(42)
        state = GameState(
            grid=grid,
            snake_segments=((19, 10), (18, 10), (17, 10)),
            snake_direction=(1, 0),  # RIGHT
            food_position=(5, 5),
            score=0,
            game_over=False,
            rng=rng,
        )
        over_state = tick(state, RIGHT)
        continued = tick(over_state, UP)
        assert continued.snake_direction == over_state.snake_direction
        assert continued.game_over is True
