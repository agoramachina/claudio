"""Exploration 3: What is the Minute Manager actually singing?
Isolated vocal stem means pyin has a chance to work properly."""

from pathlib import Path
import numpy as np
import librosa
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import json

STEMS_DIR = Path("/home/claude/music_perceiver/stems")
OUT_DIR = Path("/home/claude/music_perceiver/stem_analysis")

SR = 22050
HOP = 512
PITCH_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

def freq_to_note(f):
    if not f or np.isnan(f) or f <= 0:
        return None
    midi = 69 + 12 * np.log2(f / 440.0)
    m = int(round(midi))
    return f"{PITCH_NAMES[m % 12]}{m // 12 - 1}", m

print("loading vocal stem...")
y, _ = librosa.load(str(STEMS_DIR / "Vocals.mp3"), sr=SR, mono=True)
print(f"  duration: {len(y)/SR:.2f}s")

print("running pyin (may take a minute on 3+ min of audio)...")
# Vocal range: roughly G2 (98 Hz) to C6 (1047 Hz); Minute Manager is baritone-ish
f0, voiced, voiced_prob = librosa.pyin(
    y,
    fmin=librosa.note_to_hz("G2"),
    fmax=librosa.note_to_hz("C6"),
    sr=SR, hop_length=HOP,
    frame_length=2048,
)
times = librosa.times_like(f0, sr=SR, hop_length=HOP)

# Convert to MIDI pitches for note-name overlay
midi_pitches = np.where(voiced & (f0 > 0) & ~np.isnan(f0),
                         69 + 12 * np.log2(f0 / 440.0),
                         np.nan)

print(f"  voiced frames: {np.sum(voiced)} / {len(voiced)}")

# Plot pitch track with section boundaries
summary = json.loads(Path("/home/claude/music_perceiver/minute_listening/summary.json").read_text())
boundaries = [0.0] + [s["end"] for s in summary["sections"]]

fig, ax = plt.subplots(figsize=(16, 5))
ax.plot(times, midi_pitches, ".", markersize=1.5, color="#2a7fff", alpha=0.7)
for b in boundaries[1:-1]:
    ax.axvline(b, color="#d04040", alpha=0.3, linewidth=0.8)
# Annotate section midpoints
for i, s in enumerate(summary["sections"]):
    mid = (boundaries[i] + boundaries[i+1]) / 2
    ax.text(mid, ax.get_ylim()[1] if i == 0 else 80, f"S{s['index']}",
            ha="center", va="bottom", fontsize=8, color="#666")
# Label note names on y-axis
midi_min, midi_max = 40, 80  # E2 to G#5 range
ax.set_ylim(midi_min, midi_max)
note_ticks = list(range(midi_min, midi_max + 1, 3))
ax.set_yticks(note_ticks)
ax.set_yticklabels([f"{PITCH_NAMES[m % 12]}{m // 12 - 1}" for m in note_ticks])
ax.set_xlabel("time (s)")
ax.set_ylabel("pitch")
ax.set_title("vocal pitch track — the minute manager's melody over time")
ax.grid(axis="y", alpha=0.2)
fig.tight_layout()
fig.savefig(OUT_DIR / "vocal_pitch_track.png", dpi=120, bbox_inches="tight")
plt.close(fig)

# Extract the bridge window specifically
bridge_start = 177.68
bridge_end = 187.78
mask = (times >= bridge_start) & (times < bridge_end) & voiced & ~np.isnan(f0)
bridge_times = times[mask]
bridge_f0 = f0[mask]
bridge_notes_raw = []
for t, f in zip(bridge_times, bridge_f0):
    result = freq_to_note(f)
    if result:
        bridge_notes_raw.append((t, f, result[0]))

# Collapse consecutive same-note frames into events
events = []
if bridge_notes_raw:
    cur = {"note": bridge_notes_raw[0][2], "start": bridge_notes_raw[0][0],
            "end": bridge_notes_raw[0][0], "hz": bridge_notes_raw[0][1]}
    cnt = 1
    for t, f, n in bridge_notes_raw[1:]:
        if n == cur["note"] and t - cur["end"] < 0.15:
            cur["end"] = t
            cur["hz"] = (cur["hz"] * cnt + f) / (cnt + 1)
            cnt += 1
        else:
            cur["duration"] = cur["end"] - cur["start"]
            if cur["duration"] >= 0.08:
                events.append(dict(cur))
            cur = {"note": n, "start": t, "end": t, "hz": f}
            cnt = 1
    cur["duration"] = cur["end"] - cur["start"]
    if cur["duration"] >= 0.08:
        events.append(dict(cur))

print(f"\nbridge notes ({len(events)} events):")
for e in events:
    print(f"  {e['start']:6.2f}s  {e['note']:>4}  ({e['duration']:.2f}s)  {e['hz']:.1f} Hz")

print(f"\nsaved: {OUT_DIR}/vocal_pitch_track.png")
