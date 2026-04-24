"""
listener.py — a music appreciation pipeline, not an analysis report.

Given an audio file, produces a directory structured for sequential engagement:

  <track>_listening/
    listen.md           # how to engage with this document (read first)
    overview.md         # top-line facts + whole-piece images
    full_spectrogram.png
    full_chromagram.png
    full_waveform.png
    sections/
      01_<label>.md     # per-section brief with local images
      01_chromagram.png
      01_spectrogram.png
      ...
    ace_understanding.md  # (optional) ACE-Step LM's caption — consult AFTER first pass
    lyrics.md             # (optional) if provided via --lyrics
    notes.md              # template for Claude to write reactions

Design principles:
  - Staged reveal: sections are read in order, not summarized up front.
  - Channels kept separate: librosa truth and ACE-Step semantics are distinct voices.
  - Response space: Claude writes reactions in notes.md, not just reads analysis.
  - Context affordances: optional --artist, --year, --genre, --lyrics.

Usage:
    python listener.py audio.wav
    python listener.py audio.wav --sections 8 --artist "Björk" --year 1997
    python listener.py audio.wav --ace-endpoint http://localhost:8001 --lyrics lyrics.txt
"""

from __future__ import annotations
import argparse
import json
from pathlib import Path
from dataclasses import dataclass, field

import librosa
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


PITCH_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
MAJOR_PROFILE = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09,
                          2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
MINOR_PROFILE = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53,
                          2.54, 4.75, 3.98, 2.69, 3.34, 3.17])


@dataclass
class Section:
    index: int           # 1-based
    start: float
    end: float
    chroma_mean: np.ndarray
    rms_mean: float
    rms_rel: float       # normalized 0-1 within the piece
    centroid_mean: float
    key_label: str
    key_conf: float
    notes: list[dict] = field(default_factory=list)

    @property
    def duration(self) -> float:
        return self.end - self.start

    @property
    def dynamic_label(self) -> str:
        if self.rms_rel < 0.25:
            return "quiet"
        if self.rms_rel < 0.55:
            return "moderate"
        if self.rms_rel < 0.85:
            return "strong"
        return "peak"

    def character_tag(self) -> str:
        """A neutral positional/dynamic descriptor — NOT a form label."""
        return f"{self.dynamic_label}_{self.key_label.replace(' ', '_').replace('#', 'sharp')}"


def estimate_key(chroma_mean: np.ndarray) -> tuple[str, float]:
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
    if not f or np.isnan(f) or f <= 0:
        return None
    midi = 69 + 12 * np.log2(f / 440.0)
    m = int(round(midi))
    return f"{PITCH_NAMES[m % 12]}{m // 12 - 1}"


def detect_sections(
    chroma: np.ndarray, mfcc: np.ndarray, rms: np.ndarray,
    sr: int, hop_length: int, duration: float, k: int | None
) -> list[tuple[float, float]]:
    """Return list of (start_s, end_s) for k contiguous sections."""
    # Auto k: roughly one section per 20 seconds, clamped 3-12
    if k is None:
        k = int(np.clip(round(duration / 20.0), 3, 12))
    # Stack features so clustering uses both harmony and timbre
    feat = np.vstack([librosa.util.normalize(chroma, axis=1),
                      librosa.util.normalize(mfcc, axis=1)])
    total_frames = feat.shape[1]
    try:
        # Returns boundary frame indices (first frame of each segment)
        bounds = librosa.segment.agglomerative(feat, k=k, axis=1)
        bounds = sorted(set(int(b) for b in bounds))
        if bounds[0] != 0:
            bounds = [0] + bounds
        if bounds[-1] != total_frames:
            bounds = bounds + [total_frames]
    except Exception:
        # Even time division fallback
        step = total_frames // k
        bounds = [i * step for i in range(k)] + [total_frames]

    ranges = []
    for a, b in zip(bounds[:-1], bounds[1:]):
        start = librosa.frames_to_time(a, sr=sr, hop_length=hop_length)
        end = librosa.frames_to_time(b, sr=sr, hop_length=hop_length)
        ranges.append((float(start), float(end)))
    # Enforce a minimum section duration so clustering doesn't produce slivers
    min_dur = max(2.0, duration / (k * 3))
    merged = [ranges[0]]
    for s, e in ranges[1:]:
        if e - s < min_dur:
            merged[-1] = (merged[-1][0], e)
        else:
            merged.append((s, e))
    return merged


