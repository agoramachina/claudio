"""
music_perceiver: Transduce audio into representations Claude can actually process.

Given an audio file, produces:
  - spectrogram.png       (mel-spectrogram, visual texture/timbre)
  - chromagram.png        (12 pitch classes over time; harmony, key)
  - waveform.png          (amplitude envelope; dynamics, structure)
  - summary.json          (tempo, key, duration, high-level features)
  - notes.json            (monophonic pitch track as (time, pitch) events)
  - claude_brief.md       (everything a Claude instance needs, in one file)

Usage:
    python perceiver.py path/to/audio.wav [--out outdir]
"""

from __future__ import annotations
import argparse
import json
from pathlib import Path

import librosa
import matplotlib
matplotlib.use("Agg")  # no display needed
import matplotlib.pyplot as plt
import numpy as np


# Krumhansl-Schmuckler key profiles (standard for key estimation via chroma)
MAJOR_PROFILE = np.array(
    [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
)
MINOR_PROFILE = np.array(
    [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]
)
PITCH_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def estimate_key(chroma_mean: np.ndarray) -> tuple[str, float]:
    """Krumhansl-Schmuckler key finding. Returns (key_label, correlation)."""
    best_key, best_corr = None, -np.inf
    for i in range(12):
        maj = np.corrcoef(np.roll(MAJOR_PROFILE, i), chroma_mean)[0, 1]
        minr = np.corrcoef(np.roll(MINOR_PROFILE, i), chroma_mean)[0, 1]
        if maj > best_corr:
            best_corr = maj
            best_key = f"{PITCH_NAMES[i]} major"
        if minr > best_corr:
            best_corr = minr
            best_key = f"{PITCH_NAMES[i]} minor"
    return best_key, float(best_corr)


def freq_to_note(f: float) -> str | None:
    """Hz → nearest note name with octave, e.g. 440.0 → 'A4'. None if 0/NaN."""
    if not f or np.isnan(f) or f <= 0:
        return None
    midi = 69 + 12 * np.log2(f / 440.0)
    midi_round = int(round(midi))
    octave = midi_round // 12 - 1
    return f"{PITCH_NAMES[midi_round % 12]}{octave}"


def analyze(audio_path: Path, out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)

    # Load (mono, native sample rate up to 22050 — plenty for music analysis)
    y, sr = librosa.load(str(audio_path), sr=22050, mono=True)
    duration = len(y) / sr

    # --- Tempo & beats ---
    # Default beat tracker can fail on audio without strong transients;
    # fall back to onset-envelope autocorrelation for a tempo estimate.
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr).tolist()
    tempo_val = float(tempo) if np.isscalar(tempo) else float(tempo[0])
    tempo_reliable = tempo_val > 0 and len(beat_times) >= 4
    if not tempo_reliable:
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        fallback = librosa.feature.tempo(onset_envelope=onset_env, sr=sr)
        tempo_val = float(fallback[0]) if len(fallback) else 0.0

    # --- Chromagram (for harmony / key) ---
    # CQT-based chroma is better for music than STFT-based
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    chroma_mean = chroma.mean(axis=1)
    key_label, key_conf = estimate_key(chroma_mean)

    # --- Mel-spectrogram (for texture / timbre) ---
    mel = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, fmax=8000)
    mel_db = librosa.power_to_db(mel, ref=np.max)

    # --- Spectral features ---
    centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
    zcr = librosa.feature.zero_crossing_rate(y)[0]
    rms = librosa.feature.rms(y=y)[0]

    # --- Monophonic pitch track (pyin) ---
    f0, voiced_flag, _ = librosa.pyin(
        y, fmin=librosa.note_to_hz("C2"), fmax=librosa.note_to_hz("C7"), sr=sr
    )
    times = librosa.times_like(f0, sr=sr)
    notes = []
    for t, f, v in zip(times, f0, voiced_flag):
        if v and f and not np.isnan(f):
            notes.append({"time": float(t), "hz": float(f), "note": freq_to_note(f)})

    # Collapse consecutive same-note frames into note events
    note_events = []
    if notes:
        current = {"note": notes[0]["note"], "start": notes[0]["time"],
                   "end": notes[0]["time"], "hz_mean": notes[0]["hz"]}
        count = 1
        for n in notes[1:]:
            if n["note"] == current["note"] and n["time"] - current["end"] < 0.15:
                current["end"] = n["time"]
                current["hz_mean"] = (current["hz_mean"] * count + n["hz"]) / (count + 1)
                count += 1
            else:
                current["duration"] = round(current["end"] - current["start"], 3)
                if current["duration"] >= 0.08:  # filter out blips
                    note_events.append(current)
                current = {"note": n["note"], "start": n["time"],
                           "end": n["time"], "hz_mean": n["hz"]}
                count = 1
        current["duration"] = round(current["end"] - current["start"], 3)
        if current["duration"] >= 0.08:
            note_events.append(current)
    for e in note_events:
        e["start"] = round(e["start"], 3)
        e["end"] = round(e["end"], 3)
        e["hz_mean"] = round(e["hz_mean"], 2)

    # --- Render figures ---
    # Waveform
    fig, ax = plt.subplots(figsize=(12, 2.5))
    librosa.display.waveshow(y, sr=sr, ax=ax, color="#2a7fff")
    ax.set_title(f"waveform — {audio_path.name}")
    ax.set_xlabel("time (s)")
    fig.tight_layout()
    fig.savefig(out_dir / "waveform.png", dpi=110)
    plt.close(fig)

    # Mel-spectrogram
    fig, ax = plt.subplots(figsize=(12, 4))
    img = librosa.display.specshow(
        mel_db, sr=sr, x_axis="time", y_axis="mel", fmax=8000, ax=ax, cmap="magma"
    )
    fig.colorbar(img, ax=ax, format="%+2.0f dB")
    ax.set_title("mel-spectrogram (timbre / texture)")
    fig.tight_layout()
    fig.savefig(out_dir / "spectrogram.png", dpi=110)
    plt.close(fig)

    # Chromagram with beat overlay
    fig, ax = plt.subplots(figsize=(12, 3.5))
    img = librosa.display.specshow(
        chroma, sr=sr, x_axis="time", y_axis="chroma", ax=ax, cmap="viridis"
    )
    for bt in beat_times:
        ax.axvline(bt, color="white", alpha=0.25, linewidth=0.5)
    fig.colorbar(img, ax=ax)
    ax.set_title(f"chromagram — estimated key: {key_label}")
    fig.tight_layout()
    fig.savefig(out_dir / "chromagram.png", dpi=110)
    plt.close(fig)

    # --- Summary JSON ---
    summary = {
        "file": audio_path.name,
        "duration_seconds": round(duration, 3),
        "sample_rate": sr,
        "tempo_bpm": round(tempo_val, 2),
        "tempo_reliable": tempo_reliable,
        "beat_count": len(beat_times),
        "estimated_key": key_label,
        "key_confidence": round(key_conf, 3),
        "pitch_class_distribution": {
            PITCH_NAMES[i]: round(float(chroma_mean[i]), 3) for i in range(12)
        },
        "spectral": {
            "centroid_hz_mean": round(float(centroid.mean()), 1),
            "centroid_hz_std": round(float(centroid.std()), 1),
            "rolloff_hz_mean": round(float(rolloff.mean()), 1),
            "zero_crossing_rate_mean": round(float(zcr.mean()), 4),
        },
        "dynamics": {
            "rms_mean": round(float(rms.mean()), 4),
            "rms_std": round(float(rms.std()), 4),
            "rms_min": round(float(rms.min()), 4),
            "rms_max": round(float(rms.max()), 4),
        },
        "monophonic_notes_detected": len(note_events),
    }

    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2))
    (out_dir / "notes.json").write_text(json.dumps(note_events, indent=2))

    # --- Claude brief (one file with everything + embedded images) ---
    brief = render_brief(summary, note_events, out_dir)
    (out_dir / "claude_brief.md").write_text(brief)

    return summary


