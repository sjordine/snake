"""Snake game entry point.

Wires GameState + renderer + input adapter into a playable game loop.

Usage:
    python -m src.main [--renderer=terminal|pygame] [--theme=default|mario] [--mute]

Default renderer is pygame. Default theme is default.
"""

import argparse
import sys
import time

from src.game.core import GameState, tick
from src.render.terminal_renderer import TerminalRenderer
from src.render.pygame_renderer import PygameRenderer
from src.input.terminal_input import poll_terminal_key, is_quit, is_restart
from src.input.pygame_input import PygameInput
from src.audio.music import AudioSystem
from src.render.themes.config import DEFAULT_THEME, MARIO_THEME, ThemeConfig

try:
    import pygame
except ImportError:
    pygame = None


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
        "--theme",
        choices=["default", "mario"],
        default="default",
        help="Visual theme at launch (default: default)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for deterministic food spawn (default: 42)",
    )
    parser.add_argument(
        "--mute",
        action="store_true",
        default=False,
        help="Mute background music and sound effects",
    )
    return parser


def _resolve_theme_config(theme_name: str) -> ThemeConfig:
    """Resolve a theme name to its ThemeConfig singleton."""
    if theme_name == "mario":
        return MARIO_THEME
    return DEFAULT_THEME


def run_terminal_game(
    seed: int = 42, theme_config: ThemeConfig | None = None,
) -> None:
    """Run the Snake game in the terminal."""
    renderer = TerminalRenderer(color=True, theme_config=theme_config)
    state = GameState.initial(seed=seed)

    current_direction = state.snake_direction  # track direction for input

    running = True
    while running:
        renderer.render(state)

        key = poll_terminal_key()

        if key is not None:
            if key in ("q", "Q"):
                running = False
                continue
            if key == "r":
                state = GameState.initial(seed=seed)
                current_direction = state.snake_direction
                continue
            if key in ("t", "T"):
                renderer.toggle_theme()
                continue
            # key is a direction tuple
            current_direction = key

        state = tick(state, current_direction)
        time.sleep(TICK_INTERVAL)


def run_pygame_game(
    seed: int = 42, muted: bool = False,
    theme_config: ThemeConfig | None = None,
) -> None:
    """Run the Snake game with Pygame rendering.

    Args:
        seed: Random seed for deterministic food spawn.
        muted: If True, skip all audio initialization.
        theme_config: Optional theme configuration. Defaults to DEFAULT_THEME.
    """
    import pygame  # noqa: E402 — loaded after renderer import
    pygame_renderer = PygameRenderer(
        cell_size=25, theme_config=theme_config,
    )
    pygame_input = PygameInput()
    audio = AudioSystem() if not muted else None
    state = GameState.initial(seed=seed)

    current_direction = state.snake_direction
    old_score = state.score
    old_game_over = state.game_over

    # Set up display for initial render
    pygame_renderer.render(state)

    # Start background music
    if audio:
        audio.play_background()

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
                        old_score = state.score
                        old_game_over = state.game_over
                    continue
                current_direction = result

            state = tick(state, current_direction)

            # Detect score change → food eaten
            if audio and state.score > old_score:
                audio.play_sfx("eat")
                old_score = state.score

            # Detect game-over transition → play death sound
            if audio and not old_game_over and state.game_over:
                audio.play_sfx("death")
                old_game_over = state.game_over

        # Handle pygame events for theme toggle (T key)
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_t:
                    pygame_renderer.toggle_theme()

        pygame_renderer.render(state)

    # Stop music on exit
    if audio:
        audio.stop_background()


def main() -> None:
    """Entry point: parse args, select renderer, run game loop."""
    parser = create_parser()
    args = parser.parse_args()

    theme_config = _resolve_theme_config(args.theme)

    if args.renderer == "terminal":
        run_terminal_game(seed=args.seed, theme_config=theme_config)
    else:
        # Pygame renderer
        try:
            import pygame

            run_pygame_game(
                seed=args.seed, muted=args.mute,
                theme_config=theme_config,
            )
        except pygame.error as e:
            print(f"Pygame error: {e}", file=sys.stderr)
            print("Falling back to terminal renderer.", file=sys.stderr)
            run_terminal_game(seed=args.seed, theme_config=theme_config)


if __name__ == "__main__":
    main()
