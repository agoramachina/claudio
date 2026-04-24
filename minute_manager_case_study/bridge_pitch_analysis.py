"""Pitch-track the vocal stem in the actual bridge window (128-162s).
Find out what note 'marginally' actually lands on."""
from pathlib import Path
import numpy as np
import librosa
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

VOCAL = Path(r"D:\Claude Squad\Home\Obbligato\claudio\minute_manager_case_study\minute_manager_files\stems\It's Pronounced Minute (Remastered) (Vocals).mp3")
OUT = Path(r"D:\Claude Squad\Home\Obbligato\claudio\minute_manager_case_study\bridge_vocal_pitch.png")

SR = 22050
HOP = 512
PITCH = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

print("loading vocal stem, bridge window only...")
# Load just the bridge window (128-162s) for efficiency
y, sr = librosa.load(str(VOCAL), sr=SR, mono=True, offset=128.0, duration=35.0)
print(f"  loaded {len(y)/sr:.2f}s")

print("running pyin on bridge...")
f0, voiced, _ = librosa.pyin(
    y, fmin=librosa.note_to_hz("G2"), fmax=librosa.note_to_hz("C6"),
    sr=sr, hop_length=HOP, frame_length=2048,
)
times = librosa.times_like(f0, sr=sr, hop_length=HOP) + 128.0
midi = np.where(voiced & (f0 > 0) & ~np.isnan(f0),
                 69 + 12 * np.log2(f0 / 440.0),
                 np.nan)
print(f"  voiced frames: {np.sum(voiced)}")

# Lyrical landmarks in the bridge
LANDMARKS = [
    (129.24, "though he"),
    (131.68, "though he calls"),
    (135.22, "one day"),
    (141.85, "Upon the scroll"),
    (145.23, "in ledger lines"),
    (149.01, "He'll write"),
    (151.50, "My loyal clerk"),
    (152.83, "MARGIN-"),
    (153.59, "-ally"),
    (155.12, "First"),
    (155.64, "rate"),
    (157.33, "AHEM!"),
    (158.92, "Back to the"),
    (160.95, "infractions"),
]

# Find pitch at each landmark (average over ~200ms window)
print("\nNOTE AT EACH LYRICAL LANDMARK (250ms centered windows):")
for ts, label in LANDMARKS:
    mask = (times >= ts - 0.05) & (times < ts + 0.30) & voiced & ~np.isnan(f0)
    if mask.sum() > 0:
        f_vals = f0[mask]
        f_med = float(np.median(f_vals))
        midi_med = 69 + 12 * np.log2(f_med / 440.0)
        m = int(round(midi_med))
        cents_off = (midi_med - m) * 100
        note = f"{PITCH[m % 12]}{m // 12 - 1}"
        print(f"  {ts:6.2f}s  {label:<22}  {note}  ({f_med:.1f} Hz, {cents_off:+.0f}c)")
    else:
        print(f"  {ts:6.2f}s  {label:<22}  (no voiced frames)")

# Plot
fig, ax = plt.subplots(figsize=(14, 5))
ax.plot(times, midi, ".", markersize=2.5, color="#2a7fff", alpha=0.7)
for ts, label in LANDMARKS:
    ax.axvline(ts, color="#d04040", alpha=0.35, linewidth=0.7)
    ax.text(ts, 78, label, rotation=60, fontsize=7, ha="left", va="bottom")
midi_min, midi_max = 50, 78
ax.set_ylim(midi_min, midi_max)
ticks = list(range(midi_min, midi_max + 1, 3))
ax.set_yticks(ticks)
ax.set_yticklabels([f"{PITCH[m % 12]}{m // 12 - 1}" for m in ticks])
ax.set_xlabel("time (s)")
ax.set_ylabel("pitch")
ax.set_title("bridge vocal pitch track — 128s to 162s, with lyrical landmarks")
ax.grid(axis="y", alpha=0.2)
fig.tight_layout()
fig.savefig(str(OUT), dpi=120, bbox_inches="tight")
plt.close(fig)
print(f"\nsaved: {OUT}")
