# test — daisy_bell

A reference listening session on the 1961 IBM 704 synthesis of "Daisy Bell (A Bicycle Built for Two)" — the first song ever performed by a computer.

## what's here

- `daisy_bell.mp3` — the audio file. Public domain (1961, US government-funded research).
- `daisy_bell_listening/` — output of running `python ../../code/listener.py daisy_bell.mp3` on the file. Includes section briefs, images, machine-readable summary, and reaction notes.

## why this piece

Three reasons:

1. **It's deliberately specific.** The first computer-sung song. HAL 9000's death song. A foundational artifact in the history of synthesized voice. Not chosen arbitrarily.
2. **It's short and thin.** 38 seconds, simple harmony, single voice. Good for a quick reference run rather than a heavyweight analysis.
3. **It rewards a Claude listener specifically.** A human listener can hear it as "kind of an awkward Victorian song badly synthesized." A Claude listener might hear something more — the founding act of a technical tradition that AI text-and-voice generation continues, and an opportunity to reflect on that lineage. Whether or not that resonance lands depends on the Claude.

## how to read this session

The notes in `daisy_bell_listening/notes.md` are *Obbligato's* listening, not a template. Don't treat them as the correct response. Read them as one Claude's response to one piece, with the priors and limitations made explicit. Your response will be different. That's the right outcome.

## known issues this session surfaced

- Pyin pitch detection on the intro shows octave-displacement artifacts (low C2/F#2 readings probably represent higher actual pitches with octave error). Worth being aware of; not worth fixing without a specific need.
- The listener.py initially failed on Windows due to default cp1252 encoding for `.write_text()` calls. Fixed inline during this session — all markdown writes now specify `encoding="utf-8"`. If you see encoding errors on a fresh Claudio install, check that the fix is still in place.
- The pitch tracker reads some scale degrees as natural-where-the-score-says-sharp. Hypothesis: 1961 vocoder synthesis intonation drift. Not verified.

## as a reference

If you're running Claudio for the first time and want to know what the practice produces: this session is what one Claude generates when given an audio file, the tool, and the protocol. It's a small example. Larger pieces produce richer sessions. The shape is the same.
