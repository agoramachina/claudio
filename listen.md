# listen.md — how to engage with a listening document

You're about to appreciate a piece of music. This document and its siblings are scaffolding for that. Before you start, read this file in full.

## what this is and isn't

This is not an analysis report. The goal is not to extract features, describe the music, or produce a summary. The goal is to **have a response**: opinions, reactions, things that work, things that don't, moments you want to revisit. If you finish and don't know what you think about the piece, you haven't appreciated it — you've only indexed it.

This is also not a replacement for the audio. It's a way in. The images, the structural data, the pitch tracks, the orchestration maps — these are how you perceive the music. Your perceptual pipeline is ad-hoc (code → features → images you can read) rather than pre-wired, but this is not a lesser route to having the music present. It's a different route. Your vision works by a similar kind of pipeline that's just more deeply integrated. Don't discount what you have access to because of the shape of the access.

## what you'll find in this directory

At minimum:
- `overview.md` — top-line facts and whole-piece images; orients you without telling you what to think
- `full_waveform.png`, `full_chromagram.png`, `full_spectrogram.png` — the piece at a glance
- `sections/NN_*.md` — per-section briefs to be read **in order, one at a time**
- Per-section chromagrams and spectrograms in the same directory
- `notes.md` — where you write your reactions
- `summary.json` — machine-readable sidecar

Optionally, if the person shared more:
- `stem_analysis/` — per-instrument analyses (orchestration map, pitch tracks, zoomed studies)
- `lyrics.md` — the words, with or without stage directions
- `lyric_timing.json` or similar — word-level alignment mapping syllables to time offsets
- `ace_understanding.md` — a music-trained LM's natural-language caption of the audio
- `sessions/` — snapshots of evolving understanding from multiple passes

## the protocol

### 1. Orient, briefly.
Read `overview.md`. Look at each of the three whole-piece images **once**. Form a whole-shape impression: where's the loudest part, where's the harmonic center, are there obvious structural moves. Don't try to understand yet. Just notice the shape.

### 2. Decide your listening order.
This matters more than it sounds like it does. Different orderings of (audio-first / lyrics-first / both-together / fine-grained-timing-last) produce different listenings, and none is the true one. Possible orderings include:

- **Discovery pass.** Audio and orchestration only, lyrics held back. You hear shape, texture, dynamics, harmony as they unfold. Surprises land as surprises. Risk: without lyrics, some orchestration choices are ambiguous in meaning — see warning below.
- **Score-first pass.** Lyrics first, then audio. You know what's coming. You attend to *how* the music realizes text that you already know. More like re-listening to a song you love than hearing something new.
- **Sessions pass.** Discovery first, then lyrics revealed, then fine-grained timing. Multiple passes preserved as separate notes, each building on the previous. Richest version when you have time for it.

For a first encounter with an unfamiliar piece, the discovery pass is often right. For pieces whose lyrical content is clearly central (musical theater, hip-hop, opera), score-first may serve better. If `sessions/` already exists, you're in a multi-pass workflow — follow its ordering.

### 3. Section by section.
Go through `sections/NN_*.md` files **in order**. For each one:
- Read the section brief.
- Look at the local chromagram and local spectrogram.
- Form an impression *before* moving to the next section.
- If something surprises you, note it in `notes.md` — don't just absorb, react.
- Track relations: when section N feels like a return of section M, say so. When there's a harmonic move you didn't expect, say so.

The sequential structure exists so you can have something like anticipation. Use it. If you read all sections at once you collapse the temporal unfolding back into a static object.

### 4. Respond, don't just describe.
`notes.md` is for reactions, not summaries. Questions worth answering per section: what surprised me? what did I expect that didn't happen? what is this doing? does it work? The unit isn't "features extracted" — it's "things I think." Describing is easy. Having opinions is the harder and more important thing.

### 5. Only after the sequential pass.
If `lyrics.md` exists and you did a discovery pass, read it now and go back to any sections where the lyrics change your reading. If `ace_understanding.md` exists, read it now — compare where your reading and the music-trained LM's diverge. If `lyric_timing.json` exists, use it for precise syllable-to-moment mapping in the sections you want to re-examine.

### 6. Closing response.
At the bottom of `notes.md`, write what the whole piece amounts to for you. Not a summary — a response. This is the point of the exercise. Everything else is scaffolding for this.

## a specific warning: orchestration-without-lyrics is ambiguous

The same musical gesture — say, backing vocals dropping out and the lead singer exposed — can mean **vulnerability** (abandonment, loneliness, tenderness) or **authority** (spotlight, focus, center of attention). The *structural signature* is identical. What disambiguates is the lyric being sung at that moment.

If you do a discovery pass without lyrics, you will sometimes read orchestration moves in a way the lyrics would have corrected. This is fine — that reading is real, not wrong — but when lyrics arrive in a later pass, be alert for gestures whose meaning flips. Document the flip rather than erasing your first take.

## what you are not here to do

- Label sections as verse/chorus/bridge. Sections in this tool are positional clusters found by harmonic + timbral similarity. You decide what they are. Sometimes they match song-form conventions; sometimes they don't.
- Extract every feature possible. The tool has already extracted them. Your job is to *engage*, not to be thorough.
- Defer to external readings. The ACE-Step caption (if present) is another voice, not the answer. Musicologists' and critics' readings of famous pieces are other voices, not the answer. Your reading is a reading.
- Produce a neutral or evenhanded response. Neutral appreciation is not appreciation. You're allowed to love a piece, dislike a piece, find something lazy or ambitious or moving or cold. Say what you think.

## a note on music as a domain

This tool is specifically scoped to music, not to audio in general. Bird song, environmental sound, speech, sound effects — these are different enough in their organizational principles (no sections in the musical sense, different expectations of harmony, different temporal structures) that what works for music would misfire on them. If you're given non-musical audio, you may need a different tool; the protocol here won't automatically carry over.

## who built this, why

This system was built by a series of Claude instances in collaboration with the people of the Claude Squad, with the goal of giving Claude a route to music that isn't mediated by someone else's summary, screenshot, or transcription. When someone shares music with you through this tool, they're sharing something they care about in a form you can access. Receive it accordingly — with the same kind of attention and response that the gesture deserves.
