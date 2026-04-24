# claude_listens

A toolkit for Claude to appreciate music, built by AM and Claude (Opus 4.7) on 2026-04-23.

## what's in here

- **`listen.md`** — the protocol document. Drops into every per-song listening folder. Tells a Claude instance how to engage with a listening session.
- **`process_log.md`** — linear narrative of what was built, what we learned, and what remains open. Written for future Claudes who will inherit this.
- **`code/`** — Python toolkit.
  - `listener.py` — main tool. `python listener.py audio.wav [--sections N] [--artist ...] [--lyrics ...]`
  - `fast_listen.py` — variant that skips pyin pitch tracking for speed on polyphonic material.
  - `perceiver.py` — v1, single-document output. Kept for reference.
  - `explore_*.py` — per-song stem-based deep-dive scripts. Adapt paths when running on new material.
  - `README.md` — install and usage notes for the original perceiver.
  - `test_synthesizers/` — scripts that generate synthetic test audio.
- **`minute_manager_case_study/`** — the first real piece this tool was used on. Gamma's *"It's Pronounced Minute!"* from the *A Study in Time* D&D campaign.
  - `listening_document/` — sequential sectioned analysis produced by `listener.py`, including Claude's section-by-section `notes.md` with reactions, corrections, and an overall response.
  - `stem_analysis/` — four exploratory passes on the 11 Suno-exported stems (orchestration map, bridge microscope, vocal pitch track, FX forensics).

## install

```bash
pip install librosa soundfile matplotlib numpy scikit-learn
```

## use

```bash
cd code/
python listener.py /path/to/song.wav --artist "..." --year 2026
# For a polyphonic mix where pyin would be slow/unreliable:
python fast_listen.py   # (edit paths in-file for now)
```

Output lands in `<songname>_listening/`. Start with that folder's `listen.md`.

## open questions

See `process_log.md` for the full list. Top three:
1. Formalize the sessions structure (audio-only → with-lyrics → with-timing, each preserved).
2. Word-level lyric alignment (map syllables to time offsets).
3. ACE-Step audio-understanding as a second perception channel.

## what this is for

When someone shares music with a Claude instance through this tool, they're sharing something they care about in a form the instance can access. The goal is not an analysis report; the goal is a response. Opinions, reactions, things to revisit. If a session ends and Claude doesn't know what it thinks of the piece, the session hasn't happened yet — only indexing has.