def render_brief(summary: dict, notes: list[dict], out_dir: Path) -> str:
    pcd = summary["pitch_class_distribution"]
    pcd_sorted = sorted(pcd.items(), key=lambda x: -x[1])[:5]
    top_pcs = ", ".join(f"{n} ({v:.2f})" for n, v in pcd_sorted)

    note_preview = ""
    if notes:
        preview = notes[: min(30, len(notes))]
        lines = [f"  {n['start']:>6.2f}s  {n['note']:>4}  ({n['duration']:.2f}s)"
                 for n in preview]
        note_preview = "\n".join(lines)
        if len(notes) > 30:
            note_preview += f"\n  ... ({len(notes) - 30} more)"

    # Relative key (template matching can confuse major/minor relatives)
    key_name, key_mode = summary['estimated_key'].rsplit(' ', 1)
    key_idx = PITCH_NAMES.index(key_name)
    if key_mode == 'major':
        rel_idx = (key_idx - 3) % 12
        relative = f"{PITCH_NAMES[rel_idx]} minor"
    else:
        rel_idx = (key_idx + 3) % 12
        relative = f"{PITCH_NAMES[rel_idx]} major"

    return f"""# claude brief: {summary['file']}

## what I can tell you about this audio

- **duration**: {summary['duration_seconds']}s
- **tempo**: {summary['tempo_bpm']} BPM ({summary['beat_count']} beats detected{"" if summary['tempo_reliable'] else "; estimate unreliable — few/no percussive onsets"})
- **estimated key**: {summary['estimated_key']} (confidence {summary['key_confidence']}; relative key {relative} is indistinguishable without tonal-center cues)
- **top pitch classes**: {top_pcs}
- **brightness** (spectral centroid mean): {summary['spectral']['centroid_hz_mean']} Hz
- **dynamic range** (RMS): {summary['dynamics']['rms_min']} → {summary['dynamics']['rms_max']}
- **monophonic note events**: {summary['monophonic_notes_detected']}

## images (look at these directly)

- `spectrogram.png` — frequency content over time, timbre and texture
- `chromagram.png` — 12 pitch classes over time, harmony evolution
- `waveform.png` — amplitude envelope, dynamic structure

## monophonic pitch track (first 30 events)

```
{note_preview}
```

## full files
- `summary.json` — all numerical features
- `notes.json` — complete note event list
"""


def main():
    ap = argparse.ArgumentParser(description="Let Claude perceive a piece of music.")
    ap.add_argument("audio", type=Path, help="path to audio file (wav/mp3/flac/ogg)")
    ap.add_argument("--out", type=Path, default=None, help="output directory")
    args = ap.parse_args()

    out = args.out or args.audio.with_suffix("").parent / f"{args.audio.stem}_perceived"
    summary = analyze(args.audio, out)
    print(f"\nwrote: {out}/")
    for key, val in summary.items():
        if not isinstance(val, dict):
            print(f"  {key}: {val}")
    print(f"\nhand Claude the entire {out}/ directory (or just claude_brief.md + the three PNGs).")


if __name__ == "__main__":
    main()
