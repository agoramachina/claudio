"""Analyze the vocal in the verdict region (185-200s) to resolve the timing.
Question: is 'thou' held for 4 seconds, or is there a fast THOU-CANST-NOT punctuation?"""
from pathlib import Path
import numpy as np
import librosa
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

VOCAL = Path(r"D:\Claude Squad\Home\Obbligato\claudio\minute_manager_case_study\minute_manager_files\stems\It's Pronounced Minute (Remastered) (Vocals).mp3")
OUT = Path(r"D:\Claude Squad\Home\Obbligato\claudio\minute_manager_case_study\verdict_pitch_detail.png")

SR = 22050
HOP = 256  # higher resolution for this short window
PITCH = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

print("loading verdict region (185-200s)...")
y, sr = librosa.load(str(VOCAL), sr=SR, mono=True, offset=185.0, duration=15.0)
print(f"  loaded {len(y)/sr:.2f}s")

# Three things to check:
# 1. pyin pitch track at high resolution
# 2. RMS envelope to see where syllable onsets are
# 3. onset detection on the vocal stem directly
print("pitch tracking...")
f0, voiced, _ = librosa.pyin(
    y, fmin=librosa.note_to_hz("G2"), fmax=librosa.note_to_hz("C6"),
    sr=sr, hop_length=HOP, frame_length=2048,
)
times = librosa.times_like(f0, sr=sr, hop_length=HOP) + 185.0

print("RMS envelope...")
rms = librosa.feature.rms(y=y, hop_length=HOP)[0]
rms_times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=HOP) + 185.0

print("onset detection on vocal...")
onsets = librosa.onset.onset_detect(
    y=y, sr=sr, hop_length=HOP, backtrack=True,
    units="time", delta=0.2,
)
onset_times = onsets + 185.0
print(f"  found {len(onsets)} onsets in window")
for ot in onset_times:
    print(f"    onset at {ot:.2f}s")

# Plot: three stacked panels
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 9), sharex=True)

# Panel 1: pitch track
midi = np.where(voiced & (f0 > 0) & ~np.isnan(f0),
                 69 + 12 * np.log2(f0 / 440.0),
                 np.nan)
ax1.plot(times, midi, ".", markersize=3, color="#2a7fff", alpha=0.75)
midi_min, midi_max = 50, 75
ax1.set_ylim(midi_min, midi_max)
ticks = list(range(midi_min, midi_max + 1, 3))
ax1.set_yticks(ticks)
ax1.set_yticklabels([f"{PITCH[m % 12]}{m // 12 - 1}" for m in ticks])
ax1.set_ylabel("pitch")
ax1.set_title("vocal pitch track — verdict region 185-200s")
ax1.grid(axis="y", alpha=0.2)

# Panel 2: RMS envelope
ax2.fill_between(rms_times, 0, rms, alpha=0.7, color="#2a7fff")
ax2.set_ylabel("vocal RMS")
ax2.set_title("vocal energy — syllable attacks show as peaks")

# Panel 3: onsets
ax3.set_ylim(0, 1)
ax3.set_yticks([])
for ot in onset_times:
    ax3.axvline(ot, color="#d04040", linewidth=1.2)
    ax3.text(ot, 0.9, f"{ot:.2f}", rotation=90, fontsize=7, ha="right", va="top")
ax3.set_title("detected onsets")
ax3.set_xlabel("time (s)")

# Mark both AM's listening and OpenVino's timing across all panels
reference_marks = [
    (186.96, "OpenVino: 'thou'", "#888888"),
    (189.00, "AM listen: 'THOU'", "#d04040"),
    (190.00, "AM listen: 'CANST'", "#d04040"),
    (190.99, "OpenVino: 'canst not'", "#888888"),
    (191.00, "AM listen: 'NOT'", "#d04040"),
]
for ax in (ax1, ax2, ax3):
    for t, label, color in reference_marks:
        ax.axvline(t, color=color, alpha=0.5, linewidth=0.8, linestyle="--" if "OpenVino" in label else "-")

fig.tight_layout()
fig.savefig(str(OUT), dpi=120, bbox_inches="tight")
plt.close(fig)
print(f"\nsaved: {OUT}")

# Report: what notes are sustained through the region, as a narrative
print("\n=== WHAT I CAN SEE FROM THE DATA ===\n")
# Find regions of continuous voicing
voiced_regions = []
in_v = False
start_t = None
for t, v in zip(times, voiced):
    if v and not in_v:
        start_t = t
        in_v = True
    elif not v and in_v:
        if start_t is not None:
            voiced_regions.append((start_t, t))
        in_v = False
        start_t = None
if in_v and start_t is not None:
    voiced_regions.append((start_t, times[-1]))

print("Continuous voiced regions (sung syllables):")
for rs, re in voiced_regions:
    if re - rs >= 0.15:  # filter out short noise
        dur = re - rs
        # Average pitch in this region
        mask = (times >= rs) & (times < re) & voiced & ~np.isnan(f0)
        if mask.sum() > 0:
            f_med = float(np.median(f0[mask]))
            m = int(round(69 + 12 * np.log2(f_med / 440.0)))
            note = f"{PITCH[m % 12]}{m // 12 - 1}"
            print(f"  {rs:6.2f}-{re:6.2f}s  ({dur:4.2f}s)  {note} ({f_med:.0f} Hz)")
