"""Snake game — terminal entry point."""

import sys
import time
from pathlib import Path

# Add project root (parent of src/) to sys.path so 'src' is the package root
sys.path.insert(0, str(Path(__file__).parent))

from src.game.core import GameState, tick
from src.game.snake import RIGHT
from src.input.terminal_input import poll_terminal_key, is_quit, is_restart
from src.render.terminal_renderer import TerminalRenderer


TICKS_PER_SECOND = 10
TICK_INTERVAL = 1.0 / TICKS_PER_SECOND


def game_loop(renderer: TerminalRenderer) -> None:
    """Run the terminal Snake game loop."""
    state = GameState.initial(seed=42)

    while True:
        # ── Tick interval: accumulate real time, apply ticks at ~10 Hz ──
        tick_accumulator = 0.0
        last_time = time.monotonic()

        while not state.game_over:
            now = time.monotonic()
            tick_accumulator += now - last_time
            last_time = now

            # Process accumulated ticks
            while tick_accumulator >= TICK_INTERVAL:
                tick_accumulator -= TICK_INTERVAL

                # Poll input
                direction = poll_terminal_key()
                if direction is not None:
                    if is_quit(direction):
                        return
                    if is_restart(direction):
                        # Break out to restart
                        break
                    else:
                        state = tick(state, direction)
                else:
                    state = tick(state, RIGHT)

                # Render only after a tick advances
                renderer.render(state)

            # Small sleep to prevent CPU spin
            time.sleep(0.001)

        # ── Game over: show final state, wait for restart or quit ──
        renderer.render(state)
        print(
            f"\nGame Over! Score: {state.score}. "
            "Press 'r' to restart, 'q' to quit."
        )

        while True:
            direction = poll_terminal_key()
            if direction is not None:
                if is_quit(direction):
                    return
                if is_restart(direction) or direction in ("\n", "\r"):
                    break
                # Other keys: ignore
            time.sleep(0.01)

        # Restart
        state = GameState.initial(seed=42)


def main() -> None:
    """Start the Snake game."""
    renderer = TerminalRenderer(color=True)
    print("Snake — Arrow keys or WASD to move, 'q' to quit, 'r' to restart")
    game_loop(renderer)


if __name__ == "__main__":
    main()
