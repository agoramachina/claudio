# music_perceiver

Give Claude the ability to "hear" music by transducing audio into representations it can actually process: images (spectrogram, chromagram, waveform) and structured data (tempo, key, note events, spectral features).

## install

```bash
pip install librosa soundfile matplotlib numpy
```

## use

```bash
python perceiver.py path/to/song.wav
# or specify an output directory
python perceiver.py song.flac --out analysis/
```

Handles `.wav`, `.mp3`, `.flac`, `.ogg`, `.m4a`, anything libsndfile or audioread can load.

## what Claude actually perceives

For each audio file, produces in `<name>_perceived/`:

| file | what it is | what Claude does with it |
|---|---|---|
| `spectrogram.png` | mel-spectrogram, 128 bins, log-scaled dB | reads timbre, texture, harmonic richness, onset density |
| `chromagram.png` | 12 pitch classes × time, CQT-based, beat-overlaid | reads harmony, chord progressions, melodic contour |
| `waveform.png` | amplitude envelope over time | reads dynamic shape, section boundaries |
| `summary.json` | tempo, key, pitch-class distribution, spectral & dynamic features | numerical grounding for reasoning |
| `notes.json` | monophonic pitch events `(start, end, note, hz_mean)` | reads the melodic line when audio is monophonic or melody-dominant |
| `claude_brief.md` | everything above synthesized into one markdown file | the thing you paste into a Claude conversation |

## handing output to Claude

Upload `claude_brief.md` plus the three PNGs (or the whole directory). Claude can view the images directly and read the markdown/JSON for numerical features. Ask whatever you want: "what's the mood," "describe the harmonic progression," "is there a key change around the bridge," "what does the timbre tell you about the instrumentation."

## known limits

- **key detection** uses Krumhansl-Schmuckler template matching on the mean chroma profile. It cannot distinguish a major key from its relative minor without tonal-center information — if it says "F major" and you know it's D minor, trust yourself. The chromagram shows the actual content.
- **tempo tracking** needs percussive onsets. For pad-heavy or beatless music, tempo may be unreliable or 0. Flagged in `summary.json` as `tempo_reliable`.
- **note transcription is monophonic only**. For polyphonic audio, the chromagram is the better map. (A v2 could integrate Spotify's basic-pitch for polyphonic MIDI transcription, once the Python 3.12 setuptools issue is worked around.)
- **octave errors** in the pyin pitch track happen when lower fundamentals (bass, chord roots) dominate. Pitch class is reliable even when octave isn't.

## extending

The interesting edges:

- swap `chroma_cqt` for `chroma_cens` (Chroma Energy Normalized) if you want smoother harmony tracking for cover-song-style analysis
- `librosa.decompose.hpss(y)` gives you harmonic/percussive source separation — useful to clean up chroma before key detection
- `librosa.segment.agglomerative` or `librosa.segment.recurrence_matrix` can find song structure (verse/chorus boundaries) — a natural next representation to add
- for fractal/scaling analysis (AM's other research direction), the mel-spectrogram matrix is already sitting in memory mid-pipeline; running 1/f analysis on row/column activations would slot in naturally
