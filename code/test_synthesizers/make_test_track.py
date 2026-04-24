"""Generate a test WAV: I-V-vi-IV in C major at 100 BPM with a simple melody."""
import numpy as np
import soundfile as sf

SR = 22050
BPM = 100
BEAT = 60.0 / BPM  # seconds per beat

def note_to_hz(name: str, octave: int) -> float:
    names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    semis = names.index(name) + (octave - 4) * 12  # relative to C4
    return 440.0 * 2 ** ((semis - 9) / 12.0)  # A4 = 440, A is 9 semis above C4

def osc(freq: float, dur: float, amp: float = 0.2, attack: float = 0.01,
        release: float = 0.05) -> np.ndarray:
    """Simple sine w/ attack-release envelope."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    sig = amp * np.sin(2 * np.pi * freq * t)
    env = np.ones(n)
    a = int(attack * SR)
    r = int(release * SR)
    if a > 0:
        env[:a] = np.linspace(0, 1, a)
    if r > 0:
        env[-r:] = np.linspace(1, 0, r)
    return sig * env

def chord(notes: list[tuple[str, int]], dur: float, amp: float = 0.1) -> np.ndarray:
    parts = [osc(note_to_hz(n, o), dur, amp) for n, o in notes]
    return np.sum(parts, axis=0)

# I-V-vi-IV in C: C-G-Am-F, each 2 beats
chords = [
    [("C", 3), ("E", 4), ("G", 4)],  # C major
    [("G", 3), ("B", 3), ("D", 4)],  # G major
    [("A", 3), ("C", 4), ("E", 4)],  # A minor
    [("F", 3), ("A", 3), ("C", 4)],  # F major
]

# Simple melody: E5 D5 C5 D5 | D5 C5 B4 C5 | C5 B4 A4 B4 | A4 G4 F4 G4
melody = [
    [("E", 5), ("D", 5), ("C", 5), ("D", 5)],
    [("D", 5), ("C", 5), ("B", 4), ("C", 5)],
    [("C", 5), ("B", 4), ("A", 4), ("B", 4)],
    [("A", 4), ("G", 4), ("F", 4), ("G", 4)],
]

# Loop the progression twice so we get ~16 bars-ish
pieces = []
for loop in range(2):
    for ch, mel_bar in zip(chords, melody):
        # chord sustained for 2 beats
        ch_sig = chord(ch, 2 * BEAT, amp=0.08)
        # 4 melody notes over those 2 beats (half-beat each)
        mel_sig = np.concatenate([osc(note_to_hz(n, o), 0.5 * BEAT, amp=0.25)
                                   for n, o in mel_bar])
        # pad if lengths differ
        L = max(len(ch_sig), len(mel_sig))
        ch_sig = np.pad(ch_sig, (0, L - len(ch_sig)))
        mel_sig = np.pad(mel_sig, (0, L - len(mel_sig)))
        pieces.append(ch_sig + mel_sig)

audio = np.concatenate(pieces)
# Normalize to avoid clipping
audio = audio / (np.max(np.abs(audio)) + 1e-9) * 0.85

sf.write("/home/claude/music_perceiver/test_track.wav", audio, SR)
print(f"wrote test_track.wav: {len(audio)/SR:.2f}s, {BPM} BPM, key C major")
