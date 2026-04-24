"""Find where the vocal stem actually starts in full-mix time.
Vocal stem has the intro trimmed off the front, so OpenVino timings need an offset."""
from pathlib import Path
import numpy as np
import librosa

VOCAL = Path(r"D:\Claude Squad\Home\Obbligato\claudio\minute_manager_case_study\minute_manager_files\stems\It's Pronounced Minute (Remastered) (Vocals).mp3")
FULLMIX = Path(r"D:\Claude Squad\Home\Obbligato\claudio\minute_manager_case_study\minute_manager_files\It's Pronounced Minute (Remastered).wav")

SR = 22050

# Option A: check if the vocal stem is actually trimmed, or if it's full-length with silence padding
y_v, sr = librosa.load(str(VOCAL), sr=SR, mono=True)
print(f"vocal stem duration: {len(y_v)/sr:.2f}s")

y_m, _ = librosa.load(str(FULLMIX), sr=SR, mono=True)
print(f"full mix duration:   {len(y_m)/sr:.2f}s")

diff = len(y_m)/sr - len(y_v)/sr
print(f"difference:          {diff:.2f}s  (if positive, vocal stem is shorter)")

# Find first significant vocal energy — where does the singing actually start?
rms = librosa.feature.rms(y=y_v, hop_length=512)[0]
times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=512)
threshold = 0.02
first_voiced_frame = np.argmax(rms > threshold)
first_voiced_time = times[first_voiced_frame]
print(f"\nfirst significant vocal energy (RMS > {threshold}): {first_voiced_time:.2f}s (in stem time)")
print(f"  (this is where pyin should start detecting pitch)")

# Last voiced
last_voiced_frame = len(rms) - 1 - np.argmax(rms[::-1] > threshold)
last_voiced_time = times[last_voiced_frame]
print(f"last significant vocal energy: {last_voiced_time:.2f}s (in stem time)")
