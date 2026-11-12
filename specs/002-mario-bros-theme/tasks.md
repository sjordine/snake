---
description: "Task list for Mario Bros. visual theme implementation"
---

# Tasks: Mario Bros. Visual Theme

**Branch**: `002-mario-bros-theme` | **Date**: 2026-11-12 | **Spec**: [spec.md](../002-mario-bros-theme/spec.md)

**Prerequisites**: plan.md (complete), spec.md (complete), research.md (complete), data-model.md (complete), contracts/theme-api.md (complete), quickstart.md (complete)

**Tests**: Only test tasks for theme infrastructure (palette, config) — renderer theme tests will be validated via quickstart.md scenarios and manual play-testing, as the feature spec does not explicitly request TDD test tasks.

## Format

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Maps to user story (US1, US2, US3 from spec.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create new package structure for theme modules.

- [x] T001 Create `src/render/themes/` directory and `__init__.py` that exports `DEFAULT_THEME`, `MARIO_THEME` from config module

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Theme infrastructure that MUST be complete before any user story can be implemented. All theme color data, configuration, and palette lookups must exist before renderers can consume them.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T002 Implement `src/render/themes/palette.py` — module-level `PALETTE` dict with `"default"` and `"mario"` color maps; each inner dict has required keys: `bg`, `snake_body`, `snake_head`, `food`, `hud`, `game_over_text`, `game_over_bg`, `grid`; all values are RGB 3-tuples (0–255)
- [ ] T003 Implement `src/render/themes/config.py` — `ThemeConfig` frozen dataclass with fields: `name` (str, non-empty), `bg_color` (3-tuple RGB), `snake_body_color` (3-tuple RGB), `snake_body_inner` (3-tuple RGB), `snake_head_color` (3-tuple RGB), `snake_head_detail` (optional 3-tuple RGB or None), `food_color` (3-tuple RGB), `food_detail` (optional 3-tuple RGB or None), `hud_text_color` (3-tuple RGB), `game_over_text_color` (3-tuple RGB), `game_over_bg_color` (4-tuple RGBA, each 0–255), `grid_line_color` (3-tuple RGB), `terminal_fg_override` (optional dict str→int); add `DEFAULT_THEME` and `MARIO_THEME` module-level singletons with values per data-model.md
- [ ] T004 [P] Add unit tests for palette in `tests/unit/test_palette.py` — verify both `"default"` and `"mario"` keys exist, all required color keys present per theme, all RGB values 0–255, dictionary is not mutated after import
- [ ] T005 [P] Add unit tests for theme config in `tests/unit/test_theme_config.py` — verify `ThemeConfig` is frozen (immutable), `DEFAULT_THEME.name == "Default"`, `MARIO_THEME.name == "Mario Bros."`, all color tuples valid, `game_over_bg_color` is 4-tuple, `snake_head_detail` and `food_detail` are non-None for Mario theme

**Checkpoint**: Foundation ready — theme data, config, and palette are defined and validated. User story implementation can now begin.

---

## Phase 3: User Story 1 — Play Snake with Mario Bros. Visual Aesthetics (Priority: P1) 🎯 MVP

**Goal**: Player experiences Snake with Mario Bros. visual styling — blue sky background, red/blue block-style snake, coin food, pixel-style HUD. Delivers the core value proposition.

**Independent Test**: Launch game with Mario theme active (`T` key), background is sky blue, snake body is overall blue with red head, food is gold coin with white highlight line, score text is white. All gameplay works identically.

### Implementation for User Story 1

- [ ] T006 [US1] Modify `src/render/themes/__init__.py` — ensure it exports `DEFAULT_THEME` and `MARIO_THEME` from config module (completes T001)
- [ ] T007 [US1] Modify `src/render/pygame_renderer.py` — add `theme_config: ThemeConfig | None = None` parameter to `__init__`; store as `self._theme_config` defaulting to `DEFAULT_THEME` if `None`; import `ThemeConfig` from `..themes.config`; use `self._theme_config` instead of hardcoded `COLOR_*` constants in all color references: `bg_color` for background fill, `grid_line_color` for grid, `snake_body_color`/`snake_body_inner` for snake body segments, `snake_head_color` for head, `food_color` for food fill, `food_detail` for food highlight, `hud_text_color` for score text, `game_over_text_color` for game-over text, `game_over_bg_color` for game-over overlay
- [ ] T008 [US1] Implement coin rendering in `src/render/pygame_renderer.py` — replace the existing food rendering (currently a red square/circle) with coin drawing: draw a gold ellipse using `self._theme_config.food_color` that fills the cell rect; if `self._theme_config.food_detail` is not None, draw a horizontal white highlight line across the center at 1/3 cell height using `self._theme_config.food_detail`; this renders identically regardless of theme (default food falls back to a gold-ish circle; Mario food is a gold coin)
- [ ] T009 [US1] Modify `src/render/terminal_renderer.py` — add `theme_config: ThemeConfig | None = None` parameter to `__init__`; store as `self._theme_config` defaulting to `DEFAULT_THEME`; import `ThemeConfig` from `..themes.config`; replace hardcoded color constants with theme-aware lookups via `self._theme_config` for background, snake body, snake head, food, HUD text, and game-over colors
- [ ] T010 [US1] Modify `src/render/terminal_renderer.py` — set `CH_FOOD = "◉"` (circle-dia character) when Mario theme active vs `*` for default; use terminal color overrides from `self._theme_config.terminal_fg_override` when `self.color` is True
- [ ] T011 [US1] Modify `src/main.py` — import `DEFAULT_THEME` from `src.render.themes.config`; create `PygameRenderer(cell_size=CELL_SIZE, theme_config=DEFAULT_THEME)` instead of `PygameRenderer(cell_size=CELL_SIZE)`; create `TerminalRenderer(color=True, theme_config=DEFAULT_THEME)` when terminal renderer selected; pass `theme_config=DEFAULT_THEME` to both renderer constructors

**Checkpoint**: At this point, User Story 1 is fully functional. Player can launch the game and see Mario-themed visuals (once the toggle is wired in Phase 4, or by modifying main.py to use `MARIO_THEME` directly for a one-time test). Background is sky blue, snake is red/blue, food is a gold coin, HUD is white text on blue.

---

## Phase 4: User Story 2 — Recognize Mario Bros. Thematic Elements (Priority: P2)

**Goal**: Snake head has Mario character element (pixelated face/eyes), food is unmistakably a coin, game-over screen uses Mario styling. Elevates from recoloring to genuine Mario experience.

**Independent Test**: Show Mario-themed game to a Mario fan — they should identify red head with face detail, gold coin food, and Mario-styled game-over text.

### Implementation for User Story 2

- [ ] T012 [US2] Enhance snake head rendering in `src/render/pygame_renderer.py` — in the snake head drawing code, if `self._theme_config.snake_head_detail` is not None and `cell_size >= 10`, draw two small square "eyes" using `self._theme_config.snake_head_detail` color: left eye at `(pos.x * cell_size + cell_size // 4 - eye_size // 2, pos.y * cell_size + cell_size // 4 - eye_size // 2)`, right eye at `(pos.x * cell_size + 3 * cell_size // 4 - eye_size // 2, pos.y * cell_size + cell_size // 4 - eye_size // 2)`, where `eye_size = max(1, cell_size // 5)`; eyes are skin-tone `(255, 180, 120)` on Mario red `(235, 33, 33)` head
- [ ] T013 [US2] Enhance game-over rendering in `src/render/pygame_renderer.py` — ensure game-over text uses `self._theme_config.game_over_text_color` (Mario red for Mario theme, gold for default) and game-over background uses `self._theme_config.game_over_bg_color` (RGBA `(0, 0, 0, 180)` for both themes); text reads "GAME OVER" in the existing font
- [ ] T014 [US2] Enhance terminal renderer snake head — while terminal already uses theme colors, ensure snake head character (`@`) appears in the snake head color from `self._theme_config.snake_head_color` (red for Mario) via the ANSI override map `self._theme_config.terminal_fg_override.get("snake_head")` when color mode is enabled
- [ ] T015 [US2] Add `render_snake_head` helper method in `src/render/pygame_renderer.py` — extract snake head rendering (with optional eye detail) into a reusable method that takes `screen`, `pos`, `cell_size`, and reads colors from `self._theme_config`; the existing snake rendering loop should call this method instead of drawing the head inline

**Checkpoint**: At this point, User Stories 1 AND 2 are both functional. The snake has pixel eyes on its head, the food is a coin, and the game-over screen uses Mario colors. A Mario fan would recognize the theme elements.

---

## Phase 5: User Story 3 — Configure Theme Toggle (Priority: P3)

**Goal**: Player can toggle Mario theme on/off during gameplay with the `T` key, with immediate visual update and no game state corruption.

**Independent Test**: Start game, press `T` to activate Mario theme (visuals change in ≤1 frame), press `T` again to revert to default (visuals revert instantly), game continues playing through both toggles without crash or state loss.

### Implementation for User Story 3

- [ ] T016 [US3] Add `toggle_theme()` method to `src/render/pygame_renderer.py` — swap `self._theme_config` between `DEFAULT_THEME` and `MARIO_THEME` by checking current theme name and switching to the other; import both themes from `..themes.config`; method returns `None`; after toggle, next `render()` call uses new theme's colors — no partial frame or glitch
- [ ] T017 [US3] Add `toggle_theme()` method to `src/render/terminal_renderer.py` — same semantics as PygameRenderer: swap `self._theme_config` between `DEFAULT_THEME` and `MARIO_THEME`; method returns `None`
- [ ] T018 [US3] Modify `src/main.py` — in the Pygame event loop (where `pygame.KEYDOWN` events for `pygame.K_q`/`pygame.K_ESCAPE` and `pygame.K_r` are handled), add handling for `pygame.K_t`: when pressed, call `pygame_renderer.toggle_theme()`; ensure `K_t` does not conflict with existing bindings (`W`/`↑`/`A`/`↓`/`S`/`↓`/`D`/`→` for direction, `Q`/`Esc` for quit, `R` for restart)
- [ ] T019 [US3] Modify `src/main.py` — in the terminal input polling (where `poll_terminal_key()` is called for direction keys), add handling for `"t"`/`"T"`: when pressed, call `terminal_renderer.toggle_theme()`; ensure `T` does not conflict with `W`/`A`/`S`/`D`/`Q`/`R`
- [ ] T020 [US3] Modify `src/main.py` — add `--theme` CLI argument with choices `["default", "mario"]` and default `"default"`; when `--theme=mario` is passed, instantiate the renderer with `theme_config=MARIO_THEME` instead of `DEFAULT_THEME`; this supports static theme selection at launch (complements the runtime `T` toggle)

**Checkpoint**: All three user stories are complete. Theme toggle works at runtime via `T` key, theme can be set at launch via `--theme=mario`, visual changes happen within 1 frame, and no game state is corrupted.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validation, cleanup, and verification against success criteria.

- [ ] T021 Run all existing unit tests (`pytest tests/unit/`) to confirm no regression in game core (`game.core`, `snake`, `food`, `collision`, `grid`) — these modules are unchanged per constitution Principle I
- [ ] T022 Run all existing integration tests (`pytest tests/integration/`) to confirm Pygame renderer and input adapters still function correctly with the new theme parameter
- [ ] T023 Execute quickstart.md validation scenarios manually (at minimum: Scenario 1 default theme smoke test, Scenario 2 Mario toggle, Scenario 6 game-over screen)
- [ ] T024 Verify performance: start game in Pygame renderer, open with Pygame debug, confirm each frame completes in ≤16ms at 60fps (theme color lookups from dataclass fields add negligible overhead vs. hardcoded constants)
- [ ] T025 Verify terminal renderer with `--renderer=terminal` and `--theme=mario` — confirm 256-color ANSI codes render correctly in a modern terminal (macOS Terminal.app or iTerm2); verify graceful fallback to standard ANSI if 256-color unsupported

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — **BLOCKS** all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - Stories can then proceed sequentially in priority order (P1 → P2 → P3) or in parallel if team capacity allows
- **Polish (Phase 6)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) — implements base theme color application to both renderers; MVP deliverable
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) — depends on US1 for renderer color infrastructure, but adds head detail and game-over styling
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) — depends on US1 for renderer theme parameter infrastructure, adds toggle mechanism and wiring

