# Data Model: Mario Bros. Theme

## Overview

This document defines the data structures for the Mario Bros. visual theme. All data lives exclusively in the `render/themes/` subpackage. The game core (`game.core`) has zero awareness of themes.

---

## ThemeConfig

**Package**: `src.render.themes.config`

**Purpose**: Holds all visual configuration for a single theme. Each theme (default, Mario) gets its own `ThemeConfig` instance. Renderers receive the config at construction time and reference it during rendering.

**Rationale**: A single flat dataclass is simpler than nested objects. Two themes don't justify inheritance. Per the constitution (Principle IV), no strategy pattern or interface hierarchy is needed.

```
ThemeConfig:
  name: str                      # Human-readable theme name, e.g. "Mario Bros." or "Default"
  bg_color: tuple[int, int, int] # RGB tuple for background
  snake_body_color: tuple[int, int, int]  # RGB for body segments
  snake_body_inner: tuple[int, int, int]  # RGB for inner highlight on body
  snake_head_color: tuple[int, int, int]  # RGB for head segment
  snake_head_detail: tuple[int, int, int] | None  # RGB for head accent (eyes, etc.)
  food_color: tuple[int, int, int]  # RGB for food item
  food_detail: tuple[int, int, int] | None  # RGB for food accent (coin line)
  hud_text_color: tuple[int, int, int]   # RGB for score and status text
  game_over_text_color: tuple[int, int, int]  # RGB for game-over text
  game_over_bg_color: tuple[int, int, int, int]  # RGBA for game-over overlay
  grid_line_color: tuple[int, int, int]  # RGB for grid cell borders
  terminal_fg_override: dict[str, int] | None  # Optional 256-color terminal color indices
```

### Validation Rules

| Rule | Description |
|------|-------------|
| `name` must be non-empty | Prevents blank theme names in logs and debug output |
| All RGB tuples must contain 3 values, each 0-255 | Prevents invalid color values at construction time |
| `game_over_bg_color` must contain 4 values (RGBA), each 0-255 | Ensures proper alpha blending in pygame |
| `snake_head_detail` and `food_detail` are optional | Not all elements need accent colors |
| `terminal_fg_override` keys must match terminal color keys used by the renderer | Prevents undefined color indices |

### Default Theme Config Values

```
name: "Default"
bg_color: (20, 20, 20)
snake_body_color: (0, 150, 0)
snake_body_inner: (0, 150, 0)
snake_head_color: (0, 200, 0)
snake_head_detail: None
food_color: (220, 50, 50)
food_detail: None
hud_text_color: (200, 200, 200)
game_over_text_color: (180, 140, 0)
game_over_bg_color: (0, 0, 0, 180)
grid_line_color: (40, 40, 40)
terminal_fg_override: None
```

### Mario Theme Config Values

```
name: "Mario Bros."
bg_color: (42, 42, 224)           # Sky blue
snake_body_color: (0, 94, 195)     # Overalls blue
snake_body_inner: (0, 94, 195)
snake_head_color: (235, 33, 33)   # Mario red
snake_head_detail: (255, 180, 120) # Skin tone (eyes)
food_color: (255, 215, 0)         # Coin gold
food_detail: (255, 255, 255)      # White coin highlight
hud_text_color: (255, 255, 255)   # White text on blue sky
game_over_text_color: (235, 33, 33)  # Mario red game-over text
game_over_bg_color: (0, 0, 0, 180)
grid_line_color: (184, 109, 27)   # Brick brown
terminal_fg_override: {
    "bg": 21,
    "snake_head": 196,
    "snake_body": 33,
    "food": 226,
    "hud": 231,
    "game_over": 208,
    "grid": 94,
}
```

---

## ThemeState

**Package**: `src.render.themes.config` (internal)

**Purpose**: Represents the runtime state of theme enablement for a renderer instance. A simple boolean flag.

```
ThemeState:
  active: bool  # True = Mario theme, False = default theme
```

### State Transitions

| Current State | Trigger | New State |
|---|---|---|
| `active: False` (default) | User presses `T` | `active: True` (Mario) |
| `active: True` (Mario) | User presses `T` | `active: False` (default) |
| Renderer constructed with `theme_config=MARIO_THEME` | Construction | `active: True` |
| Renderer constructed with `theme_config=DEFAULT_THEME` | Construction | `active: True` (default is the only other option) |

### Validation Rules

| Rule | Description |
|------|-------------|
| `active` is boolean only | No intermediate states; theme is either on or off |

---

## Color Palette

**Package**: `src.render.themes.palette`

**Purpose**: Defines named color constants organized by theme. Each theme name maps to a `dict[str, tuple[int, int, int]]` of color name → RGB tuple. The `ThemeConfig` is constructed by looking up these palette entries.

```
Palette (dict of dict):
  "default": {
    "bg": (20, 20, 20),
    "snake_body": (0, 150, 0),
    "snake_head": (0, 200, 0),
    "food": (220, 50, 50),
    "hud": (200, 200, 200),
    "game_over_text": (180, 140, 0),
    "game_over_bg": (0, 0, 0),
    "grid": (40, 40, 40),
  }
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
  }
```

### Validation Rules

| Rule | Description |
|------|-------------|
| Both "default" and "mario" keys must exist | Prevents missing palette configurations |
| Each palette entry must have at least 8 keys: `bg`, `snake_body`, `snake_head`, `food`, `hud`, `game_over_text`, `game_over_bg`, `grid` | Prevents missing required colors |
| All RGB values must be 0-255 | Prevents invalid color definitions |

---

## Relationships

```
┌─────────────────┐       ┌──────────────────┐
│    Palette       │       │   ThemeConfig    │
│  (static dict)   │──────▶│ (immutable config│
│                  │       │  from palette)   │
└─────────────────┘       └────────┬─────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              ▼                    ▼                    ▼
    ┌────────────────┐  ┌────────────────┐  ┌────────────────┐
    │ PygameRenderer │  │TerminalRenderer│  │  main.py (wire)│
    │  (reads config)│  │  (reads config)│  │  (holds both)  │
    └────────────────┘  └────────────────┘  └────────────────┘
              │
              ▼
    ┌────────────────┐
    │  ThemeState    │
    │  (active bool) │
    └────────────────┘
```

**Key relationships**:
- `Palette` is a static module-level constant — constructed once at import time, never mutated.
- `ThemeConfig` instances are created by looking up colors from `Palette`. They are immutable (constructed once, passed to renderers).
- `ThemeState` is per-renderer instance. Each renderer holds its own active state.
- The game core (`GameState`, `snake`, `food`, `grid`, `collision`, `core`) has **no references** to any theme entity.
