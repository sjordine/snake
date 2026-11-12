"""Chiptune music and sound effects for Snake.

Produces retro Mario Bros-style melodies and sound effects
using pure sine-wave synthesis with pygame.mixer.

No external audio files needed — everything is generated programmatically.

Design decisions:
- Mario Bros-style 8-bit theme using pentatonic scale notes
- Pure sine waves with square-wave flavor via harmonics
- Sound effects: eating (ascending chime), game over (descending crash)
- Background music loops continuously during gameplay
- Muted by default for users without speakers
"""

import math
import struct
from dataclasses import dataclass
from enum import Enum, auto

import pygame

# ---------------------------------------------------------------------------
# Note frequencies (scientific pitch notation)
# Includes chromatic notes (sharps/flats) for the authentic Mario theme.
# ---------------------------------------------------------------------------

NOTE_FREQS: dict[str, float] = {
    "C4": 261.63,
    "C#4": 277.18,
    "D4": 293.66,
    "D#4": 311.13,
    "E4": 329.63,
    "F4": 349.23,
    "F#4": 369.99,
    "G4": 392.00,
    "G#4": 415.30,
    "A4": 440.00,
    "A#4": 466.16,  # enharmonic to Bb4
    "B4": 493.88,
    "C5": 523.25,
    "C#5": 554.37,
    "D5": 587.33,
    "D#5": 622.25,
    "E5": 659.25,
    "F5": 698.46,
    "G5": 783.99,
    "A5": 880.00,
    "rest": 0,  # silence
}

# ---------------------------------------------------------------------------
# Super Mario Bros. Ground Theme (Koji Kondo, 1985)
# ---------------------------------------------------------------------------
# Authentic transcription of the iconic main theme melody.
# Tempo: 100 BPM, time signature 4/4.
# Each tuple: (note, duration_in_beats)

MARIO_THEME: list[tuple[str, float]] = [
    # ── Section A — iconic opening melody (plays twice) ──
    # Measure 1
    ("E5", 0.5), ("E5", 0.5), ("rest", 0.5), ("E5", 0.5),
    ("rest", 0.5), ("C5", 0.5), ("E5", 0.5), ("rest", 0.5),
    ("G5", 0.5), ("rest", 0.5), ("G5", 1.0),

    # Measure 2
    ("C5", 0.5), ("E5", 0.5), ("G5", 1.0),
    ("A5", 1.0), ("A4", 1.0), ("A5", 1.0),

    # Measure 3
    ("G5", 0.5), ("E5", 0.5), ("C5", 0.5), ("D5", 0.5), ("B4", 1.0),
    ("A4", 0.5), ("C5", 0.5), ("D5", 1.0),

    # Measure 4
    ("E5", 0.5), ("D5", 0.5), ("D5", 1.0),
    ("E5", 0.5), ("D5", 0.5), ("C5", 1.0),
    ("B4", 0.5), ("C5", 0.5), ("C5", 1.0),

    # ── Section B — bridge (plays twice) ──
    # Measure 5
    ("A4", 0.5), ("A4", 0.5), ("C5", 1.0),
    ("E5", 0.5), ("D5", 0.5), ("C5", 0.5), ("B4", 0.5),
    ("A4", 0.5), ("A4", 0.5), ("C5", 0.5), ("D5", 0.5),

    # Measure 6
    ("E5", 0.5), ("D5", 0.5), ("D5", 1.0),
    ("E5", 0.5), ("D5", 0.5), ("C5", 1.0),
    ("B4", 0.5), ("C5", 0.5), ("C5", 1.0),
    ("A4", 0.5), ("A4", 0.5), ("A4", 1.0),

    # ── Section C — chromatic bridge (F♯, G♯) ──
    # Measure 7
    ("G#4", 0.5), ("F#4", 0.5), ("F4", 0.5), ("D4", 0.5), ("E4", 0.5),
    ("G4", 0.5), ("A4", 0.5), ("C5", 0.5),
    ("A4", 0.5), ("C5", 0.5), ("D5", 0.5),

    # Measure 8
    ("G#4", 0.5), ("F#4", 0.5), ("F4", 0.5), ("D4", 0.5), ("E4", 0.5),
    ("G4", 0.5), ("A4", 0.5), ("C5", 0.5),
    ("A4", 0.5), ("C5", 0.5), ("D5", 0.5),

    # ── Section D — resolution (descending) ──
    # Measure 9
    ("D#5", 0.5), ("D5", 0.5), ("C5", 1.0),
    ("C5", 0.5), ("C5", 0.5), ("C5", 1.0),
    ("C5", 0.5), ("D5", 0.5), ("E5", 0.5), ("C5", 0.5), ("A4", 0.5), ("G4", 0.5),

    # ── Section E — final phrase ──
    # Measure 10
    ("E5", 0.5), ("E5", 0.5), ("E5", 0.5),
    ("C5", 0.5), ("E5", 0.5), ("G5", 0.5),
    ("G5", 1.0),

    # Measure 11
    ("C5", 0.5), ("G4", 0.5), ("E4", 0.5),
    ("A4", 0.5), ("B4", 0.5), ("A4", 0.5),
    ("G4", 0.5), ("E5", 0.5), ("G5", 0.5), ("A#4", 0.5),

    # Measure 12
    ("F5", 0.5), ("G5", 0.5), ("E5", 0.5), ("C5", 0.5), ("D5", 0.5),
    ("B4", 0.5),
]

