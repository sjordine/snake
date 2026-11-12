"""Unit tests for theme configuration dataclass."""

import dataclasses
from dataclasses import replace

from src.render.themes.config import ThemeConfig, DEFAULT_THEME, MARIO_THEME


class TestThemeConfig:
    """Validate ThemeConfig and its pre-built singletons."""

    def _make_fresh_config(self) -> ThemeConfig:
        """Create a fresh ThemeConfig instance for testing without mutating singletons."""
        return ThemeConfig(
            name="test",
            bg_color=(0, 0, 0),
            snake_body_color=(0, 0, 0),
            snake_body_inner=(0, 0, 0),
            snake_head_color=(0, 0, 0),
            snake_head_detail=None,
            food_color=(0, 0, 0),
            food_detail=None,
            hud_text_color=(0, 0, 0),
            game_over_text_color=(0, 0, 0),
            game_over_bg_color=(0, 0, 0, 180),
            grid_line_color=(0, 0, 0),
            terminal_fg_override=None,
        )

    def test_frozen_dataclass(self) -> None:
        """ThemeConfig is immutable — direct attribute assignment raises FrozenInstanceError."""
        fresh = self._make_fresh_config()
        try:
            fresh.name = "bar"
            assert False, "ThemeConfig should be frozen"
        except dataclasses.FrozenInstanceError:
            pass  # Expected

    def test_frozen_allow_replace(self) -> None:
        """Frozen dataclass supports dataclasses.replace()."""
        fresh = self._make_fresh_config()
        updated = replace(fresh, name="updated")
        assert updated.name == "updated"
        assert fresh.name == "test"

    def test_default_theme_name(self) -> None:
        assert DEFAULT_THEME.name == "Default"

    def test_mario_theme_name(self) -> None:
        assert MARIO_THEME.name == "Mario Bros."

    def test_default_bg_color(self) -> None:
        assert DEFAULT_THEME.bg_color == (20, 20, 20)

    def test_mario_bg_color(self) -> None:
        assert MARIO_THEME.bg_color == (42, 42, 224)

    def test_default_snake_head_is_green(self) -> None:
        assert DEFAULT_THEME.snake_head_color == (0, 200, 0)

    def test_mario_snake_head_is_red(self) -> None:
        assert MARIO_THEME.snake_head_color == (235, 33, 33)

    def test_default_snake_head_detail_is_none(self) -> None:
        assert DEFAULT_THEME.snake_head_detail is None

    def test_mario_snake_head_detail_is_skin_tone(self) -> None:
        assert MARIO_THEME.snake_head_detail == (255, 180, 120)

    def test_mario_food_detail_is_white(self) -> None:
        assert MARIO_THEME.food_detail == (255, 255, 255)

    def test_default_food_color(self) -> None:
        assert DEFAULT_THEME.food_color == (220, 50, 50)

    def test_mario_food_color_is_gold(self) -> None:
        assert MARIO_THEME.food_color == (255, 215, 0)

    def test_game_over_bg_is_4_tuple(self) -> None:
        assert len(DEFAULT_THEME.game_over_bg_color) == 4
        assert len(MARIO_THEME.game_over_bg_color) == 4

    def test_game_over_bg_alpha(self) -> None:
        assert DEFAULT_THEME.game_over_bg_color[3] == 180
        assert MARIO_THEME.game_over_bg_color[3] == 180

    def test_terminal_fg_override_none_for_default(self) -> None:
        assert DEFAULT_THEME.terminal_fg_override is None

    def test_terminal_fg_override_set_for_mario(self) -> None:
        assert MARIO_THEME.terminal_fg_override is not None
        assert isinstance(MARIO_THEME.terminal_fg_override, dict)
        for key in ("bg", "snake_head", "snake_body", "food", "hud", "game_over", "grid"):
            assert key in MARIO_THEME.terminal_fg_override
