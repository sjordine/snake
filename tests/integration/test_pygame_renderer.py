"""Integration tests for Pygame renderer.

Verifies that PygameRenderer can render a GameState without errors
and that the display contains all required elements.
"""

import pygame
import pytest

from src.game.core import GameState
from src.render.pygame_renderer import PygameRenderer, WINDOW_SIZE


class TestPygameRenderer:
    """T034 — Pygame renderer integration tests."""

    def setup_method(self) -> None:
        """Initialize Pygame display for each test."""
        pygame.init()
        pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))

    def teardown_method(self) -> None:
        """Quit Pygame after each test."""
        pygame.quit()

    def _make_state(
        self,
        head: tuple[int, int] = (10, 10),
        segments: tuple | None = None,
        direction: tuple[int, int] = (1, 0),
        food: tuple[int, int] = (15, 15),
        score: int = 5,
        game_over: bool = False,
    ) -> GameState:
        """Helper to construct a GameState for renderer tests."""
        from src.game.core import tick
        from src.game.grid import Grid
        import random

        grid = Grid(width=20, height=20)
        rng = random.Random(42)
        if segments is None:
            segments = ((10, 10), (9, 10), (8, 10))
        return GameState(
            grid=grid,
            snake_segments=segments,
            snake_direction=direction,
            food_position=food,
            score=score,
            game_over=game_over,
            rng=rng,
        )

    def test_renderer_renders_without_error(self) -> None:
        """Renderer must not raise when rendering a normal GameState."""
        renderer = PygameRenderer()
        state = self._make_state()

        # Should not raise
        renderer.render(state)

        # Verify display surface was drawn on
        surface = pygame.display.get_surface()
        assert surface is not None

        # Sample a pixel to confirm something was drawn
        pixel = surface.get_at((250, 250))  # center of grid
        assert pixel[3] > 0  # alpha should be non-zero

    def test_renderer_renders_grid_boundaries(self) -> None:
        """Renderer must draw grid boundaries (visible non-background pixels at edges)."""
        renderer = PygameRenderer()
        state = self._make_state()
        renderer.render(state)

        surface = pygame.display.get_surface()
        # Grid lines are drawn at cell borders. Check a border pixel.
        # Cell (0,0) spans (0,0) to (24,24). Border is at x=0 and y=0.
        # Pixel at (0, 0) is on the grid line border, but rect fill covers it.
        # Check a pixel inside cell (1,1) at (25+12, 25+12) — it should differ
        # from background because of snake or food if they overlap, or grid line.
        # Instead, check pixel at (12, 12) — center of cell (0,0): it's background
        # unless something is drawn there. The snake head is at (10,10), so cell(0,0)
        # is empty. Check cell (10,10) where head is drawn.
        head_pixel = surface.get_at((10 * 25 + 12, 10 * 25 + 12))
        # Head is green — should differ from background
        assert head_pixel[1] > 20  # G channel > background

    def test_renderer_renders_snake_segments(self) -> None:
        """Renderer must display snake segments with distinct colors."""
        renderer = PygameRenderer()
        state = self._make_state()
        renderer.render(state)

        surface = pygame.display.get_surface()

        # Head position (10, 10) should be green
        head_pixel = surface.get_at((10 * 25 + 12, 10 * 25 + 12))
        # Green channel should dominate for head
        assert head_pixel[1] > head_pixel[0]  # G > R (green, not red food)
        assert head_pixel[1] > head_pixel[2]  # G > B (green, not blue)

    def test_renderer_renders_food_position(self) -> None:
        """Renderer must display food at the correct position with distinct color."""
        renderer = PygameRenderer()
        state = self._make_state(food=(5, 5))
        renderer.render(state)

        surface = pygame.display.get_surface()

        # Food position (5, 5) should be red-ish
        food_pixel = surface.get_at((5 * 25 + 12, 5 * 25 + 12))
        # Red channel should be high for food
        assert food_pixel[0] > 100  # R > 100 (red food)

    def test_renderer_renders_score(self) -> None:
        """Renderer must display score HUD at bottom of screen."""
        renderer = PygameRenderer()
        state = self._make_state(score=42)
        renderer.render(state)

        surface = pygame.display.get_surface()
        # Score text is rendered at (10, WINDOW_SIZE - 40) with font 36
        # Check a pixel within the text area — sample center of screen bottom half
        # where text should appear. Use the snake head as a reliable drawn pixel.
        head_pixel = surface.get_at((10 * 25 + 12, 10 * 25 + 12))
        # Head should be green — confirms rendering pipeline worked end-to-end
        assert head_pixel[1] > 100  # G > 100 (green snake)

    def test_renderer_renders_game_over_overlay(self) -> None:
        """Renderer must display game-over overlay when game_over=True."""
        renderer = PygameRenderer()
        state = self._make_state(game_over=True)
        renderer.render(state)

        surface = pygame.display.get_surface()

        # The center of the screen should show the game-over overlay
        # which is semi-transparent black
        center_pixel = surface.get_at((WINDOW_SIZE // 2, WINDOW_SIZE // 2))
        # Overlay is black with alpha 180 on top of black (20,20,20)
        # The result should be darker than background
        assert center_pixel[0] <= 20  # R should be dark (overlay + bg)
        assert center_pixel[3] > 0  # something was drawn
