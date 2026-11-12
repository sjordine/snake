"""Tests for collision detection."""

import pytest

from src.game.collision import check_wall_collision, check_self_collision


class TestCheckWallCollision:
    """Test wall collision detection."""

    def test_wall_collision_at_right_edge(self) -> None:
        """x = grid_width must be a wall collision (per FR-010)."""
        assert check_wall_collision((20, 10), grid_width=20, grid_height=20) is True

    def test_wall_collision_at_left_edge(self) -> None:
        """x = -1 must be a wall collision."""
        assert check_wall_collision((-1, 10), grid_width=20, grid_height=20) is True

    def test_wall_collision_at_top_edge(self) -> None:
        """y = -1 must be a wall collision."""
        assert check_wall_collision((10, -1), grid_width=20, grid_height=20) is True

    def test_wall_collision_at_bottom_edge(self) -> None:
        """y = grid_height must be a wall collision."""
        assert check_wall_collision((10, 20), grid_width=20, grid_height=20) is True

    def test_no_wall_collision_inside_grid(self) -> None:
        """Coordinates within bounds must NOT trigger wall collision."""
        assert check_wall_collision((0, 0), grid_width=20, grid_height=20) is False
        assert check_wall_collision((19, 19), grid_width=20, grid_height=20) is False
        assert check_wall_collision((10, 10), grid_width=20, grid_height=20) is False
        assert check_wall_collision((0, 19), grid_width=20, grid_height=20) is False
        assert check_wall_collision((19, 0), grid_width=20, grid_height=20) is False

    def test_wall_collision_custom_dimensions(self) -> None:
        """Wall collision must respect custom grid dimensions."""
        assert check_wall_collision((10, 0), grid_width=10, grid_height=10) is True
        assert check_wall_collision((9, 9), grid_width=10, grid_height=10) is False


class TestCheckSelfCollision:
    """Test self-collision detection."""

    def test_no_self_collision_clear_path(self) -> None:
        """New head far from body must not collide."""
        segments = ((10, 10), (10, 11), (10, 12))  # head at (10, 10)
        assert check_self_collision((11, 10), segments, tail_removed=True) is False

    def test_self_collision_body_overlap(self) -> None:
        """New head on body segment must collide."""
        # Snake: head(5,5), body(5,6), tail(5,7)
        segments = ((5, 5), (5, 6), (5, 7))
        assert check_self_collision((5, 6), segments, tail_removed=True) is True
        assert check_self_collision((5, 5), segments, tail_removed=True) is True

    def test_no_collision_with_tail_when_removed(self) -> None:
        """New head on tail position must NOT collide when tail is being removed.
        
        This is the key case: snake moves into the cell its tail occupied
        this tick because the tail moves away simultaneously.
        """
        # Snake: head(5,5), body(5,6), tail(5,7)
        # Moving right: new_head = (6, 5), tail_removed = True
        segments = ((5, 5), (5, 6), (5, 7))
        assert check_self_collision((5, 7), segments, tail_removed=True) is False

    def test_collision_with_tail_when_not_removed(self) -> None:
        """New head on tail position MUST collide when tail is NOT being removed (growing).
        
        When snake eats food, tail is preserved, so colliding with tail is real.
        """
        # Snake: head(5,5), body(5,6), tail(5,7)
        # Moving right, ate_food so tail NOT removed: new_head = (6, 5)
        # This shouldn't collide, but let's test with a case that does
        segments = ((5, 5), (5, 6), (5, 7))
        # If new head is (5, 7) and tail is not removed, that's a collision
        assert check_self_collision((5, 7), segments, tail_removed=False) is True

    def test_self_collision_looping_back(self) -> None:
        """Long snake looping back on itself must detect self collision."""
        # Snake forming a loop: head(5,5) -> right to (6,5) -> down to (6,6) -> left to (5,6) -> down to (5,7) -> left to (4,7)
        segments = ((5, 5), (6, 5), (6, 6), (5, 6), (5, 7), (4, 7))
        # If head moves down to (6, 5) — wait, (6,5) is index 1 (body)
        # Actually head is at (5,5), moving down: new_head = (5, 6)
        assert check_self_collision((5, 6), segments, tail_removed=True) is True
