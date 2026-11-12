"""Terminal ASCII renderer for Snake."""

import os
import sys

from ..game.core import GameState


class TerminalRenderer:
    """Renders a GameState to the terminal as ASCII art.

    Contract: Pure print operation, no side effects on GameState
    (per renderer-interface.md contract).
    """

    # Visual characters
    CH_SNAKE_HEAD = "@"
    CH_SNAKE_BODY = "#"
    CH_FOOD = "*"
    CH_EMPTY = "."
    CH_WALL = "+"
    COLOR_RESET = "\033[0m"
    COLOR_GREEN = "\033[92m"
    COLOR_RED = "\033[91m"
    COLOR_YELLOW = "\033[93m"
    COLOR_WHITE = "\033[97m"
    COLOR_CYAN = "\033[96m"
    ANSI_CLEAR = "\033[2J\033[H"

    def __init__(self, color: bool = True) -> None:
        """Initialize renderer.

        Args:
            color: Use ANSI color codes (default True). Set False for monochrome.
        """
        self.color = color

    def _c(self, text: str, color: str) -> str:
        """Wrap text in color if enabled."""
        if self.color:
            return f"{color}{text}{self.COLOR_RESET}"
        return text

    def render(self, state: GameState) -> None:
        """Render the current game state to the terminal.

        Draws:
        - Grid boundaries with `+` and `-`/`|` characters.
        - Snake segments as `#` (body) and `@` (head), in green.
        - Food as `*`, in red.
        - Score below the grid, in cyan.
        - Game-over overlay in yellow.

        Args:
            state: The current GameState to render.
        """
        width = state.grid.width
        height = state.grid.height

        # Clear screen and move cursor to top-left
        sys.stdout.write(self.ANSI_CLEAR)
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
        if 0 <= fx < width and 0 <= fy < height:
            grid_chars[fy][fx] = self.CH_FOOD

        # Render grid with borders
        sys.stdout.write(self._c("+", self.COLOR_WHITE))
        sys.stdout.write(self._c("-" * width, self.COLOR_WHITE))
        sys.stdout.write(self._c("+", self.COLOR_WHITE))
        sys.stdout.write("\n")

        for y in range(height):
            sys.stdout.write(self._c("|", self.COLOR_WHITE))
            for x in range(width):
                ch = grid_chars[y][x]
                if ch == self.CH_SNAKE_HEAD:
                    sys.stdout.write(self._c(ch, self.COLOR_GREEN))
                elif ch == self.CH_SNAKE_BODY:
                    sys.stdout.write(self._c(ch, self.COLOR_GREEN))
                elif ch == self.CH_FOOD:
                    sys.stdout.write(self._c(ch, self.COLOR_RED))
                else:
                    sys.stdout.write(self._c(ch, self.COLOR_WHITE))
            sys.stdout.write(self._c("|", self.COLOR_WHITE))
            sys.stdout.write("\n")

        sys.stdout.write(self._c("+", self.COLOR_WHITE))
        sys.stdout.write(self._c("-" * width, self.COLOR_WHITE))
        sys.stdout.write(self._c("+", self.COLOR_WHITE))
        sys.stdout.write("\n")

        # Score display
        score_text = self._c(f"Score: {state.score}", self.COLOR_CYAN)
        sys.stdout.write(f"{score_text}\n")

        # Game-over overlay
        if state.game_over:
            go_text = self._c(" GAME OVER — Press q to quit, r to restart ", self.COLOR_YELLOW)
            sys.stdout.write(f"\n{go_text}\n")
            sys.stdout.write(self._c("Directions: Arrow keys | Quit: q | Restart: r\n", self.COLOR_WHITE))
        else:
            sys.stdout.write(self._c("Arrow keys to move | q to quit\n", self.COLOR_WHITE))

        sys.stdout.flush()
