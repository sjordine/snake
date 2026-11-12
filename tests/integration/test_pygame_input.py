"""Integration tests for Pygame input adapter.

Verifies that PygameInput converts pygame KEYDOWN events
to Direction enum values correctly.
"""

import pytest
import pygame

from src.game.snake import UP, DOWN, LEFT, RIGHT
from src.input.pygame_input import PygameInput


class TestPygameInput:
    """T035 — Pygame input integration tests."""

    def setup_method(self) -> None:
        """Initialize Pygame before each test."""
        pygame.init()

    def teardown_method(self) -> None:
        """Quit Pygame after each test."""
        pygame.quit()

    def _post_key(self, key: int) -> None:
        """Post a KEYDOWN event for the given pygame key code."""
        event = pygame.event.Event(pygame.KEYDOWN, key=key)
        pygame.event.post(event)

    def _clear_events(self) -> None:
        """Clear all pending pygame events."""
        pygame.event.get()

    def test_arrow_up_maps_to_up(self) -> None:
        """Arrow Up key maps to UP direction tuple."""
        input_adapter = PygameInput()
        self._post_key(pygame.K_UP)
        result = input_adapter.poll_events()
        assert result == UP
        self._clear_events()

    def test_arrow_down_maps_to_down(self) -> None:
        """Arrow Down key maps to DOWN direction tuple."""
        input_adapter = PygameInput()
        self._post_key(pygame.K_DOWN)
        result = input_adapter.poll_events()
        assert result == DOWN
        self._clear_events()

    def test_arrow_left_maps_to_left(self) -> None:
        """Arrow Left key maps to LEFT direction tuple."""
        input_adapter = PygameInput()
        self._post_key(pygame.K_LEFT)
        result = input_adapter.poll_events()
        assert result == LEFT
        self._clear_events()

    def test_arrow_right_maps_to_right(self) -> None:
        """Arrow Right key maps to RIGHT direction tuple."""
        input_adapter = PygameInput()
        self._post_key(pygame.K_RIGHT)
        result = input_adapter.poll_events()
        assert result == RIGHT
        self._clear_events()

    def test_returns_none_with_no_events(self) -> None:
        """poll_events() returns None when no events are pending."""
        input_adapter = PygameInput()
        result = input_adapter.poll_events()
        assert result is None

    def test_only_arrow_keys_map_to_directions(self) -> None:
        """Non-arrow keys should not return a direction tuple."""
        input_adapter = PygameInput()
        # Post a W key (not an arrow key)
        self._post_key(pygame.K_w)
        result = input_adapter.poll_events()
        # Should not be a direction tuple
        assert result not in [UP, DOWN, LEFT, RIGHT]
        self._clear_events()

    def test_single_direction_per_call(self) -> None:
        """poll_events() returns at most one direction per call (no input stacking)."""
        input_adapter = PygameInput()
        # Post two UP keys — only the first should be returned
        self._post_key(pygame.K_UP)
        self._post_key(pygame.K_UP)

        first = input_adapter.poll_events()
        assert first == UP

        # Second call returns None: all events were consumed in first call
        second = input_adapter.poll_events()
        assert second is None  # no stacking

    def test_enter_returns_restart(self) -> None:
        """Enter key returns 'r' for restart."""
        input_adapter = PygameInput()
        self._post_key(pygame.K_RETURN)
        result = input_adapter.poll_events()
        assert result == "r"
        assert input_adapter.is_restart(result) is True
        self._clear_events()

    def test_q_returns_quit(self) -> None:
        """Q key returns 'q' for quit."""
        input_adapter = PygameInput()
        self._post_key(pygame.K_q)
        result = input_adapter.poll_events()
        assert result == "q"
        assert input_adapter.is_quit(result) is True
        self._clear_events()