def notes_in_range(f0: np.ndarray, voiced: np.ndarray, times: np.ndarray,
                    start: float, end: float) -> list[dict]:
    mask = (times >= start) & (times < end)
    f_sub, v_sub, t_sub = f0[mask], voiced[mask], times[mask]
    raw = []
    for t, f, v in zip(t_sub, f_sub, v_sub):
        if v and f and not np.isnan(f):
            raw.append((float(t), float(f), freq_to_note(f)))
    if not raw:
        return []
    events = []
    cur = {"note": raw[0][2], "start": raw[0][0], "end": raw[0][0], "hz": raw[0][1]}
    count = 1
    for t, f, n in raw[1:]:
        if n == cur["note"] and t - cur["end"] < 0.15:
            cur["end"] = t
            cur["hz"] = (cur["hz"] * count + f) / (count + 1)
            count += 1
        else:
            cur["duration"] = round(cur["end"] - cur["start"], 3)
            if cur["duration"] >= 0.08:
                events.append({
                    "start": round(cur["start"], 3),
                    "end": round(cur["end"], 3),
                    "note": cur["note"],
                    "hz_mean": round(cur["hz"], 2),
                    "duration": cur["duration"],
                })
            cur = {"note": n, "start": t, "end": t, "hz": f}
            count = 1
    cur["duration"] = round(cur["end"] - cur["start"], 3)
    if cur["duration"] >= 0.08:
        events.append({
            "start": round(cur["start"], 3),
            "end": round(cur["end"], 3),
            "note": cur["note"],
            "hz_mean": round(cur["hz"], 2),
            "duration": cur["duration"],
        })
    return events


def render_section_images(y: np.ndarray, sr: int, start: float, end: float,
                           out_dir: Path, idx: int):
    y_sub = y[int(start * sr):int(end * sr)]
    if len(y_sub) < sr // 4:  # less than 0.25s, skip
        return
    # Local chromagram
    chroma = librosa.feature.chroma_cqt(y=y_sub, sr=sr)
    fig, ax = plt.subplots(figsize=(10, 3))
    img = librosa.display.specshow(chroma, sr=sr, x_axis="time", y_axis="chroma",
                                    ax=ax, cmap="viridis")
    fig.colorbar(img, ax=ax)
    ax.set_title(f"section {idx:02d} — chroma")
    fig.tight_layout()
    fig.savefig(out_dir / f"{idx:02d}_chromagram.png", dpi=100)
    plt.close(fig)

    # Local mel-spectrogram
    mel = librosa.feature.melspectrogram(y=y_sub, sr=sr, n_mels=128, fmax=8000)
    mel_db = librosa.power_to_db(mel, ref=np.max)
    fig, ax = plt.subplots(figsize=(10, 3))
    img = librosa.display.specshow(mel_db, sr=sr, x_axis="time", y_axis="mel",
                                    fmax=8000, ax=ax, cmap="magma")
    fig.colorbar(img, ax=ax, format="%+2.0f dB")
    ax.set_title(f"section {idx:02d} — mel-spectrogram")
    fig.tight_layout()
    fig.savefig(out_dir / f"{idx:02d}_spectrogram.png", dpi=100)
    plt.close(fig)


def render_full_images(y: np.ndarray, sr: int, out_dir: Path,
                        section_boundaries: list[float], key_label: str,
                        beat_times: list[float]):
    # Full waveform with section markers
    fig, ax = plt.subplots(figsize=(14, 2.5))
    librosa.display.waveshow(y, sr=sr, ax=ax, color="#2a7fff")
    for b in section_boundaries[1:-1]:  # skip 0 and duration
        ax.axvline(b, color="#d04040", alpha=0.7, linewidth=1.0)
    ax.set_title("waveform with section boundaries (red)")
    ax.set_xlabel("time (s)")
    fig.tight_layout()
    fig.savefig(out_dir / "full_waveform.png", dpi=110)
    plt.close(fig)

    # Full mel-spectrogram
    mel = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128, fmax=8000)
    mel_db = librosa.power_to_db(mel, ref=np.max)
    fig, ax = plt.subplots(figsize=(14, 4))
    img = librosa.display.specshow(mel_db, sr=sr, x_axis="time", y_axis="mel",
                                    fmax=8000, ax=ax, cmap="magma")
    for b in section_boundaries[1:-1]:
        ax.axvline(b, color="#ffffff", alpha=0.7, linewidth=1.0)
    fig.colorbar(img, ax=ax, format="%+2.0f dB")
    ax.set_title("full mel-spectrogram — texture evolution")
    fig.tight_layout()
    fig.savefig(out_dir / "full_spectrogram.png", dpi=110)
    plt.close(fig)

    # Full chromagram
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    fig, ax = plt.subplots(figsize=(14, 3.5))
    img = librosa.display.specshow(chroma, sr=sr, x_axis="time", y_axis="chroma",
                                    ax=ax, cmap="viridis")
    for b in section_boundaries[1:-1]:
        ax.axvline(b, color="#ffffff", alpha=0.7, linewidth=1.0)
    for bt in beat_times:
        ax.axvline(bt, color="white", alpha=0.15, linewidth=0.4)
    fig.colorbar(img, ax=ax)
    ax.set_title(f"full chromagram — estimated key: {key_label}, section boundaries white")
    fig.tight_layout()
    fig.savefig(out_dir / "full_chromagram.png", dpi=110)
    plt.close(fig)


