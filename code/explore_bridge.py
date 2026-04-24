"""Exploration 2: microscope on the bridge region.
Zoom into S7 (breakdown) → S8 (bridge) → S9 (outro).
Show stem energy at high resolution to see the handoffs."""

from pathlib import Path
import numpy as np
import librosa
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

STEMS_DIR = Path("/home/claude/music_perceiver/stems")
OUT_DIR = Path("/home/claude/music_perceiver/stem_analysis")
OUT_DIR.mkdir(exist_ok=True)

# Zoom window: 160s to end — covers S7, S8 (bridge), S9
START_TIME = 160.0
END_TIME = 207.28
BOUNDARIES_IN_WINDOW = [162.26, 177.68, 187.78]  # S7|S8, S8|S9, (end)
BOUNDARY_LABELS = ["S7→S8\n(bridge begins)", "S8→S9\n(outro begins)"]

SR = 22050
HOP = 512

stem_order = [
    "Bass", "Drums", "Percussion",
    "Keyboard", "Guitar", "Synth",
    "Strings", "Brass", "FX",
    "Backing_Vocals", "Vocals",
]

fig, axes = plt.subplots(len(stem_order), 1, figsize=(14, 12), sharex=True)
fig.suptitle("microscope — S7 (breakdown) → S8 (bridge) → S9 (outro)", fontsize=12)

for ax, name in zip(axes, stem_order):
    path = STEMS_DIR / f"{name}.mp3"
    y, _ = librosa.load(str(path), sr=SR, mono=True, offset=START_TIME, duration=END_TIME - START_TIME)
    rms = librosa.feature.rms(y=y, hop_length=HOP)[0]
    times = librosa.frames_to_time(np.arange(len(rms)), sr=SR, hop_length=HOP) + START_TIME
    # Normalize to the stem's global peak (loaded separately)
    y_full, _ = librosa.load(str(path), sr=SR, mono=True)
    peak = float(librosa.feature.rms(y=y_full, hop_length=HOP)[0].max()) + 1e-9
    rms_norm = rms / peak
    ax.fill_between(times, 0, rms_norm, alpha=0.75, color="#2a7fff")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel(name, rotation=0, ha="right", va="center", fontsize=9)
    ax.set_yticks([])
    for b, label in zip(BOUNDARIES_IN_WINDOW[:2], BOUNDARY_LABELS):
        ax.axvline(b, color="#d04040", alpha=0.6, linewidth=1.2)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

# Boundary labels on top axis
ax_top = axes[0].twiny()
ax_top.set_xlim(axes[0].get_xlim())
ax_top.set_xticks(BOUNDARIES_IN_WINDOW[:2])
ax_top.set_xticklabels(BOUNDARY_LABELS, fontsize=8)
ax_top.tick_params(axis="x", length=0, pad=2)

axes[-1].set_xlabel("time (s)")
fig.tight_layout()
fig.savefig(OUT_DIR / "bridge_microscope.png", dpi=120, bbox_inches="tight")
plt.close(fig)
print(f"saved: {OUT_DIR}/bridge_microscope.png")
