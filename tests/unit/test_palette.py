"""Unit tests for theme color palette."""

from src.render.themes.palette import PALETTE, _REQUIRED_KEYS


class TestPalette:
    """Validate the PALETTE module-level constant."""

    def test_default_key_exists(self) -> None:
        assert "default" in PALETTE

    def test_mario_key_exists(self) -> None:
        assert "mario" in PALETTE

    def test_required_keys_present(self) -> None:
        for theme_name, colors in PALETTE.items():
            for key in _REQUIRED_KEYS:
                assert key in colors, f"Missing key {key!r} in theme {theme_name}"

    def test_all_rgb_values_in_range(self) -> None:
        for theme_name, colors in PALETTE.items():
            for color_name, rgb in colors.items():
                assert len(rgb) == 3, f"{theme_name}/{color_name} is not a 3-tuple"
                for component in rgb:
                    assert 0 <= component <= 255, (
                        f"{theme_name}/{color_name} component {component} out of range"
                    )

    def test_palette_not_mutated_at_import(self) -> None:
        """PALETTE is a stable dict — no KeyError on re-import."""
        assert len(PALETTE) == 2
        assert len(PALETTE["default"]) >= len(_REQUIRED_KEYS)
        assert len(PALETTE["mario"]) >= len(_REQUIRED_KEYS)
