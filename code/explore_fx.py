"""Exploration 4: What's in the FX stem, especially the S6-S7 burst?
Plot waveform + spectrogram of FX only, with discrete onset markers."""
from pathlib import Path
import numpy as np
import librosa
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

STEMS_DIR = Path("/home/claude/music_perceiver/stems")
OUT_DIR = Path("/home/claude/music_perceiver/stem_analysis")

SR = 22050
HOP = 512

y, _ = librosa.load(str(STEMS_DIR / "FX.mp3"), sr=SR, mono=True)
duration = len(y) / SR
times = np.arange(len(y)) / SR

# Onset detection — find discrete FX events
onset_frames = librosa.onset.onset_detect(y=y, sr=SR, hop_length=HOP, backtrack=False,
                                             units="frames", delta=0.15)
onset_times = librosa.frames_to_time(onset_frames, sr=SR, hop_length=HOP)

# Two-panel: waveform + mel-spectrogram
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 7), sharex=True)

ax1.plot(times, y, linewidth=0.5, color="#2a7fff", alpha=0.7)
for ot in onset_times:
    ax1.axvline(ot, color="#d04040", alpha=0.3, linewidth=0.5)
ax1.set_ylabel("amplitude")
ax1.set_title(f"FX stem — waveform + onsets ({len(onset_times)} onset events)")
ax1.set_xlim(0, duration)

mel = librosa.feature.melspectrogram(y=y, sr=SR, n_mels=128, fmax=8000, hop_length=HOP)
mel_db = librosa.power_to_db(mel, ref=np.max)
img = librosa.display.specshow(mel_db, sr=SR, x_axis="time", y_axis="mel", fmax=8000,
                                  ax=ax2, cmap="magma", hop_length=HOP)
fig.colorbar(img, ax=ax2, format="%+2.0f dB")
ax2.set_title("FX stem — mel-spectrogram")

fig.tight_layout()
fig.savefig(OUT_DIR / "fx_forensics.png", dpi=120, bbox_inches="tight")
plt.close(fig)

# Report where the major FX events cluster
print(f"FX onsets by time-region:")
bins = [(0, 30), (30, 70), (70, 105), (105, 130), (130, 165), (165, 190), (190, 210)]
labels = ["S1 intro", "S2 verse", "S3-S4", "S5 chorus", "S6", "S7-bridge", "S9 outro"]
for (lo, hi), lbl in zip(bins, labels):
    n = sum(1 for t in onset_times if lo <= t < hi)
    print(f"  {lbl:16s} {lo:>3}-{hi:>3}s: {n} events")

# RMS by region gives us rough energy distribution
rms = librosa.feature.rms(y=y, hop_length=HOP)[0]
rms_times = librosa.frames_to_time(np.arange(len(rms)), sr=SR, hop_length=HOP)
for (lo, hi), lbl in zip(bins, labels):
    mask = (rms_times >= lo) & (rms_times < hi)
    if mask.sum() > 0:
        e = rms[mask].mean()
        print(f"  FX rms in {lbl}: {e:.4f}")

print(f"\nsaved: {OUT_DIR}/fx_forensics.png")
