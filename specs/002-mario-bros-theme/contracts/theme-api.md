# Contract: Theme API

**Package**: `src.render.themes`
**Scope**: Public interface for theme configuration and renderer theme application.

---

## 1. Palette Module (`src/render/themes/palette.py`)

### Module-Level Constants

```python
PALETTE: dict[str, dict[str, tuple[int, int, int]]]
```

A module-level dictionary mapping theme names to color dictionaries.

**Invariants**:
- Keys are lowercase theme identifiers: `"default"`, `"mario"`
- Each inner dict has at least the required color keys
- Values are RGB tuples (3 ints, each 0–255)
- The dictionary is immutable after module load — never mutated at runtime

**Required color keys per theme**:
`bg`, `snake_body`, `snake_head`, `food`, `hud`, `game_over_text`, `game_over_bg`, `grid`

---

## 2. Config Module (`src/render/themes/config.py`)

### `ThemeConfig` Dataclass

```python
@dataclass(frozen=True)
class ThemeConfig:
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
```

**Invariants**:
- Frozen (immutable) — created once, shared read-only
- All RGB fields are 3-tuples of values 0–255
- `game_over_bg_color` is a 4-tuple (RGBA)
- `snake_head_detail` and `food_detail` are optional
- `terminal_fg_override` is a mapping of terminal color role → ANSI 256-color index

### Module-Level Instances

```python
DEFAULT_THEME: ThemeConfig  # Pre-built with default snake colors
MARIO_THEME: ThemeConfig    # Pre-built with Mario Bros. colors
```

**Invariants**:
- Both are module-level singletons — imported and shared read-only
- No factory function needed — two fixed themes
- `DEFAULT_THEME.name == "Default"`, `MARIO_THEME.name == "Mario Bros."`

---

## 3. Renderer Contract

### `PygameRenderer` Signature Change

```python
class PygameRenderer:
    def __init__(
        self,
        cell_size: int = CELL_SIZE,
        theme_config: ThemeConfig | None = None,
    ) -> None: ...

    def toggle_theme(self) -> None: ...
```

**Contract**:
- `theme_config`: If `None`, defaults to `DEFAULT_THEME`. If provided, must be either `DEFAULT_THEME` or `MARIO_THEME`.
- `toggle_theme()`: Switches between `DEFAULT_THEME` and `MARIO_THEME` for the renderer instance. Mutates the renderer's internal theme reference, not any game state. Returns `None`.
- After `toggle_theme()`, the next `render(state)` call uses the new theme's colors.
- No visual glitch or partial frame is produced — theme switch is atomic per frame.

### `TerminalRenderer` Signature Change

```python
class TerminalRenderer:
    def __init__(
        self,
        color: bool = True,
        theme_config: ThemeConfig | None = None,
    ) -> None: ...

    def toggle_theme(self) -> None: ...
```

**Contract**:
- Same semantics as `PygameRenderer.toggle_theme()`.
- If `color=False`, theme is effectively ignored (falls back to monochrome).
- `terminal_fg_override` is used only when `color=True`.

---

## 4. Input Contract

### Pygame Input — `T` Key Detection

**Event handler in main.py event loop**:
```python
# After existing event loop
for event in pygame.event.get():
    ...
    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_t:
            pygame_renderer.toggle_theme()
        elif event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
            running = False
        elif event.key == pygame.K_r:
            game_state = reset_game(seed)
```

**Invariants**:
- `K_t` toggle must not conflict with existing key bindings (direction: W/A/S/D or arrows; quit: Q; restart: R).
- Toggle is non-blocking — reads event and applies instantly.

### Terminal Input — `T` Key Detection

**Input handler in main.py**:
```python
# After existing input polling
key = poll_terminal_key(timeout=0)
if key in ("t", "T"):
    terminal_renderer.toggle_theme()
```

**Invariants**:
- `T` toggle must not conflict with existing terminal keys (direction: WASD; quit: Q; restart: R).
- Toggle is polled every frame like direction keys — no blocking wait.

---

## 5. Food Rendering Contract

### Pygame — Coin Rendering

```python
def render_coin(screen: pygame.Surface, pos: Position, cell_size: int, theme: ThemeConfig) -> None:
    """Render food as a gold coin."""
    rect = pygame.Rect(pos.x * cell_size, pos.y * cell_size, cell_size, cell_size)
    pygame.draw.ellipse(screen, theme.food_color, rect)
    if theme.food_detail is not None:
        pygame.draw.line(
            screen,
            theme.food_detail,
            (pos.x * cell_size + cell_size // 4, pos.y * cell_size + cell_size // 3),
            (pos.x * cell_size + 3 * cell_size // 4, pos.y * cell_size + cell_size // 3),
            2,
        )
```

### Terminal — Coin Character

Replace existing `CH_FOOD = "*"` with `CH_FOOD = "◉"` when Mario theme is active.

### Default Theme Food Rendering

Unchanged from current implementation: `COLOR_FOOD = (220, 50, 50)` red square/circle.

---

## 6. Snake Head Rendering Contract

### Pygame — Mario Head with Eyes

```python
def render_snake_head(screen: pygame.Surface, pos: Position, cell_size: int, theme: ThemeConfig) -> None:
    """Render snake head with optional Mario face detail."""
    head_rect = pygame.Rect(pos.x * cell_size, pos.y * cell_size, cell_size, cell_size)
    pygame.draw.rect(screen, theme.snake_head_color, head_rect)
    if theme.snake_head_detail is not None and cell_size >= 10:
        eye_size = max(1, cell_size // 5)
        # Left eye
        eye1_x = pos.x * cell_size + cell_size // 4 - eye_size // 2
        eye1_y = pos.y * cell_size + cell_size // 4 - eye_size // 2
        pygame.draw.rect(screen, theme.snake_head_detail, (eye1_x, eye1_y, eye_size, eye_size))
        # Right eye
        eye2_x = pos.x * cell_size + 3 * cell_size // 4 - eye_size // 2
        eye2_y = pos.y * cell_size + cell_size // 4 - eye_size // 2
        pygame.draw.rect(screen, theme.snake_head_detail, (eye2_x, eye2_y, eye_size, eye_size))
```

### Terminal — Head Character

Unchanged from current `CH_SNAKE_HEAD = "@"` — the color already provides differentiation (red for Mario head).

---

## 7. Main.py Wiring Contract

```python
# Creation
from src.render.themes.config import DEFAULT_THEME, MARIO_THEME

pygame_renderer = PygameRenderer(
    cell_size=CELL_SIZE,
    theme_config=DEFAULT_THEME,
)

# Toggle (in game loop)
pygame_renderer.toggle_theme()

# Pass active theme config during rendering (renderer stores internally)
pygame_renderer.render(game_state)
```

**Invariants**:
- `main.py` holds references to both `DEFAULT_THEME` and `MARIO_THEME`
- The toggle switches the renderer's active config reference
- No game state is passed to theme functions — themes only consume `GameState` via the renderer's existing `render()` signature