### Within Each User Story

- Models/config before renderers
- Renderer changes before main.py wiring
- Story complete before moving to next priority

### Parallel Opportunities

- T004 and T005 (Phase 2 tests) can run in parallel — different files (`test_palette.py` vs `test_theme_config.py`)
- Once Foundational phase completes, US1 (Phase 3) can begin independently
- US2 can begin after US1 is stable (it enhances renderer methods US1 modifies)
- US3 can begin after US1 is stable (it uses theme parameter infrastructure US1 establishes)

---

## Parallel Example: Foundational Phase

```bash
# Launch palette tests and config tests together:
Task: "Add unit tests for palette in tests/unit/test_palette.py"
Task: "Add unit tests for theme config in tests/unit/test_theme_config.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Launch game, toggle to Mario theme, verify sky blue background, red/blue snake, gold coin food, white HUD text
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → MVP! (Mario visuals work, toggle pending)
3. Add User Story 2 → Test independently → Mario theme is recognizable (head detail + game-over styling)
4. Add User Story 3 → Test independently → Theme toggle works at runtime
5. Polish → Regression tests pass, performance validated

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (renderer color application)
   - (Developer B: waits for US1 to stabilize before starting US2)
   - (Developer C: waits for US1 to stabilize before starting US3)
3. Stories complete and integrate — theme fully functional

---

## Notes

- [P] tasks = different files, no dependencies
- Story labels map tasks to specific user stories for traceability
- Each user story is independently completable and testable
- Commit after each task or logical group
- Game core (`game.core`, `snake.py`, `food.py`, `collision.py`, `grid.py`) is **UNCHANGED** per constitution Principle I — no tasks touch these files
- All theme logic lives in `src/render/themes/` and renderer modifications only — no game state mutation
- Total task count: **25** tasks across 6 phases
- Tasks T004/T005 are test tasks added for theme infrastructure validation (palette + config data integrity)
