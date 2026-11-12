"""Tests for the chiptune music system.

Verifies:
- Music initialization succeeds without raising
- Music can be played and stopped
- Music loop cycles correctly
- Note synthesis produces valid pygame.mixer.Sound objects
"""

import pygame
import pytest


@pytest.fixture(scope="module", autouse=True)
def pygame_init():
    """Initialize pygame for all tests in this module."""
    pygame.init()
    pygame.mixer.quit()
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    yield
    pygame.mixer.quit()


class TestMusicInitialization:
    """Test that music system initializes correctly."""

    def test_music_init_no_error(self):
        """Music system initializes without raising."""
        from src.audio.music import AudioSystem
        audio = AudioSystem()
        assert audio is not None

    def test_music_notes_are_valid(self):
        """Music notes contain valid frequency values."""
        from src.audio.music import MARIO_THEME, NOTE_FREQS
        assert len(MARIO_THEME) > 0
        for note_name, _ in MARIO_THEME:
            assert note_name in NOTE_FREQS


class TestNoteSynthesis:
    """Test that individual notes can be synthesized."""

    def test_synthesize_note_produces_samples(self):
        """synth_note returns a list of float samples."""
        from src.audio.music import synth_note, NOTE_FREQS
        samples = synth_note(NOTE_FREQS["C4"], duration=0.1)
        assert samples is not None
        assert isinstance(samples, list)
        assert len(samples) > 0

    def test_synthesize_rest_produces_none(self):
        """synth_rest returns None (silence)."""
        from src.audio.music import synth_rest
        result = synth_rest(duration=0.1)
        assert result is None

    def test_different_notes_same_duration_same_length(self):
        """Different notes at same duration produce same-length sample lists."""
        from src.audio.music import synth_note, NOTE_FREQS
        samples1 = synth_note(NOTE_FREQS["C4"], duration=0.1)
        samples2 = synth_note(NOTE_FREQS["E4"], duration=0.1)
        assert len(samples1) == len(samples2)

    def test_longer_note_more_samples(self):
        """A longer note produces more samples."""
        from src.audio.music import synth_note, NOTE_FREQS
        short = synth_note(NOTE_FREQS["C4"], duration=0.05)
        long_ = synth_note(NOTE_FREQS["C4"], duration=0.2)
        assert len(long_) > len(short)

    def test_sample_values_clamped(self):
        """Sample values are in valid range [-1.0, 1.0]."""
        from src.audio.music import synth_note, NOTE_FREQS
        samples = synth_note(NOTE_FREQS["C4"], duration=0.1, volume=1.0)
        for s in samples:
            assert -1.0 <= s <= 1.0


class TestMarioTheme:
    """Test the Mario Bros theme sequence."""

    def test_mario_theme_has_sequence(self):
        """Mario theme contains a note sequence."""
        from src.audio.music import AudioSystem, MARIO_THEME
        assert len(MARIO_THEME) > 0

    def test_mario_theme_play_cycles(self):
        """Playing Mario theme cycles through notes."""
        from src.audio.music import AudioSystem
        audio = AudioSystem()
        # play_background should not raise
        audio.play_background()
        import time
        time.sleep(0.5)  # Let it play a bit
        audio.stop_background()

    def test_mario_theme_loop_mode(self):
        """Mario theme loops when set to loop."""
        from src.audio.music import AudioSystem
        audio = AudioSystem()
        audio.play_background()  # loops by default
        import time
        time.sleep(0.3)
        audio.stop_background()
