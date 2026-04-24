"""Fast analysis path — skips pyin pitch tracking (unreliable on polyphonic mix).
Runs everything else: sections, chromagram, mel-spec, dynamics, key, tempo.
"""
import sys, json
from pathlib import Path
import numpy as np
import librosa
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, '/home/claude/music_perceiver')
from listener import (
    estimate_key, detect_sections, render_section_images, render_full_images,
    write_overview, write_section_brief, write_notes_template,
    write_listen_protocol, Section, PITCH_NAMES
)

audio_path = Path("/home/claude/music_perceiver/minute.wav")
out_dir = Path("/home/claude/music_perceiver/minute_listening")
out_dir.mkdir(exist_ok=True)
sections_dir = out_dir / "sections"
sections_dir.mkdir(exist_ok=True)

print("loading audio...")
y, sr = librosa.load(str(audio_path), sr=22050, mono=True)
duration = len(y) / sr
hop_length = 512
print(f"loaded: {duration:.1f}s @ {sr}Hz")

print("tempo / beats...")
tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr, hop_length=hop_length)
beat_times = librosa.frames_to_time(beat_frames, sr=sr, hop_length=hop_length).tolist()
tempo_val = float(tempo) if np.isscalar(tempo) else float(tempo[0])
tempo_reliable = tempo_val > 0 and len(beat_times) >= 4
print(f"  tempo: {tempo_val:.2f} BPM, {len(beat_times)} beats, reliable={tempo_reliable}")

print("chroma / mfcc / rms / centroid...")
chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=hop_length)
mfcc = librosa.feature.mfcc(y=y, sr=sr, hop_length=hop_length, n_mfcc=13)
rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]
centroid = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=hop_length)[0]

chroma_mean_all = chroma.mean(axis=1)
key_label, key_conf = estimate_key(chroma_mean_all)
print(f"  key: {key_label} (conf {key_conf:.3f})")

# Auto-section — this song is ~3.5min, expect ~7-10 sections
print("sectioning...")
section_ranges = detect_sections(chroma, mfcc, rms, sr, hop_length, duration, None)
print(f"  found {len(section_ranges)} sections")

rms_global_max = float(rms.max()) or 1e-9
sections = []
for i, (start, end) in enumerate(section_ranges, start=1):
    fa = librosa.time_to_frames(start, sr=sr, hop_length=hop_length)
    fb = librosa.time_to_frames(end, sr=sr, hop_length=hop_length)
    fb = min(fb, chroma.shape[1])
    if fb <= fa:
        continue
    s_chroma_mean = chroma[:, fa:fb].mean(axis=1)
    s_rms = rms[fa:fb]
    s_centroid = centroid[fa:fb]
    s_key, s_key_conf = estimate_key(s_chroma_mean)
    sections.append(Section(
        index=i, start=start, end=end,
        chroma_mean=s_chroma_mean,
        rms_mean=float(s_rms.mean()),
        rms_rel=float(s_rms.mean() / rms_global_max),
        centroid_mean=float(s_centroid.mean()),
        key_label=s_key, key_conf=s_key_conf,
        notes=[],  # skip pyin
    ))
    print(f"  section {i}: {start:6.2f}-{end:6.2f}s  rms_rel={sections[-1].rms_rel:.2f}  key={s_key}  ({sections[-1].dynamic_label})")
    render_section_images(y, sr, start, end, sections_dir, i)

summary = {
    "file": audio_path.name,
    "duration_seconds": round(duration, 3),
    "tempo_bpm": round(tempo_val, 2),
    "tempo_reliable": tempo_reliable,
    "estimated_key": key_label,
    "key_confidence": round(key_conf, 3),
    "spectral": {"centroid_hz_mean": round(float(centroid.mean()), 1)},
    "dynamics": {
        "rms_mean": round(float(rms.mean()), 4),
        "rms_min": round(float(rms.min()), 4),
        "rms_max": round(float(rms.max()), 4),
    },
    "sections": len(sections),
}

boundaries = [0.0] + [s.end for s in sections]
render_full_images(y, sr, out_dir, boundaries, key_label, beat_times)

meta = {"artist": "Gamma", "year": "2026", "album": "A Study in Time",
        "genre": "orchestral villain song / musical theater"}
write_overview(out_dir, meta, summary, sections)
for i, s in enumerate(sections):
    prev = sections[i - 1] if i > 0 else None
    write_section_brief(sections_dir, s, prev)
write_notes_template(out_dir, len(sections))
write_listen_protocol(out_dir, audio_path.stem, meta, len(sections))

(out_dir / "summary.json").write_text(json.dumps({
    **summary,
    "sections": [
        {"index": s.index, "start": s.start, "end": s.end,
         "dynamic": s.dynamic_label, "rms_rel": round(s.rms_rel, 3),
         "key": s.key_label, "key_conf": round(s.key_conf, 3),
         "centroid_hz": round(s.centroid_mean, 0)}
        for s in sections
    ]
}, indent=2))
print(f"\ndone: {out_dir}/")
