# Research: Mario Bros. Theme Implementation

## Overview

This research resolves technical decisions for implementing a Mario Bros. visual theme in the Snake game. All decisions respect the "Núcleo Puro, Casca Fina" principle: the theme affects only the rendering layer.

---

## Decision 1: Theme Configuration Approach

**Decision**: Use a simple `ThemeConfig` dataclass with a `Palette` dataclass for color constants. Pass a theme config object to each renderer constructor.

**Rationale**:
- The constitution forbids premature abstraction (Principle IV: "Sem classes base, sem estratégias, sem observers"). A strategy pattern or observer system would violate this.
- Two themes (default + Mario) don't warrant an enum or registry yet. A simple dataclass is sufficient per YAGNI.
- The renderers already accept initialization parameters (e.g., `cell_size` in `PygameRenderer`). Adding a `theme` parameter is consistent.
- Each renderer reads the palette colors it needs at render time — no shared mutable state.

**Alternatives considered**:
1. **Enum-based theme switching** — Added a `Theme` enum. Rejected: overkill for two themes, and the toggle just needs a boolean flag anyway.
2. **Observer pattern for theme changes** — Rejected: constitution explicitly forbids observers. Renderer gets theme as a constructor parameter or a method argument.
3. **Singleton theme manager** — Rejected: unnecessary global state. Each renderer holds its own theme config.

---

## Decision 2: Mario Bros. Color Palette

**Decision**: Use the following NES-era Super Mario Bros. World 1-1 palette, defined as named RGB tuples:

```
Mario Theme Palette:
- BG_BLUE:        (42, 42, 224)   # Sky blue (World 1-1 background)
- BRICK_BROWN:    (184, 109, 27)  # Brick block color
- PIPE_GREEN:     (0, 170, 0)     # Pipe green
- MARIO_RED:      (235, 33, 33)   # Primary red (Mario hat/shirt)
- OVERALL_BLUE:   (0, 94, 195)    # Overalls blue
- COIN_GOLD:      (255, 215, 0)   # Coin yellow/gold
- SKIN_TONE:      (255, 180, 120) # Mario skin tone
- BLACK:          (0, 0, 0)       # Pure black
- WHITE:          (255, 255, 255) # Pure white
```

**Mapping to game elements**:
- **Background**: `BG_BLUE` (replaces current `COLOR_BG = (20, 20, 20)` dark gray)
- **Snake body**: `OVERALL_BLUE` segments with `MARIO_RED` inner highlight
- **Snake head**: `MARIO_RED` with skin-tone accent (small pixel for face detail)
- **Food**: `COIN_GOLD` circular or square with yellow highlight (replaces current `COLOR_FOOD = (220, 50, 50)` red)
- **HUD text**: `WHITE` on `BG_BLUE` (NES-style white text on blue sky)
- **Game-over overlay**: `BLACK` semi-transparent overlay with `MARIO_RED` "GAME OVER" text
- **Grid lines**: `BRICK_BROWN` thin lines (subtle, like brick outlines)

**Terminal theme**:
- **Background**: ANSI 256-color blue (ANSI `\033[48;5;21m`) or standard blue background
- **Snake body**: ANSI green foreground with blue background blocks
- **Snake head**: ANSI red foreground
- **Food**: ANSI yellow foreground (coin color)
- **HUD text**: ANSI white on blue background
- **Game-over**: ANSI yellow text on red background

**Alternatives considered**:
1. **Using actual NES palette hex values** — The RGB values above approximate the NES 64-color palette. Exact palette values would require palette-indexed rendering which pygame doesn't natively support without custom code.
2. **Pixel-art sprite loading from files** — Rejected: constitution and assumptions say no external assets. All rendering must be done with pygame primitives or ANSI codes.
3. **Gradient/3D effect** — Rejected: out of scope for the initial Mario theme. Keep it pixel-flat.

---

## Decision 3: Theme Toggle Mechanism

**Decision**: Add a keyboard shortcut `T` to toggle the Mario theme during gameplay. The renderer receives a `theme_config` parameter and re-renders the next frame with the new colors.

**Rationale**:
- The spec requires a "user-accessible toggle" (FR-005) that works "without restarting the game."
- A single key press is the simplest interaction — no menus, no configuration files.
- The toggle is a boolean flag on the renderer. No game state mutation.
- For Pygame: the toggle is polled in the main event loop (same location as quit/restart).
- For Terminal: the toggle is polled alongside direction keys.

**Alternatives considered**:
1. **Command-line flag `--theme=mario`** — Useful for static launches but doesn't satisfy the "toggle during gameplay" requirement. Can coexist as a bonus.
2. **Menu-based theme selector** — Rejected: over-engineered, adds UI layers for what is a simple toggle.
3. **Auto-cycling themes** — Rejected: out of scope, reduces player agency.

---

## Decision 4: Renderer Modification Strategy

