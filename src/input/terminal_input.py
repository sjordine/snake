"""Terminal keyboard input handler for Snake."""

import sys

from ..game.snake import UP, DOWN, LEFT, RIGHT, VALID_DIRECTIONS, opposite


def poll_terminal_key() -> tuple[int, int] | str | None:
    """Read a single key press from stdin (non-blocking).

    Uses tty.cbreak mode so characters are available immediately
    without waiting for Enter. Returns None if no key pressed.

    Returns:
        Direction tuple (dx, dy) for arrow/WASD keys,
        a single-character command string ("q"/"r"), or None.
    """
    import select
    import tty
    import termios

    fd = sys.stdin.fileno()
    old_attrs = termios.tcgetattr(fd)

    try:
        tty.setcbreak(fd)
        # Non-blocking read with short timeout
        ready, _, _ = select.select([sys.stdin], [], [], 0.001)
        if ready:
            key = sys.stdin.read(1)
            direction = _key_to_direction(key)
            if direction is not None:
                return direction
            # Return command keys as strings
            if key in ("q", "r"):
                return key
    except (OSError, termios.error):
        pass
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_attrs)

    return None


def _key_to_direction(key: str) -> tuple[int, int] | None:
    """Map a key character to a direction tuple.

    Args:
        key: A single character from stdin.

    Returns:
        Direction tuple or None if not an arrow key.
    """
    mapping: dict[str, tuple[int, int]] = {
        "\x1b[A": UP,    # Up arrow (escape sequence)
        "\x1b[B": DOWN,   # Down arrow
        "\x1b[C": RIGHT,  # Right arrow
        "\x1b[D": LEFT,   # Left arrow
        "w": UP,
        "s": DOWN,
        "d": RIGHT,
        "a": LEFT,
    }
    return mapping.get(key)


def is_quit(key: str | None) -> bool:
    """Check if the key press means quit."""
    return key is not None and key == "q"


def is_restart(key: str | None) -> bool:
    """Check if the key press means restart."""
    return key is not None and key == "r"
