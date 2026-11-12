"""Pygame renderer for Snake.

Renders a 20×20 grid with colored snake segments, colored food,
score HUD, and game-over overlay. Supports theme swapping at
runtime via the `theme_config` parameter and `toggle_theme()` method.

Constraints:
- Completes within one frame budget (~16ms at 60fps).
- Pure rendering: no side effects on GameState.
"""

import pygame

from ..game.core import GameState
from src.render.themes.config import DEFAULT_THEME, MARIO_THEME, ThemeConfig

# Cell size in pixels
CELL_SIZE = 25
GRID_WIDTH = 20
GRID_HEIGHT = 20
WINDOW_SIZE = GRID_WIDTH * CELL_SIZE  # 500×500


class PygameRenderer:
    """Renders a GameState to a Pygame window.

    Contract: Pure rendering — no mutations to GameState.
    Completes within one frame budget (~16ms at 60fps).
    Supports theme toggle at runtime via toggle_theme().
    """

    def __init__(
        self, cell_size: int = CELL_SIZE, theme_config: ThemeConfig | None = None,
    ) -> None:
        """Initialize the Pygame renderer.

        Args:
            cell_size: Pixel size of each grid cell (default 25, giving 500×500 window).
            theme_config: Optional theme configuration. Defaults to DEFAULT_THEME.
        """
        self.cell_size = cell_size
        self.window_size = GRID_WIDTH * cell_size
        self._pygame_initialized = False
        self._theme_config = theme_config or DEFAULT_THEME

    @property
    def theme_config(self) -> ThemeConfig:
        """Current theme configuration."""
        return self._theme_config

    def _ensure_pygame(self) -> None:
        """Initialize Pygame if not already done."""
        if not self._pygame_initialized:
            pygame.init()
            self._pygame_initialized = True

    def toggle_theme(self) -> None:
        """Swap between DEFAULT_THEME and MARIO_THEME.

        The next render() call will use the new theme's colors.
        No partial frame or glitch.
        """
        if self._theme_config.name == "Mario Bros.":
            self._theme_config = DEFAULT_THEME
        else:
            self._theme_config = MARIO_THEME

    # ── Rendering helpers ───────────────────────────────────────

    def _render_snake_head(
        self, screen: pygame.Surface, pos: tuple[int, int],
    ) -> None:
        """Draw the snake head with optional eye detail.

        Args:
            screen: The display surface.
            pos: Grid position (x, y) of the head.
        """
        theme = self._theme_config
        cx = pos[0] * self.cell_size
        cy = pos[1] * self.cell_size
        head_rect = pygame.Rect(cx, cy, self.cell_size, self.cell_size)

        pygame.draw.rect(screen, theme.snake_head_color, head_rect)
        inner_head = head_rect.inflate(-4, -4)
        pygame.draw.rect(screen, theme.snake_head_color, inner_head)

        # Draw eyes if detail color is set (Mario theme)
        if theme.snake_head_detail is not None and self.cell_size >= 10:
            eye_size = max(1, self.cell_size // 5)
            # Eyes on the top row of the head
            for eye_x_offset in (1, 3):
                ex = cx + eye_x_offset * self.cell_size // 4 - eye_size // 2
                ey = cy + self.cell_size // 4 - eye_size // 2
                eye_rect = pygame.Rect(ex, ey, eye_size, eye_size)
                pygame.draw.rect(screen, theme.snake_head_detail, eye_rect)

    def _render_food_coin(self, screen: pygame.Surface, pos: tuple[int, int]) -> None:
        """Draw food as a coin (gold ellipse with white highlight).

        Args:
            screen: The display surface.
            pos: Grid position (x, y) of the food.
        """
        theme = self._theme_config
        cx = pos[0] * self.cell_size
        cy = pos[1] * self.cell_size
        food_rect = pygame.Rect(cx, cy, self.cell_size, self.cell_size)

        # Draw gold ellipse filling the cell
        pygame.draw.ellipse(
            screen,
            theme.food_color,
            food_rect.inflate(-2, -2),
        )

        # White highlight line across center at 1/3 cell height
        if theme.food_detail is not None:
            highlight_y = cy + self.cell_size // 3
            line_length = self.cell_size - 6
            pygame.draw.line(
                screen,
                theme.food_detail,
                (cx + 3, highlight_y),
                (cx + self.cell_size - 3, highlight_y),
                2,
            )

    def _render_background(self, screen: pygame.Surface) -> None:
        """Fill background and draw grid lines.

        Args:
            screen: The display surface.
        """
        theme = self._theme_config
        screen.fill(theme.bg_color)

        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                rect = pygame.Rect(
                    x * self.cell_size,
                    y * self.cell_size,
                    self.cell_size,
                    self.cell_size,
                )
                pygame.draw.rect(screen, theme.grid_line_color, rect, 1)

    def _render_snake_body(self, screen: pygame.Surface, segments: list[tuple[int, int]]) -> None:
        """Draw all snake body segments (excluding head).

        Args:
            screen: The display surface.
            segments: List of (x, y) tuples for body segments.
        """
        theme = self._theme_config
        for seg in reversed(segments[1:]):  # skip head
            sx, sy = seg
            rect = pygame.Rect(
                sx * self.cell_size,
                sy * self.cell_size,
                self.cell_size,
                self.cell_size,
            )
            pygame.draw.rect(screen, theme.snake_body_color, rect)
            inner = rect.inflate(-4, -4)
            pygame.draw.rect(screen, theme.snake_body_inner, inner)

    def _render_hud(self, screen: pygame.Surface, score: int) -> None:
        """Draw score HUD text.

        Args:
            screen: The display surface.
            score: Current player score.
        """
        theme = self._theme_config
        font = pygame.font.Font(None, 36)
        score_surf = font.render(f"Score: {score}", True, theme.hud_text_color)
        screen.blit(score_surf, (10, self.window_size - 40))

    def _render_game_over(self, screen: pygame.Surface, state: GameState) -> None:
        """Draw game-over overlay.

        Args:
            screen: The display surface.
            state: Current game state.
        """
        theme = self._theme_config

        # Semi-transparent overlay
        overlay = pygame.Surface(
            (self.window_size, self.window_size), pygame.SRCALPHA
        )
        overlay.fill(theme.game_over_bg_color)
        screen.blit(overlay, (0, 0))

        big_font = pygame.font.Font(None, 64)
        go_text = big_font.render("GAME OVER", True, theme.game_over_text_color)
        text_rect = go_text.get_rect(
            center=(self.window_size // 2, self.window_size // 2 - 20)
        )
        screen.blit(go_text, text_rect)

        small_font = pygame.font.Font(None, 32)
        restart_text = small_font.render(
            "Press Enter to restart", True, theme.hud_text_color
        )
        restart_rect = restart_text.get_rect(
            center=(self.window_size // 2, self.window_size // 2 + 40)
        )
        screen.blit(restart_text, restart_rect)

    # ── Public API ──────────────────────────────────────────────

    def render(self, state: GameState) -> None:
        """Render the current game state to the Pygame window.

        Draws:
        - Background and grid lines (theme-aware).
        - Snake segments (head with optional eye detail, body).
        - Food as a coin (gold ellipse + white highlight).
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

        # Draw layers
        self._render_background(screen)
        self._render_snake_body(screen, state.snake_segments)
        self._render_snake_head(screen, state.snake_segments[0])
        self._render_food_coin(screen, state.food_position)
        self._render_hud(screen, state.score)

        if state.game_over:
            self._render_game_over(screen, state)

        pygame.display.flip()
