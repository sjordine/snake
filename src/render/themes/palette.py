"""Color palettes for Snake themes.

Module-level constant PALETTE maps theme names to color dictionaries.
Each inner dict has required keys: bg, snake_body, snake_head, food,
hud, game_over_text, game_over_bg, grid.
Values are RGB 3-tuples with components 0-255.
Immutable after import — never mutated at runtime.
"""

# Common required keys shared by every theme
_REQUIRED_KEYS = frozenset([
    "bg", "snake_body", "snake_head", "food",
    "hud", "game_over_text", "game_over_bg", "grid",
])


def _validate_palette(palette: dict) -> None:
    """Validate that a color palette dict has all required keys and valid RGB values."""
    for key in _REQUIRED_KEYS:
        if key not in palette:
            raise KeyError(f"Missing required palette key: {key!r}")
    for color_name, color_value in palette.items():
        if len(color_value) != 3:
            raise ValueError(
                f"Palette color {color_name!r} must be a 3-tuple, got {len(color_value)} values"
            )
        for component in color_value:
            if not (0 <= component <= 255):
                raise ValueError(
                    f"Palette color {color_name!r} component {component} out of range 0-255"
                )


PALETTE: dict[str, dict[str, tuple[int, int, int]]] = {
    "default": {
        "bg": (20, 20, 20),
        "snake_body": (0, 150, 0),
        "snake_head": (0, 200, 0),
        "food": (220, 50, 50),
        "hud": (200, 200, 200),
        "game_over_text": (180, 140, 0),
        "game_over_bg": (0, 0, 0),
        "grid": (40, 40, 40),
    },
    "mario": {
        "bg": (42, 42, 224),
        "snake_body": (0, 94, 195),
        "snake_head": (235, 33, 33),
        "snake_head_detail": (255, 180, 120),
        "food": (255, 215, 0),
        "food_detail": (255, 255, 255),
        "hud": (255, 255, 255),
        "game_over_text": (235, 33, 33),
        "game_over_bg": (0, 0, 0),
        "grid": (184, 109, 27),
    },
}

# Validate at import time
for _theme_name, _colors in PALETTE.items():
    _validate_palette(_colors)
del _theme_name, _colors
