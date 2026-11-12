"""Pygame renderer for Snake.

Renders a 20×20 grid with colored snake segments, colored food,
score HUD, and game-over overlay.

Constraints:
- Completes within one frame budget (~16ms at 60fps).
- Pure rendering: no side effects on GameState.
"""

import pygame

from ..game.core import GameState

# Cell size in pixels
CELL_SIZE = 25
GRID_WIDTH = 20
GRID_HEIGHT = 20
WINDOW_SIZE = GRID_WIDTH * CELL_SIZE  # 500×500

# Colors
COLOR_BG = (20, 20, 20)
COLOR_GRID = (40, 40, 40)
COLOR_SNAKE_HEAD = (0, 200, 0)
COLOR_SNAKE_BODY = (0, 150, 0)
COLOR_FOOD = (220, 50, 50)
COLOR_HUD_TEXT = (200, 200, 200)
COLOR_GAME_OVER = (180, 140, 0)
COLOR_GAME_OVER_BG = (0, 0, 0, 180)


class PygameRenderer:
    """Renders a GameState to a Pygame window.

    Contract: Pure rendering — no mutations to GameState.
    Completes within one frame budget (~16ms at 60fps).
    """

    def __init__(self, cell_size: int = CELL_SIZE) -> None:
        """Initialize the Pygame renderer.

        Args:
            cell_size: Pixel size of each grid cell (default 25, giving 500×500 window).
        """
        self.cell_size = cell_size
        self.window_size = GRID_WIDTH * cell_size
        self._pygame_initialized = False

    def _ensure_pygame(self) -> None:
        """Initialize Pygame if not already done."""
        if not self._pygame_initialized:
            pygame.init()
            self._pygame_initialized = True

    def render(self, state: GameState) -> None:
        """Render the current game state to the Pygame window.

        Draws:
        - Background and grid lines.
        - Snake segments (head and body) in different green shades.
        - Food as a red cell.
        - Score HUD at the bottom.
        - Game-over overlay when game_over is True.

        Args:
            state: The current GameState to render.
        """
        self._ensure_pygame()

        screen = pygame.display.get_surface()
        if screen is None:
            screen = pygame.display.set_mode(
                (self.window_size, self.window_size)
            )
            pygame.display.set_caption("Snake")

        # Fill background
        screen.fill(COLOR_BG)

        # Draw grid cells
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                rect = pygame.Rect(
                    x * self.cell_size,
                    y * self.cell_size,
                    self.cell_size,
                    self.cell_size,
                )
                pygame.draw.rect(screen, COLOR_GRID, rect, 1)

        # Draw snake body (reverse order so head is drawn last, on top)
        segments = state.snake_segments
        for seg in reversed(segments[1:]):  # skip head
            sx, sy = seg
            rect = pygame.Rect(
                sx * self.cell_size,
                sy * self.cell_size,
                self.cell_size,
                self.cell_size,
            )
            pygame.draw.rect(screen, COLOR_SNAKE_BODY, rect)
            # Inner highlight
            inner = rect.inflate(-4, -4)
            pygame.draw.rect(screen, COLOR_SNAKE_BODY, inner)

        # Draw snake head
        hx, hy = segments[0]
        head_rect = pygame.Rect(
            hx * self.cell_size,
            hy * self.cell_size,
            self.cell_size,
            self.cell_size,
        )
        pygame.draw.rect(screen, COLOR_SNAKE_HEAD, head_rect)
        inner_head = head_rect.inflate(-4, -4)
        pygame.draw.rect(screen, COLOR_SNAKE_HEAD, inner_head)

        # Draw food
        fx, fy = state.food_position
        food_rect = pygame.Rect(
            fx * self.cell_size,
            fy * self.cell_size,
            self.cell_size,
            self.cell_size,
        )
        pygame.draw.rect(screen, COLOR_FOOD, food_rect)
        inner_food = food_rect.inflate(-4, -4)
        pygame.draw.rect(screen, COLOR_FOOD, inner_food)

        # Score HUD
        font = pygame.font.Font(None, 36)
        score_surf = font.render(f"Score: {state.score}", True, COLOR_HUD_TEXT)
        screen.blit(score_surf, (10, self.window_size - 40))

        # Game-over overlay
        if state.game_over:
            overlay = pygame.Surface(
                (self.window_size, self.window_size), pygame.SRCALPHA
            )
            overlay.fill(COLOR_GAME_OVER_BG)
            screen.blit(overlay, (0, 0))

            big_font = pygame.font.Font(None, 64)
            go_text = big_font.render("GAME OVER", True, COLOR_GAME_OVER)
            text_rect = go_text.get_rect(
                center=(self.window_size // 2, self.window_size // 2 - 20)
            )
            screen.blit(go_text, text_rect)

            small_font = pygame.font.Font(None, 32)
            restart_text = small_font.render(
                "Press Enter to restart", True, COLOR_HUD_TEXT
            )
            restart_rect = restart_text.get_rect(
                center=(self.window_size // 2, self.window_size // 2 + 40)
            )
            screen.blit(restart_text, restart_rect)

        pygame.display.flip()
