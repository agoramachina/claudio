"""Exploration 1: The orchestration map.
Stack all 11 stems' RMS energy over time, overlay section boundaries.
Tells us: who plays where."""

from pathlib import Path
import numpy as np
import librosa
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import json

STEMS_DIR = Path("/home/claude/music_perceiver/stems")
OUT_DIR = Path("/home/claude/music_perceiver/stem_analysis")
OUT_DIR.mkdir(exist_ok=True)

# Load section boundaries from the full-mix analysis we already did
summary = json.loads(Path("/home/claude/music_perceiver/minute_listening/summary.json").read_text())
boundaries = [0.0] + [s["end"] for s in summary["sections"]]
section_labels = [f"S{s['index']}" for s in summary["sections"]]
section_keys = [s["key"] for s in summary["sections"]]
section_dynamics = [s["dynamic"] for s in summary["sections"]]
section_midpoints = [(boundaries[i] + boundaries[i+1]) / 2 for i in range(len(summary["sections"]))]

# Ordering chosen by musical role: low rhythm → high rhythm → low harmony → high harmony → lead
stem_order = [
    "Bass", "Drums", "Percussion",
    "Keyboard", "Guitar", "Synth",
    "Strings", "Brass",
    "FX",
    "Backing_Vocals", "Vocals",
]

# Load each stem's RMS envelope at the same hop
SR = 22050
HOP = 512
stem_rms = {}
stem_peak = {}
for name in stem_order:
    path = STEMS_DIR / f"{name}.mp3"
    y, sr = librosa.load(str(path), sr=SR, mono=True)
    rms = librosa.feature.rms(y=y, hop_length=HOP)[0]
    stem_rms[name] = rms
    stem_peak[name] = float(rms.max())
    print(f"  {name:16s}  dur={len(y)/sr:.2f}s  rms_peak={rms.max():.4f}  rms_mean={rms.mean():.4f}")

# Align all stems to the shortest one
min_len = min(len(r) for r in stem_rms.values())
times = librosa.frames_to_time(np.arange(min_len), sr=SR, hop_length=HOP)

# Stack plot
fig, axes = plt.subplots(len(stem_order), 1, figsize=(16, 14), sharex=True)
fig.suptitle("orchestration map — per-stem RMS energy, section boundaries", fontsize=12, y=0.995)
for ax, name in zip(axes, stem_order):
    rms = stem_rms[name][:min_len]
    # Normalize each stem to its own peak so texture stories are comparable
    rms_norm = rms / (stem_peak[name] + 1e-9)
    ax.fill_between(times, 0, rms_norm, alpha=0.7, color="#2a7fff")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel(name, rotation=0, ha="right", va="center", fontsize=9)
    ax.set_yticks([])
    # Section boundary markers
    for b in boundaries[1:-1]:
        ax.axvline(b, color="#d04040", alpha=0.4, linewidth=0.8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
axes[-1].set_xlabel("time (s)")
# Section labels on top axis
ax_top = axes[0].twiny()
ax_top.set_xlim(axes[0].get_xlim())
ax_top.set_xticks(section_midpoints)
ax_top.set_xticklabels([f"{lbl}\n{k}\n{d}" for lbl, k, d in zip(section_labels, section_keys, section_dynamics)],
                        fontsize=7)
ax_top.tick_params(axis="x", length=0, pad=2)
fig.tight_layout()
fig.savefig(OUT_DIR / "orchestration_map.png", dpi=120, bbox_inches="tight")
plt.close(fig)
print(f"\nsaved: {OUT_DIR}/orchestration_map.png")
