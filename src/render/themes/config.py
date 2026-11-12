"""Theme configuration dataclass for Snake.

ThemeConfig is an immutable (frozen) dataclass that holds all visual
configuration for a single theme. Renderers receive a ThemeConfig
instance at construction and reference it during rendering.
"""

from __future__ import annotations

from dataclasses import dataclass

from .palette import PALETTE


@dataclass(frozen=True)
class ThemeConfig:
    """Immutable configuration for a single visual theme.

    Attributes:
        name: Human-readable theme name, e.g. "Mario Bros." or "Default".
        bg_color: RGB background color.
        snake_body_color: RGB for body segments.
        snake_body_inner: RGB for inner highlight on body segments.
        snake_head_color: RGB for head segment.
        snake_head_detail: Optional RGB for head accent (eyes, etc.).
        food_color: RGB for food item.
        food_detail: Optional RGB for food accent (coin highlight line).
        hud_text_color: RGB for score and status text.
        game_over_text_color: RGB for game-over text.
        game_over_bg_color: RGBA for game-over overlay (4-tuple).
        grid_line_color: RGB for grid cell borders.
        terminal_fg_override: Optional dict mapping terminal color role
            to ANSI 256-color index.
    """

    name: str
    bg_color: tuple[int, int, int]
    snake_body_color: tuple[int, int, int]
    snake_body_inner: tuple[int, int, int]
    snake_head_color: tuple[int, int, int]
    snake_head_detail: tuple[int, int, int] | None
    food_color: tuple[int, int, int]
    food_detail: tuple[int, int, int] | None
    hud_text_color: tuple[int, int, int]
    game_over_text_color: tuple[int, int, int]
    game_over_bg_color: tuple[int, int, int, int]
    grid_line_color: tuple[int, int, int]
    terminal_fg_override: dict[str, int] | None

    # ── Validation ──────────────────────────────────────────────
    def __post_init__(self) -> None:
        _validate_rgb_tuple("bg_color", self.bg_color)
        _validate_rgb_tuple("snake_body_color", self.snake_body_color)
        _validate_rgb_tuple("snake_body_inner", self.snake_body_inner)
        _validate_rgb_tuple("snake_head_color", self.snake_head_color)
        _validate_rgb_optional("snake_head_detail", self.snake_head_detail)
        _validate_rgb_tuple("food_color", self.food_color)
        _validate_rgb_optional("food_detail", self.food_detail)
        _validate_rgb_tuple("hud_text_color", self.hud_text_color)
        _validate_rgb_tuple("game_over_text_color", self.game_over_text_color)
        _validate_rgba_tuple("game_over_bg_color", self.game_over_bg_color)
        _validate_rgb_tuple("grid_line_color", self.grid_line_color)


# ── Private helpers ───────────────────────────────────────────


def _validate_rgb_tuple(
    field_name: str, value: tuple[int, int, int]
) -> None:
    """Validate a 3-tuple of ints each in 0-255."""
    if len(value) != 3:
        raise ValueError(
            f"{field_name} must be a 3-tuple, got {len(value)}"
        )
    for v in value:
        if not isinstance(v, int) or not (0 <= v <= 255):
            raise ValueError(
                f"{field_name} values must be ints 0-255, got {v}"
            )


def _validate_rgb_optional(
    field_name: str, value: tuple[int, int, int] | None
) -> None:
    """Validate an optional 3-tuple."""
    if value is None:
        return
    _validate_rgb_tuple(field_name, value)


def _validate_rgba_tuple(
    field_name: str, value: tuple[int, int, int, int]
) -> None:
    """Validate a 4-tuple of ints each in 0-255."""
    if len(value) != 4:
        raise ValueError(
            f"{field_name} must be a 4-tuple, got {len(value)}"
        )
    for v in value:
        if not isinstance(v, int) or not (0 <= v <= 255):
            raise ValueError(
                f"{field_name} values must be ints 0-255, got {v}"
            )


# ── Theme singletons ──────────────────────────────────────────


DEFAULT_THEME = ThemeConfig(
    name="Default",
    bg_color=PALETTE["default"]["bg"],
    snake_body_color=PALETTE["default"]["snake_body"],
    snake_body_inner=PALETTE["default"]["snake_body"],
    snake_head_color=PALETTE["default"]["snake_head"],
    snake_head_detail=None,
    food_color=PALETTE["default"]["food"],
    food_detail=None,
    hud_text_color=PALETTE["default"]["hud"],
    game_over_text_color=PALETTE["default"]["game_over_text"],
    game_over_bg_color=(0, 0, 0, 180),
    grid_line_color=PALETTE["default"]["grid"],
    terminal_fg_override=None,
)


MARIO_THEME = ThemeConfig(
    name="Mario Bros.",
    bg_color=PALETTE["mario"]["bg"],
    snake_body_color=PALETTE["mario"]["snake_body"],
    snake_body_inner=PALETTE["mario"]["snake_body"],
    snake_head_color=PALETTE["mario"]["snake_head"],
    snake_head_detail=PALETTE["mario"]["snake_head_detail"],
    food_color=PALETTE["mario"]["food"],
    food_detail=PALETTE["mario"]["food_detail"],
    hud_text_color=PALETTE["mario"]["hud"],
    game_over_text_color=PALETTE["mario"]["game_over_text"],
    game_over_bg_color=(0, 0, 0, 180),
    grid_line_color=PALETTE["mario"]["grid"],
    terminal_fg_override={
        "bg": 21,
        "snake_head": 196,
        "snake_body": 33,
        "food": 226,
        "hud": 231,
        "game_over": 208,
        "grid": 94,
    },
)