# Beat duration at 100 bpm — slow enough that beat-based
# note length differences are clearly perceptible.
BPM = 100
BEAT_DURATION = 60.0 / BPM  # 0.6 s

# ---------------------------------------------------------------------------
# Sound effects
# ---------------------------------------------------------------------------

# Eat food: ascending arpeggio (C4, E4, G4, C5)
EAT_NOTES: list[tuple[str, float]] = [
    ("C4", 0.08),
    ("E4", 0.08),
    ("G4", 0.08),
    ("C5", 0.12),
]

# Game over: descending crash (B4, A4, G4, E4, C4)
DEATH_NOTES: list[tuple[str, float]] = [
    ("B4", 0.15),
    ("A4", 0.15),
    ("G4", 0.2),
    ("E4", 0.2),
    ("C4", 0.3),
]


# ---------------------------------------------------------------------------
# Note synthesizer
# ---------------------------------------------------------------------------

def synth_note(
    frequency: float,
    duration: float,
    volume: float = 0.3,
    sample_rate: int = 44100,
) -> list[float] | None:
    """Synthesize a single note as raw float samples.

    Uses a square wave with harmonics for a chiptune/Mario Bros flavor,
    with a soft attack/release to avoid clicking.

    Args:
        frequency: Note frequency in Hz (0 for silence).
        duration: Note duration in seconds.
        volume: Amplitude (0.0 — 1.0).
        sample_rate: Audio sample rate (default 44100).

    Returns:
        A list of raw float samples, or None if frequency is 0 (rest).
    """
    if frequency <= 0:
        return None

    num_samples = int(sample_rate * duration)
    if num_samples == 0:
        return None

    # Build square wave with harmonics (Mario Bros 8-bit flavor)
    samples: list[float] = []
    for i in range(num_samples):
        t = i / sample_rate
        phase = 2.0 * math.pi * frequency * t

        # Fundamental (square wave approximation using tanh)
        fundamental = math.tanh(math.sin(phase)) * 0.7

        # 3rd harmonic (thin, buzzy character)
        harmonic3 = math.tanh(math.sin(3.0 * phase)) * 0.15

        # 5th harmonic (extra brightness)
        harmonic5 = math.tanh(math.sin(5.0 * phase)) * 0.08

        sample = (fundamental + harmonic3 + harmonic5) * volume

        # Envelope: tight attack & release for crisp chiptune articulation
        # Attack/release are kept short relative to beat duration so note
        # length differences remain perceptible at the given tempo.
        attack = min(i / (sample_rate * 0.002), 1.0)
        release_start = max(num_samples - int(sample_rate * 0.004), 0)
        release = 1.0
        if i > release_start:
            release = max(0.0, (num_samples - i) / (sample_rate * 0.004))

        sample *= attack * release
        samples.append(sample)

    return samples


def synth_rest(duration: float, sample_rate: int = 44100) -> None:
    """Return None to represent silence (no sound to play)."""
    return None


# ---------------------------------------------------------------------------
# Audio system
# ---------------------------------------------------------------------------

class MusicState(Enum):
    """State of the music system."""

    IDLE = auto()
    PLAYING = auto()
    STOPPED = auto()
    MUTED = auto()


