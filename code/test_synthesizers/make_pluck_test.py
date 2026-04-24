"""Generate a percussive test: plucked tones at 120 BPM, D minor pentatonic."""
import numpy as np
import soundfile as sf

SR = 22050
BPM = 120
BEAT = 60.0 / BPM  # 0.5s at 120 BPM

def note_to_hz(name: str, octave: int) -> float:
    names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    semis = names.index(name) + (octave - 4) * 12
    return 440.0 * 2 ** ((semis - 9) / 12.0)

def pluck(freq: float, dur: float, amp: float = 0.5) -> np.ndarray:
    """Decaying exponential envelope on sine — sounds like a pluck."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    # Add 2nd and 3rd harmonics for a richer (less pure-sine) timbre
    sig = (np.sin(2 * np.pi * freq * t)
           + 0.3 * np.sin(2 * np.pi * 2 * freq * t)
           + 0.15 * np.sin(2 * np.pi * 3 * freq * t))
    env = np.exp(-4.0 * t / dur)  # fast decay
    a = int(0.003 * SR)
    env[:a] = np.linspace(0, 1, a) * env[:a]
    return amp * sig * env

# D minor pentatonic: D F G A C
notes = [("D", 3), ("F", 3), ("G", 3), ("A", 3), ("C", 4),
         ("D", 4), ("C", 4), ("A", 3), ("G", 3), ("F", 3),
         ("D", 3), ("F", 3), ("A", 3), ("C", 4), ("D", 4), ("C", 4)]

pieces = []
for n, o in notes:
    pieces.append(pluck(note_to_hz(n, o), BEAT))

audio = np.concatenate(pieces)
audio = audio / (np.max(np.abs(audio)) + 1e-9) * 0.85
sf.write("/home/claude/music_perceiver/test_pluck.wav", audio, SR)
print(f"wrote test_pluck.wav: {len(audio)/SR:.2f}s, {BPM} BPM, D minor pentatonic")
