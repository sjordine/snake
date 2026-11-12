"""Snake game entry point.

Wires GameState + renderer + input adapter into a playable game loop.

Usage:
    python -m src.main [--renderer=terminal|pygame]

Default renderer is pygame.
"""

import argparse
import sys
import time

from src.game.core import GameState, tick
from src.render.terminal_renderer import TerminalRenderer
from src.render.pygame_renderer import PygameRenderer
from src.input.terminal_input import poll_terminal_key, is_quit, is_restart
from src.input.pygame_input import PygameInput


TICK_RATE = 10  # ticks per second
TICK_INTERVAL = 1.0 / TICK_RATE


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI."""
    parser = argparse.ArgumentParser(description="Snake Game")
    parser.add_argument(
        "--renderer",
        choices=["terminal", "pygame"],
        default="pygame",
        help="Rendering backend (default: pygame)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for deterministic food spawn (default: 42)",
    )
    return parser


def run_terminal_game(seed: int = 42) -> None:
    """Run the Snake game in the terminal."""
    renderer = TerminalRenderer()
    state = GameState.initial(seed=seed)

    current_direction = state.snake_direction  # track direction for input

    running = True
    while running:
        renderer.render(state)

        key = poll_terminal_key()

        if key is not None:
            if is_quit(key):
                running = False
                continue
            if is_restart(key):
                state = GameState.initial(seed=seed)
                current_direction = state.snake_direction
                continue
            # key is a direction tuple
            current_direction = key

        state = tick(state, current_direction)
        time.sleep(TICK_INTERVAL)


def run_pygame_game(seed: int = 42) -> None:
    """Run the Snake game with Pygame rendering."""
    pygame_renderer = PygameRenderer()
    pygame_input = PygameInput()
    state = GameState.initial(seed=seed)

    current_direction = state.snake_direction

    # Set up display for initial render
    pygame_renderer.render(state)

    running = True
    tick_timer = time.monotonic()

    while running:
        now = time.monotonic()
        if now - tick_timer >= TICK_INTERVAL:
            tick_timer = now

            result = pygame_input.poll_events()

            if result is not None:
                if pygame_input.is_quit(result):
                    running = False
                    continue
                if pygame_input.is_restart(result):
                    if state.game_over:
                        state = GameState.initial(seed=seed)
                        current_direction = state.snake_direction
                    continue
                current_direction = result

            state = tick(state, current_direction)

        pygame_renderer.render(state)


def main() -> None:
    """Entry point: parse args, select renderer, run game loop."""
    parser = create_parser()
    args = parser.parse_args()

    if args.renderer == "terminal":
        run_terminal_game(seed=args.seed)
    else:
        # Pygame renderer
        try:
            run_pygame_game(seed=args.seed)
        except pygame.error as e:
            print(f"Pygame error: {e}", file=sys.stderr)
            print("Falling back to terminal renderer.", file=sys.stderr)
            run_terminal_game(seed=args.seed)


if __name__ == "__main__":
    main()