@dataclass
class AudioSystem:
    """Manages background music and sound effects.

    Contract:
    - play_background() starts the looping Mario theme.
    - stop_background() stops the looping theme.
    - play_sfx(name) plays a sound effect (eat, death).
    - mute() / unmute() control global volume.

    All audio is generated programmatically — no external files.
    """

    sample_rate: int = 44100
    volume: float = 0.3
    muted: bool = False
    _state: MusicState = MusicState.IDLE

    # Cached sound objects (pre-computed for performance)
    _eat_sound: pygame.mixer.Sound | None = None
    _death_sound: pygame.mixer.Sound | None = None

    @property
    def state(self) -> MusicState:
        """Current music state."""
        return self._state

    @staticmethod
    def _samples_to_sound(samples: list[float]) -> pygame.mixer.Sound:
        """Convert raw float samples to a pygame.mixer.Sound (mono, 16-bit).

        Args:
            samples: List of float samples in range [-1.0, 1.0].

        Returns:
            A pygame.mixer.Sound object.
        """
        import array
        int_samples = struct.pack(
            f"<{'h' * len(samples)}",
            *(int(32767 * max(-1.0, min(1.0, s))) for s in samples),
        )
        return pygame.mixer.Sound(buffer=int_samples)

    def play_background(self) -> None:
        """Start looping the Mario Bros theme.

        Pre-computes all notes, chains them into raw PCM data,
        and plays it on a loop channel.
        """
        if self.muted:
            self._state = MusicState.MUTED
            return

        # Build the full theme as one continuous sound buffer
        raw_samples: list[float] = []
        staccato_gap = int(self.sample_rate * 0.01)  # 10ms silence between notes
        for i, (note_name, beats) in enumerate(MARIO_THEME):
            freq = NOTE_FREQS.get(note_name, 0)
            duration = beats * BEAT_DURATION
            num_samples = int(self.sample_rate * duration)

            if note_name == "rest":
                # Rests produce silence of the correct duration
                raw_samples.extend([0.0] * num_samples)
            else:
                note_samples = synth_note(freq, duration, self.volume, self.sample_rate)
                if note_samples is not None:
                    # Insert staccato gap between consecutive non-rest notes
                    if i > 0 and MARIO_THEME[i - 1][0] != "rest":
                        raw_samples.extend([0.0] * staccato_gap)
                    raw_samples.extend(note_samples)

        if raw_samples:
            chain = self._samples_to_sound(raw_samples)
            self._chain = chain
            # Play on loop (channel 1 reserved for music)
            channel = pygame.mixer.Channel(1)
            channel.play(chain, loops=-1)
            self._state = MusicState.PLAYING

    def stop_background(self) -> None:
        """Stop the looping background music."""
        channel = pygame.mixer.Channel(1)
        channel.stop()
        self._state = MusicState.STOPPED

    def play_sfx(self, name: str) -> None:
        """Play a sound effect.

        Args:
            name: 'eat' for food consumption chime,
                  'death' for game-over sound.
        """
        if self.muted:
            return

        if name == "eat" and self._eat_sound is None:
            self._eat_sound = self._build_chain(EAT_NOTES)

        elif name == "death" and self._death_sound is None:
            self._death_sound = self._build_chain(DEATH_NOTES)

        sound = None
        if name == "eat":
            sound = self._eat_sound
        elif name == "death":
            sound = self._death_sound

        if sound is not None:
            # Channel 0 for sound effects (music is on channel 1)
            channel = pygame.mixer.Channel(0)
            channel.play(sound)

    def mute(self) -> None:
        """Mute all audio."""
        self.muted = True
        self._state = MusicState.MUTED
        pygame.mixer.music.set_volume(0.0)

    def unmute(self) -> None:
        """Unmute all audio."""
        self.muted = False
        if self._state in (MusicState.PLAYING, MusicState.STOPPED):
            self._state = MusicState.PLAYING
        pygame.mixer.music.set_volume(self.volume)

    def _build_chain(
        self,
        notes: list[tuple[str, float]],
    ) -> pygame.mixer.Sound | None:
        """Build a chain of notes for a sound effect."""
        raw_samples: list[float] = []
        staccato_gap = int(self.sample_rate * 0.04)  # 40ms silence between notes
        for i, (note_name, duration) in enumerate(notes):
            freq = NOTE_FREQS.get(note_name, 0)
            samples = synth_note(freq, duration, self.volume, self.sample_rate)
            if samples is not None:
                if i > 0:
                    prev_name = notes[i - 1][0]
                    if note_name != "rest" and prev_name != "rest":
                        raw_samples.extend([0.0] * staccato_gap)
                raw_samples.extend(samples)
        if raw_samples:
            return self._samples_to_sound(raw_samples)
        return None