**Decision**: Modify both `PygameRenderer` and `TerminalRenderer` to accept an optional `theme_config` parameter (defaulting to a `DEFAULT_THEME` constant). Each renderer extracts colors from the palette at render time.

**Implementation approach**:
1. Create `render/themes/__init__.py` — exports `DEFAULT_THEME` and `MARIO_THEME`
2. Create `render/themes/palette.py` — defines `Color` dataclass and theme color mappings
3. Create `render/themes/config.py` — defines `ThemeConfig` dataclass with named color attributes
4. Modify `PygameRenderer.__init__(self, cell_size, theme_config)` — store and use theme colors
5. Modify `TerminalRenderer.__init__(self, color, theme_config)` — store and use theme colors
6. Modify `main.py` — create both theme configs, wire `T` key to toggle between them

**Why modify in place rather than create new renderers**:
- Two renderers are simpler than a factory pattern or strategy interface for 2 themes
- The constitution explicitly forbids unnecessary abstraction (Principle IV)
- Adding a theme parameter to existing constructors is a minimal, low-risk change

**Alternatives considered**:
1. **Decorator pattern** — A `ThemedRenderer` that wraps an existing renderer. Rejected: adds complexity without benefit for 2 themes.
2. **Separate theme renderer classes** — `MarioPygameRenderer` subclass. Rejected: violates YAGNI, code duplication.

---

## Decision 5: Visual Representation of Food as Coin

**Decision**: Render the food item as a gold coin using a pygame ellipse with horizontal line highlight, or as a mushroom shape using overlapping rectangles.

**Rationale**:
- A coin is the most instantly recognizable Mario Bros. item and matches "FR-003: coin, mushroom, star, or power-up."
- A coin can be drawn with simple pygame primitives (ellipse + line) — no sprite loading needed.
- A mushroom is also acceptable but requires more complex shape composition.
- Default to coin; mushroom can be a future variation.

**Coin rendering (Pygame)**:
```python
# Gold coin: ellipse with inner highlight line
coin_rect = pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size)
pygame.draw.ellipse(screen, COIN_GOLD, coin_rect)
pygame.draw.line(screen, COIN_WHITE, 
    (x * cell_size + 3, y * cell_size + 5),
    (x * cell_size + cell_size - 3, y * cell_size + 5),
    2)
```

**Coin rendering (Terminal)**:
```
Use '◉' or '◆' character in COIN_GOLD color instead of current '*'
```

---

## Decision 6: Terminal Theme Color Mapping

**Decision**: Use ANSI 256-color mode for the terminal Mario theme, mapping palette colors to the nearest available terminal colors.

**Rationale**:
- Modern terminals support 256 colors via `\033[38;5;NNm` (foreground) and `\033[48;5;NNm` (background).
- The existing `TerminalRenderer` already uses ANSI color codes (`\033[92m` = bright green, etc.).
- 256-color mode provides a much better visual experience than standard 16 colors.
- Falls back gracefully if the terminal doesn't support 256 colors (ANSI codes are ignored).

**Color mapping**:
| Palette Color | 256-color Index | ANSI Code |
|---|---|---|
| BG_BLUE | 21 (background) | `\033[48;5;21m` |
| MARIO_RED | 196 (foreground) | `\033[38;5;196m` |
| OVERALL_BLUE | 33 (foreground) | `\033[38;5;33m` |
| COIN_GOLD | 226 (foreground) | `\033[38;5;226m` |
| WHITE | 231 (foreground) | `\033[38;5;231m` |

---

## Decision 7: Default Snake Head Visual Enhancement

**Decision**: Add minimal face detail to the snake head when Mario theme is active — two small pixel "eyes" using the skin-tone color.

**Rationale**:
- User Story 2 requires "snake head incorporates a Mario character element."
- Simple pixel eyes are the minimal viable Mario-like head detail.
- No complex sprite needed — just 2-3 additional pixel rects.

**Implementation**:
```python
# Draw 2 small square "eyes" on the snake head
eye_size = cell_size // 5
pygame.draw.rect(screen, SKIN_TONE, eye1_rect)
pygame.draw.rect(screen, SKIN_TONE, eye2_rect)
```

---

## Summary of Research Findings

| # | Decision | Choice | Rationale |
|---|----------|--------|-----------|
| 1 | Theme config approach | `ThemeConfig` dataclass + palette dict | Minimal abstraction, constitution-compliant |
| 2 | Mario color palette | NES World 1-1-inspired RGB values | Authentic look, no external assets |
| 3 | Toggle mechanism | Keyboard `T` key, boolean flag | Simple, works during gameplay |
| 4 | Renderer strategy | Modify existing renderers with theme parameter | YAGNI, no new patterns needed |
| 5 | Food as coin | Gold ellipse with highlight line | Most recognizable Mario item, pygame primitive |
| 6 | Terminal colors | ANSI 256-color mapping | Better visuals, graceful fallback |
| 7 | Snake head detail | Two pixel "eyes" on head | Minimal Mario character element |
