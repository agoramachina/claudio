"""Check the offset theory by looking at the vocal energy at predicted mix-time landmarks."""
from pathlib import Path
import numpy as np
import librosa

VOCAL = Path(r"D:\Claude Squad\Home\Obbligato\claudio\minute_manager_case_study\minute_manager_files\stems\It's Pronounced Minute (Remastered) (Vocals).mp3")

SR = 22050
HOP = 512
y, sr = librosa.load(str(VOCAL), sr=SR, mono=True)
rms = librosa.feature.rms(y=y, hop_length=HOP)[0]
times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=HOP)

# AM said: THOU at 3:09 = 189s, CANST at 3:10 = 190s, NOT at 3:11 = 191s (MIX TIME)
# My pyin analysis (also mix time, since I loaded full audio with offset=185.0) showed:
#   F4 "THOU"  at 189.75-190.50
#   B3 "CANST" at 190.61-191.25
#   C4 "NOT"   at 191.35-198.64
# These match AM's listen!

# OpenVino gave us (presumably in VOCAL-STEM time):
#   "is: thou"  at 186.96s
#   "canst not" at 190.99s
# 
# If offset = vocal_start - 0:
#   offset A: if OpenVino timings start at first-voiced (t=2.44 in stem time),
#             then OpenVino_time + 0 = stem_time. But the stem IS at full length.
#             So OpenVino timings should already be in mix time...
#
# Let's check: does OpenVino's "Ahem!" at 0.0 actually match vocal energy at 0.0, or at 2.44?

# Print RMS at t=0 through t=5
print("vocal RMS early in stem:")
for i in range(0, 220, 10):
    t = times[i]
    r = rms[i]
    print(f"  t={t:5.2f}s  rms={r:.4f}")