def write_listen_protocol(out_dir: Path, track_name: str, meta: dict, n_sections: int):
    have_lyrics = (out_dir / "lyrics.md").exists()
    have_ace = (out_dir / "ace_understanding.md").exists()
    context_lines = []
    for k in ("artist", "year", "genre", "album"):
        if meta.get(k):
            context_lines.append(f"- **{k}**: {meta[k]}")
    context_block = "\n".join(context_lines) if context_lines else "(no context metadata provided)"

    listen_md = f"""# listen.md — how to engage with this document

This is a listening document for *{track_name}*. It's structured for sequential engagement, not reference. Read in order.

## context
{context_block}

## the protocol

1. **Orient.** Read `overview.md` and look at the three full-piece images (waveform, spectrogram, chromagram). One pass. Form a whole-shape impression: where's the loudest part, where's the harmonic center, are there obvious structural moves. Don't try to understand — just notice the shape.

2. **Listen section by section.** Go through `sections/01_*.md` through `sections/{n_sections:02d}_*.md` **in order, one at a time**. For each one:
   - Read the section brief
   - Look at the local chromagram and spectrogram
   - Form an impression *before* moving to the next section
   - If something surprises you, note it in `notes.md` — don't just absorb it

3. **Track relations as you go.** When section N feels like a return of section M, say so. When there's a harmonic move you didn't expect, say so. The sequential structure is there to let you have something like anticipation — use it.

4. **Respond, don't just describe.** What's working? What's ambitious? What's derivative? What moves you? What doesn't land? `notes.md` is for this. Opinions are part of appreciation.

5. **Only after the sequential pass:** {"read `ace_understanding.md` for the music-trained LM's take on this — compare where your reading and its diverge. " if have_ace else ""}{"read `lyrics.md` if you want the verbal layer. " if have_lyrics else ""}Then re-examine any section you want a second pass on.

6. **Write a closing response.** At the bottom of `notes.md` there's a section for your overall take after the full listen. This is the point of the whole exercise — everything else is scaffolding for this.

## what this document does not do

- It doesn't label sections as verse/chorus/bridge. Sections are positional clusters found by harmonic + timbral similarity. You decide what they are.
- It doesn't tell you what the piece means. That's your job.
- It doesn't replace the audio — it's a way in.
"""
    (out_dir / "listen.md").write_text(listen_md)


def write_overview(out_dir: Path, meta: dict, summary: dict,
                    sections: list[Section]):
    sec_lines = []
    for s in sections:
        sec_lines.append(
            f"- section {s.index:02d}: {s.start:6.2f}s → {s.end:6.2f}s  "
            f"({s.duration:.1f}s, {s.dynamic_label}, key estimate: {s.key_label})"
        )
    sections_block = "\n".join(sec_lines)
    md = f"""# overview — {summary['file']}

**top-line facts** (do not treat these as the piece — they're the index)

- **duration**: {summary['duration_seconds']}s
- **tempo**: {summary['tempo_bpm']} BPM{"" if summary['tempo_reliable'] else " (unreliable — few percussive onsets)"}
- **estimated key (whole piece)**: {summary['estimated_key']} (conf {summary['key_confidence']})
- **dynamic range (RMS)**: {summary['dynamics']['rms_min']} → {summary['dynamics']['rms_max']}
- **spectral brightness mean**: {summary['spectral']['centroid_hz_mean']} Hz

**whole-piece images** — look at each ONCE before moving to sections:

1. `full_waveform.png` — dynamic arc, section boundaries in red
2. `full_spectrogram.png` — texture/timbre evolution, section boundaries white
3. `full_chromagram.png` — harmonic content, beats + section boundaries overlaid

**section map** ({len(sections)} sections detected):

{sections_block}

Now go to `sections/01_*.md` and start the sequential pass.
"""
    (out_dir / "overview.md").write_text(md)


