"""Compare the two different vocal files - are they different, and which did OpenVino use?"""
from pathlib import Path
import numpy as np
import librosa

V_FULL = Path(r"D:\Claude Squad\Home\Obbligato\claudio\minute_manager_case_study\minute_manager_files\stems\full\It's Pronounced Minute (Remastered) (Vocals).mp3")
V_SPLIT = Path(r"D:\Claude Squad\Home\Obbligato\claudio\minute_manager_case_study\minute_manager_files\stems\split\It's Pronounced Minute (Remastered) (Vocals).mp3")

SR = 22050
HOP = 512

for name, path in [("full/Vocals", V_FULL), ("split/Vocals", V_SPLIT)]:
    print(f"\n=== {name} ===")
    print(f"  path exists: {path.exists()}")
    if not path.exists():
        continue
    print(f"  file size: {path.stat().st_size:,} bytes")
    y, sr = librosa.load(str(path), sr=SR, mono=True)
    dur = len(y) / sr
    print(f"  duration: {dur:.3f}s")
    
    # Find first and last significant vocal energy
    rms = librosa.feature.rms(y=y, hop_length=HOP)[0]
    times = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=HOP)
    thresh = 0.02
    first_idx = np.argmax(rms > thresh)
    last_idx = len(rms) - 1 - np.argmax(rms[::-1] > thresh)
    print(f"  first vocal energy: {times[first_idx]:.3f}s")
    print(f"  last vocal energy:  {times[last_idx]:.3f}s")
    print(f"  vocal span: {times[last_idx] - times[first_idx]:.3f}s")
