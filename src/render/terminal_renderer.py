"""Terminal ASCII renderer for Snake.

Supports theme-aware ANSI color rendering and character overrides.
"""

import os
import sys

from ..game.core import GameState
from src.render.themes.config import DEFAULT_THEME, MARIO_THEME, ThemeConfig

# ANSI color codes (256-color palette)
ANSI_COLOR_RESET = "\033[0m"
ANSI_COLOR_BLACK = "\033[30m"
ANSI_COLOR_RED = "\033[31m"
ANSI_COLOR_GREEN = "\033[32m"
ANSI_COLOR_YELLOW = "\033[33m"
ANSI_COLOR_BLUE = "\033[34m"
ANSI_COLOR_CYAN = "\033[36m"
ANSI_COLOR_WHITE = "\033[37m"

# 256-color palette for Mario theme
MARIO_256 = {
    "bg": "\033[38;5;21m",       # Sky blue (light blue-ish)
    "snake_head": "\033[38;5;196m",  # Mario red
    "snake_body": "\033[38;5;33m",   # Overworld blue
    "food": "\033[38;5;226m",      # Coin gold
    "hud": "\033[38;5;231m",       # White
    "game_over": "\033[38;5;208m", # Orange-red
    "grid": "\033[38;5;94m",       # Brown brick
}

ANSI_CLEAR = "\033[2J\033[H"


class TerminalRenderer:
    """Renders a GameState to the terminal as ASCII art.

    Contract: Pure print operation, no side effects on GameState.
    Supports theme toggle at runtime via toggle_theme().
    """

    # Default visual characters
    CH_SNAKE_HEAD = "@"
    CH_SNAKE_BODY = "#"
    CH_FOOD_DEFAULT = "*"
    CH_FOOD_MARIO = "◉"
    CH_EMPTY = "."
    CH_WALL = "+"
    COLOR_RESET = ANSI_COLOR_RESET

    def __init__(
        self, color: bool = True, theme_config: ThemeConfig | None = None,
    ) -> None:
        """Initialize renderer.

        Args:
            color: Use ANSI color codes (default True). Set False for monochrome.
            theme_config: Optional theme configuration. Defaults to DEFAULT_THEME.
        """
        self.color = color
        self._theme_config = theme_config or DEFAULT_THEME

    @property
    def theme_config(self) -> ThemeConfig:
        """Current theme configuration."""
        return self._theme_config

    def toggle_theme(self) -> None:
        """Swap between DEFAULT_THEME and MARIO_THEME."""
        if self._theme_config.name == "Mario Bros.":
            self._theme_config = DEFAULT_THEME
        else:
            self._theme_config = MARIO_THEME

    def _c(self, text: str, color: str) -> str:
        """Wrap text in color if enabled."""
        if self.color:
            return f"{color}{text}{self.COLOR_RESET}"
        return text

    def _get_color(self, role: str) -> str:
        """Resolve a color string for a given role.

        Uses terminal_fg_override from the theme config when available,
        otherwise falls back to default ANSI color codes.

        Args:
            role: Color role key (e.g. "snake_head", "food", "bg").

        Returns:
            ANSI color code string.
        """
        overrides = self._theme_config.terminal_fg_override
        if overrides is not None:
            ansi_index = overrides.get(role)
            if ansi_index is not None:
                return f"\033[38;5;{ansi_index}m"

        # Fallback to default ANSI codes
        fallback = {
            "bg": ANSI_COLOR_BLACK,
            "snake_head": ANSI_COLOR_RED,
            "snake_body": ANSI_COLOR_GREEN,
            "food": ANSI_COLOR_RED,
            "hud": ANSI_COLOR_CYAN,
            "game_over": ANSI_COLOR_YELLOW,
            "grid": ANSI_COLOR_WHITE,
        }
        return fallback.get(role, ANSI_COLOR_WHITE)

    def _get_food_char(self) -> str:
        """Get the food character for the current theme."""
        if self._theme_config.name == "Mario Bros.":
            return self.CH_FOOD_MARIO
        return self.CH_FOOD_DEFAULT

    def render(self, state: GameState) -> None:
        """Render the current game state to the terminal.

        Draws:
        - Grid boundaries with theme-aware colors.
        - Snake segments with theme-aware colors and characters.
        - Food with theme-aware character and color.
        - Score below the grid, in theme-aware HUD color.
        - Game-over overlay in theme-aware game-over color.

        Args:
            state: The current GameState to render.
        """
        width = state.grid.width
        height = state.grid.height

        # Clear screen and move cursor to top-left
        sys.stdout.write(ANSI_CLEAR)
        if self.color:
            sys.stdout.write(self.COLOR_RESET)

        # Build the grid as a 2D array of characters
        grid_chars = [[self.CH_EMPTY] * width for _ in range(height)]

        # Draw snake body
        segments = state.snake_segments
        for seg in segments[1:]:  # skip head for now
            x, y = seg
            if 0 <= x < width and 0 <= y < height:
                grid_chars[y][x] = self.CH_SNAKE_BODY

        # Draw snake head
        head_x, head_y = state.head
        if 0 <= head_x < width and 0 <= head_y < height:
            grid_chars[head_y][head_x] = self.CH_SNAKE_HEAD

        # Draw food
        fx, fy = state.food_position
        food_ch = self._get_food_char()
        if 0 <= fx < width and 0 <= fy < height:
            grid_chars[fy][fx] = food_ch

        # Render grid with borders
        sys.stdout.write(self._c("+", self.COLOR_RESET))
        sys.stdout.write(self._c("-" * width, self.COLOR_RESET))
        sys.stdout.write(self._c("+", self.COLOR_RESET))
        sys.stdout.write("\n")

        for y in range(height):
            sys.stdout.write(self._c("|", self.COLOR_RESET))
            for x in range(width):
                ch = grid_chars[y][x]
                if ch == self.CH_SNAKE_HEAD:
                    sys.stdout.write(self._c(ch, self._get_color("snake_head")))
                elif ch == self.CH_SNAKE_BODY:
                    sys.stdout.write(self._c(ch, self._get_color("snake_body")))
                elif ch == food_ch:
                    sys.stdout.write(self._c(ch, self._get_color("food")))
                else:
                    sys.stdout.write(self._c(ch, self._get_color("grid")))
            sys.stdout.write(self._c("|", self.COLOR_RESET))
            sys.stdout.write("\n")

        sys.stdout.write(self._c("+", self.COLOR_RESET))
        sys.stdout.write(self._c("-" * width, self.COLOR_RESET))
        sys.stdout.write(self._c("+", self.COLOR_RESET))
        sys.stdout.write("\n")

        # Score display
        score_text = self._c(f"Score: {state.score}", self._get_color("hud"))
        sys.stdout.write(f"{score_text}\n")

        # Game-over overlay
        if state.game_over:
            go_text = self._c(
                " GAME OVER — Press q to quit, r to restart ",
                self._get_color("game_over"),
            )
            sys.stdout.write(f"\n{go_text}\n")
            sys.stdout.write(
                self._c(
                    "Directions: Arrow keys | Quit: q | Restart: r | Theme: t\n",
                    self._get_color("hud"),
                )
            )
        else:
            sys.stdout.write(
                self._c(
                    "Arrow keys to move | q to quit | Theme: t\n",
                    self._get_color("hud"),
                )
            )

        sys.stdout.flush()
