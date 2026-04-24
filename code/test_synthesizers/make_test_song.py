"""
Structured test: an A-B-A-C-A "song" with clear section contrasts.
- A (verse-like): C major, I-V-vi-IV, moderate dynamics, melody in mid register
- B (chorus-like): C major, IV-V-I-vi, louder, melody higher + doubled octave
- C (bridge): modulation to A minor / G major area, sparser, quieter
"""
import numpy as np
import soundfile as sf

SR = 22050
BPM = 96
BEAT = 60.0 / BPM

def note_to_hz(name: str, octave: int) -> float:
    names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    semis = names.index(name) + (octave - 4) * 12
    return 440.0 * 2 ** ((semis - 9) / 12.0)

def tone(freq: float, dur: float, amp: float = 0.2,
         harmonics: list[float] = None, decay: float = 0.0) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n) / SR
    harmonics = harmonics or [1.0]
    sig = sum(h * np.sin(2 * np.pi * (k + 1) * freq * t)
              for k, h in enumerate(harmonics))
    env = np.ones(n)
    a = int(0.008 * SR)
    if a > 0:
        env[:a] = np.linspace(0, 1, a)
    r = int(0.04 * SR)
    if r > 0 and n > r:
        env[-r:] = np.linspace(1, 0, r)
    if decay > 0:
        env *= np.exp(-decay * t)
    return amp * sig * env

def chord_pad(notes_list: list[tuple[str, int]], dur: float, amp: float = 0.07) -> np.ndarray:
    parts = [tone(note_to_hz(n, o), dur, amp, harmonics=[1.0, 0.3]) for n, o in notes_list]
    L = max(len(p) for p in parts)
    return sum(np.pad(p, (0, L - len(p))) for p in parts)

def pluck(freq: float, dur: float, amp: float = 0.35) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n) / SR
    sig = (np.sin(2 * np.pi * freq * t)
           + 0.4 * np.sin(2 * np.pi * 2 * freq * t)
           + 0.2 * np.sin(2 * np.pi * 3 * freq * t))
    env = np.exp(-3.0 * t / dur)
    a = int(0.003 * SR)
    if a > 0:
        env[:a] = np.linspace(0, 1, a) * env[:a]
    return amp * sig * env

def build_bar(chord: list[tuple[str, int]], melody_notes: list[tuple[str, int]],
              amp_chord: float, amp_melody: float, bar_beats: int = 4) -> np.ndarray:
    bar_dur = bar_beats * BEAT
    ch = chord_pad(chord, bar_dur, amp=amp_chord)
    # Melody: each note gets bar_beats/len(melody) beats
    beats_per_note = bar_beats / len(melody_notes)
    mel_parts = [pluck(note_to_hz(n, o), beats_per_note * BEAT, amp=amp_melody)
                  for n, o in melody_notes]
    mel = np.concatenate(mel_parts)
    L = max(len(ch), len(mel))
    ch = np.pad(ch, (0, L - len(ch)))
    mel = np.pad(mel, (0, L - len(mel)))
    return ch + mel

# === Section A (verse) — C major, I-V-vi-IV, moderate ===
A_chords = [[("C", 3), ("E", 4), ("G", 4)],
            [("G", 3), ("B", 3), ("D", 4)],
            [("A", 3), ("C", 4), ("E", 4)],
            [("F", 3), ("A", 3), ("C", 4)]]
A_melody = [[("E", 4), ("D", 4), ("C", 4), ("D", 4)],
            [("D", 4), ("C", 4), ("B", 3), ("C", 4)],
            [("C", 4), ("B", 3), ("A", 3), ("B", 3)],
            [("A", 3), ("G", 3), ("F", 3), ("G", 3)]]

def section_A() -> np.ndarray:
    bars = [build_bar(c, m, amp_chord=0.06, amp_melody=0.3)
            for c, m in zip(A_chords, A_melody)]
    return np.concatenate(bars)

# === Section B (chorus) — C major, IV-V-I-vi, louder, melody up an octave ===
B_chords = [[("F", 3), ("A", 3), ("C", 4)],
            [("G", 3), ("B", 3), ("D", 4)],
            [("C", 4), ("E", 4), ("G", 4)],
            [("A", 3), ("C", 4), ("E", 4)]]
B_melody = [[("A", 4), ("G", 4), ("F", 4), ("G", 4)],
            [("G", 4), ("F", 4), ("E", 4), ("D", 4)],
            [("E", 5), ("D", 5), ("C", 5), ("G", 4)],
            [("A", 4), ("G", 4), ("E", 4), ("C", 4)]]

def section_B() -> np.ndarray:
    bars = [build_bar(c, m, amp_chord=0.10, amp_melody=0.45)
            for c, m in zip(B_chords, B_melody)]
    return np.concatenate(bars)

# === Section C (bridge) — A minor feel, sparser, quieter ===
C_chords = [[("A", 2), ("E", 3), ("A", 3)],
            [("D", 3), ("A", 3), ("D", 4)],
            [("E", 3), ("B", 3), ("E", 4)],
            [("A", 2), ("E", 3), ("A", 3)]]
C_melody = [[("A", 4), ("G", 4)],  # fewer notes, longer
            [("F", 4), ("E", 4)],
            [("D", 4), ("B", 3)],
            [("A", 3), ("E", 4)]]

def section_C() -> np.ndarray:
    bars = [build_bar(c, m, amp_chord=0.05, amp_melody=0.22, bar_beats=4)
            for c, m in zip(C_chords, C_melody)]
    return np.concatenate(bars)

# Assemble A-B-A-C-A with small gaps
gap = np.zeros(int(0.1 * SR))
audio = np.concatenate([
    section_A(), gap,
    section_B(), gap,
    section_A(), gap,
    section_C(), gap,
    section_A(),
])
audio = audio / (np.max(np.abs(audio)) + 1e-9) * 0.85
sf.write("/home/claude/music_perceiver/test_song.wav", audio, SR)
print(f"wrote test_song.wav: {len(audio)/SR:.2f}s, form: A-B-A-C-A, BPM {BPM}")