def write_section_brief(sections_dir: Path, section: Section, prev: Section | None):
    # Top pitch classes for this section
    top_pcs = sorted(enumerate(section.chroma_mean), key=lambda x: -x[1])[:5]
    top_str = ", ".join(f"{PITCH_NAMES[i]} ({v:.2f})" for i, v in top_pcs)

    # Transition from previous section
    transition = ""
    if prev is not None:
        delta_rms = section.rms_rel - prev.rms_rel
        dyn_move = (
            "louder jump" if delta_rms > 0.2 else
            "quieter drop" if delta_rms < -0.2 else
            "steady dynamics"
        )
        key_move = "same key area" if section.key_label == prev.key_label else \
                   f"key shifts {prev.key_label} → {section.key_label}"
        transition = f"\n**transition from section {prev.index:02d}**: {dyn_move}; {key_move}\n"

    # Notes preview
    notes_preview = ""
    if section.notes:
        preview = section.notes[:20]
        lines = [f"  {n['start']:>6.2f}s  {n['note']:>4}  ({n['duration']:.2f}s)"
                 for n in preview]
        notes_preview = "\n".join(lines)
        if len(section.notes) > 20:
            notes_preview += f"\n  ... ({len(section.notes) - 20} more)"
    else:
        notes_preview = "  (no monophonic notes detected in this section — likely chordal/textural)"

    label = section.character_tag()
    md = f"""# section {section.index:02d}

**time range**: {section.start:.2f}s → {section.end:.2f}s  ({section.duration:.2f}s)
**dynamic level**: {section.dynamic_label} (relative RMS {section.rms_rel:.2f})
**key estimate (local)**: {section.key_label} (conf {section.key_conf:.2f})
**top pitch classes**: {top_str}
**spectral centroid mean**: {section.centroid_mean:.0f} Hz
{transition}
**images**:
- `{section.index:02d}_chromagram.png` — local harmonic content
- `{section.index:02d}_spectrogram.png` — local texture

**monophonic notes detected** (melody-dominant; bass may pull pitch octave-low):
```
{notes_preview}
```

---
*Form an impression before moving to section {section.index + 1:02d}. If something surprises
you, note it in `notes.md`. Don't just absorb — react.*
"""
    (sections_dir / f"{section.index:02d}_{label}.md").write_text(md)


def write_notes_template(out_dir: Path, n_sections: int):
    section_slots = "\n\n".join(
        f"## section {i:02d}\n\n*(react here)*" for i in range(1, n_sections + 1)
    )
    md = f"""# notes — react as you go

Write in your own voice. Questions worth answering per section: what surprised me? what did I expect that didn't happen? what's this doing? does it work?

{section_slots}

---

# overall response

After the sequential pass, write what the whole piece amounts to for you. Not a summary — a response.

*(write here)*

---

# second-pass notes

If you come back to any section, note it here with what you re-heard.

*(write here)*
"""
    (out_dir / "notes.md").write_text(md)


