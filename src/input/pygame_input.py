"""Pygame input adapter for Snake.

Polls pygame.KEYDOWN events and maps Arrow keys to direction tuples.

Constraints:
- Returns one direction change per call (no input stacking).
- Only responds to Arrow keys (no WASD).
- Also handles Enter for restart and Q for quit.
"""

import pygame

from ..game.snake import UP, DOWN, LEFT, RIGHT, VALID_DIRECTIONS


class PygameInput:
    """Adapter that converts Pygame KEYDOWN events to game direction changes.

    Contract:
    - poll_events() returns one direction tuple or a command string or None.
    - Only Arrow keys map to directions; no WASD.
    - Input is consumed per call (no stacking).
    """

    # Pygame key → direction mapping (Arrow keys only)
    _KEY_TO_DIRECTION: dict[int, tuple[int, int]] = {
        pygame.K_UP: UP,
        pygame.K_DOWN: DOWN,
        pygame.K_LEFT: LEFT,
        pygame.K_RIGHT: RIGHT,
    }

    def poll_events(self) -> tuple[int, int] | str | None:
        """Poll for KEYDOWN events.

        Returns:
            Direction tuple for Arrow keys,
            a command string ("r" for restart, "q" for quit),
            or None if no relevant key was pressed.
        """
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                key = event.key
                direction = self._KEY_TO_DIRECTION.get(key)
                if direction is not None:
                    return direction
                # Enter key for restart
                if key == pygame.K_RETURN or key == pygame.K_KP_ENTER:
                    return "r"
                # Q key for quit
                if key == pygame.K_q:
                    return "q"
        return None

    def is_quit(self, result: tuple[int, int] | str | None) -> bool:
        """Check if the poll result means quit."""
        return result == "q"

    def is_restart(self, result: tuple[int, int] | str | None) -> bool:
        """Check if the poll result means restart."""
        return result == "r"