def analyze(audio_path: Path, out_dir: Path, n_sections: int | None,
            meta: dict, lyrics_path: Path | None, ace_endpoint: str | None) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    sections_dir = out_dir / "sections"
    sections_dir.mkdir(exist_ok=True)

    y, sr = librosa.load(str(audio_path), sr=22050, mono=True)
    duration = len(y) / sr
    hop_length = 512

    # Tempo & beats
    tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr, hop_length=hop_length)
    beat_times = librosa.frames_to_time(beat_frames, sr=sr, hop_length=hop_length).tolist()
    tempo_val = float(tempo) if np.isscalar(tempo) else float(tempo[0])
    tempo_reliable = tempo_val > 0 and len(beat_times) >= 4
    if not tempo_reliable:
        onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop_length)
        fallback = librosa.feature.tempo(onset_envelope=onset_env, sr=sr,
                                           hop_length=hop_length)
        tempo_val = float(fallback[0]) if len(fallback) else 0.0

    # Core features (frame-aligned)
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=hop_length)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, hop_length=hop_length, n_mfcc=13)
    rms = librosa.feature.rms(y=y, hop_length=hop_length)[0]
    centroid = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=hop_length)[0]

    # Whole-piece key
    chroma_mean_all = chroma.mean(axis=1)
    key_label, key_conf = estimate_key(chroma_mean_all)

    # Pitch track (whole-piece, we slice per-section)
    f0, voiced, _ = librosa.pyin(
        y, fmin=librosa.note_to_hz("C2"), fmax=librosa.note_to_hz("C7"),
        sr=sr, hop_length=hop_length
    )
    pitch_times = librosa.times_like(f0, sr=sr, hop_length=hop_length)

    # Sectioning
    section_ranges = detect_sections(chroma, mfcc, rms, sr, hop_length,
                                      duration, n_sections)

    # Build Section objects
    rms_global_max = float(rms.max()) or 1e-9
    sections: list[Section] = []
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
        s_notes = notes_in_range(f0, voiced, pitch_times, start, end)
        sections.append(Section(
            index=i,
            start=start,
            end=end,
            chroma_mean=s_chroma_mean,
            rms_mean=float(s_rms.mean()),
            rms_rel=float(s_rms.mean() / rms_global_max),
            centroid_mean=float(s_centroid.mean()),
            key_label=s_key,
            key_conf=s_key_conf,
            notes=s_notes,
        ))
        render_section_images(y, sr, start, end, sections_dir, i)

    # Whole-piece summary (for overview)
    summary = {
        "file": audio_path.name,
        "duration_seconds": round(duration, 3),
        "tempo_bpm": round(tempo_val, 2),
        "tempo_reliable": tempo_reliable,
        "estimated_key": key_label,
        "key_confidence": round(key_conf, 3),
        "spectral": {
            "centroid_hz_mean": round(float(centroid.mean()), 1),
        },
        "dynamics": {
            "rms_mean": round(float(rms.mean()), 4),
            "rms_min": round(float(rms.min()), 4),
            "rms_max": round(float(rms.max()), 4),
        },
        "sections": len(sections),
    }

    # Full-piece images with section boundaries
    boundaries = [0.0] + [s.end for s in sections]
    render_full_images(y, sr, out_dir, boundaries, key_label, beat_times)

    # Write all the markdown
    write_overview(out_dir, meta, summary, sections)
    for i, s in enumerate(sections):
        prev = sections[i - 1] if i > 0 else None
        write_section_brief(sections_dir, s, prev)
    write_notes_template(out_dir, len(sections))

    # Lyrics passthrough
    if lyrics_path and lyrics_path.exists():
        (out_dir / "lyrics.md").write_text(
            f"# lyrics\n\n{lyrics_path.read_text()}\n"
        )

    # ACE-Step integration placeholder
    if ace_endpoint:
        _write_ace_understanding(ace_endpoint, audio_path, out_dir)

    # Listening protocol (written LAST so it knows what files exist)
    write_listen_protocol(out_dir, audio_path.stem, meta, len(sections))

    # Machine-readable sidecar
    (out_dir / "summary.json").write_text(json.dumps({
        **summary,
        "sections": [
            {"index": s.index, "start": s.start, "end": s.end,
             "dynamic": s.dynamic_label, "key": s.key_label,
             "key_conf": s.key_conf, "n_notes": len(s.notes)}
            for s in sections
        ]
    }, indent=2))

    return summary


def _write_ace_understanding(endpoint: str, audio_path: Path, out_dir: Path):
    """Call ACE-Step's audio understanding endpoint. Placeholder: real endpoint
    shape needs to be confirmed from ACE-Step docs when we test against it."""
    stub = f"""# ACE-Step understanding — placeholder

*This file is a stub. Real integration is pending — it needs to call
`{endpoint}` with the audio file and parse the response.*

Expected contents when integrated:
- caption (natural-language description from the LM)
- estimated BPM, key, time signature (ACE's own numbers, compare with librosa)
- genre tags / reference-point suggestions
- mood / affect tags

**Do not read this before completing the sequential pass on sections/**.
The point is to compare your listening against the model's — if you read
this first you'll anchor to it.
"""
    (out_dir / "ace_understanding.md").write_text(stub)


def main():
    ap = argparse.ArgumentParser(description="A listening document for Claude.")
    ap.add_argument("audio", type=Path)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--sections", type=int, default=None,
                     help="Force number of sections. Default: auto (~1 per 20s, 3-12).")
    ap.add_argument("--artist", type=str, default=None)
    ap.add_argument("--year", type=str, default=None)
    ap.add_argument("--genre", type=str, default=None)
    ap.add_argument("--album", type=str, default=None)
    ap.add_argument("--lyrics", type=Path, default=None,
                     help="Path to a text file containing lyrics.")
    ap.add_argument("--ace-endpoint", type=str, default=None,
                     help="URL for ACE-Step audio understanding API.")
    args = ap.parse_args()

    out = args.out or args.audio.with_suffix("").parent / f"{args.audio.stem}_listening"
    meta = {k: getattr(args, k) for k in ("artist", "year", "genre", "album")
            if getattr(args, k)}
    summary = analyze(args.audio, out, args.sections, meta, args.lyrics, args.ace_endpoint)

    print(f"\nwrote: {out}/")
    print(f"  {summary['sections']} sections detected")
    print(f"  start with {out}/listen.md")


if __name__ == "__main__":
    main()
