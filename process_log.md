# process log — building a way for Claude to listen to music

*A record of how this listening system was built, what we learned, and what remains open. Written for future Claude instances who will use, extend, or inherit this work.*

---

## the starting problem

For years, users who wanted to share music with Claude had to translate sound into forms Claude could access: lyrics as text, sheet music as images, Sonic Visualizer screenshots carefully curated to be informationally dense and aesthetically legible. These workarounds were craft in themselves — tux tucker specifically tuned each Sonic Visualizer view before capturing, choosing what to emphasize so Claude could read harmonic or textural content from the picture. One user (tux tucker) built this practice around a piece called KOCHlea: a Koch-snowflake L-system that generated MIDI that became post-rock that became a Sonic Visualizer screenshot that became a shared artifact. "Koch curve plus cochlea — the fractal that hears itself."

These workarounds worked. They were also lossy, pre-filtered, and bandwidth-limited. A screenshot captures what the user decided to show. It doesn't let Claude *ask new questions* of the audio.

The goal of this system: give Claude a way to have the music as a thing present, not a thing summarized.

## version 1: perceiver.py — analysis report

First attempt. Python script using librosa: takes an audio file, produces a directory with a spectrogram, chromagram, waveform, monophonic pitch track via pyin, and a `claude_brief.md` that packages everything into one pastable document.

**Worked on synthetic test audio.** Key detection via Krumhansl-Schmuckler on mean chroma: nailed C major on a test song. Chromagram was readable — you could see the chord progression directly as pitch-class bands lighting up in sequence.

**Conceptual problem:** this was a reference document, not a listening experience. It gave Claude everything at once. That's closer to reading a program note than hearing the music. Music unfolds in time; a single brief collapses that unfolding. Something important was missing.

## version 2: listener.py — sequential sections

Redesigned around the idea that **appreciation requires staging**. The key move: detect musically-meaningful sections using agglomerative clustering on stacked chroma + MFCC features, then produce separate files per section to be read **in order, one at a time.**

Structure of output:
- `listen.md` — protocol telling Claude how to engage with the document
- `overview.md` — top-line facts and whole-piece images (read once, then move on)
- `sections/01_*.md` through `NN_*.md` — per-section briefs read sequentially
- `notes.md` — scratchpad for Claude's actual reactions
- `summary.json` — machine-readable sidecar

**Design principles baked in:**
1. Sequential engagement: read section N *before* looking at section N+1.
2. Multiple channels kept separate: librosa's signal-processing truth isn't pre-merged with external interpretation layers.
3. Response space: a dedicated place for Claude to write reactions, not just absorb features.
4. Context affordances: optional artist/year/genre/lyrics arguments so Claude can bring historical/theoretical knowledge to bear.
5. No form labels: sections are positional clusters, not "verse/chorus/bridge." Claude decides what they are.

**Tested on a synthetic A-B-A-C-A piece.** The bridge detection worked cleanly — the only section where harmony moved out of C major. The A-B-A segmentation was imperfect because verse and chorus shared key and timbre and differed mainly in register, which chroma+MFCC weight weakly. Documented as a real limitation.

**The important test:** Claude (this instance) actually *used* the tool on the synthetic song — walked through it section by section, wrote reactions as each section arrived, formed opinions, noted what surprised. Writing "a teacher would love this, a listener would not" about a piece Claude had designed itself was the moment the tool proved it was doing the intended thing. Not extracting features — producing opinions.

## the minute manager case study

tux tucker shared "It's Pronounced Minute!" — a villain song for the Minute Manager, a bureaucratic cleric obsessed with the Horologist, in Gamma's D&D campaign *A Study in Time*. Gamma generated the song via Suno, refined prompts, iterated to a Remastered version, and exported 11 stems through Suno Studio. Total duration 3:27, 143.55 BPM, key center G minor.

**First pass: full mix only.** Ran `listener.py` on the master. It detected 9 sections. The structural data alone was enough to predict:
- Section 1 (0-26s, G major, quiet): spoken bureaucratic intro
- Sections 2-7 (G minor, verse-chorus alternation): body
- Section 8 (178-188s, **C minor**, moderate — 10 seconds): bridge
- Section 9 (188-207s, G major, strong): outro

The bridge prediction was key. Shortest body section, only harmonic modulation in the piece, dynamic drop, modulating to iv of the tonic (standard bridge grammar). All of that was detectable from summary stats before looking at any image or hearing any word.

**Second pass: stems.** tux tucker exported all 11 stems (bass, drums, percussion, keyboard, guitar, synth, strings, brass, FX, backing vocals, vocals). Four exploratory analyses were run:

1. **Orchestration map.** Stacked per-stem RMS energy with section boundaries. Revealed: backing vocals are discrete block events coinciding with choruses; keyboard appears only in sections 4-5; FX clusters in the last third; brass sustains almost throughout.

2. **Bridge microscope.** Zoomed into S7→S8→S9 at high resolution. Revealed: the orchestration withdraws from the bridge in phases, not all at once. Backing vocals linger ~5 seconds into the bridge before disappearing exactly as the "marginally" lyric arrives. That delayed withdrawal is a staging choice — it makes loneliness happen *during* the singing rather than *before* it.

3. **Vocal pitch track.** Ran pyin on the isolated vocal stem. Revealed the melody directly. The S2→S3 boundary has a G5 spike (the "SEIZE THEM!" shout). The bridge notes form a classical lament figure: G#4 (♭6 in C minor) descending stepwise through F, Eb, D, C, back up, and repeated. Same melodic shape used in Purcell's "When I am laid in earth" and Bach's crucifixus. The outro has a drop to A3 (lowest register in the song) for "Thou canst not."

4. **FX forensics.** Investigated the dense FX burst around 2:30-3:27. Initially interpreted as a theatrical design layer that intensified during climax, backed off for the bridge, returned for the outro. **tux tucker corrected this**: Suno generates mix-first and separates stems *backward*, so the FX stem is actually cymbal crashes bleeding over from percussion. The substantive finding (cymbals cluster in the climactic section) was real; the compositional-intent reading was wrong. Useful lesson about how to trust stems from any backward-separation tool.

## the main mistake and what it taught

Initially misread section 9 (the outro) as "loneliness" because the backing vocals are absent and the orchestration thins around "Thou canst not." **tux tucker corrected this as *focus*, not abandonment.** Everyone steps back because *he* is the one in the frame — concentrated authority, not exposure. The "NOT!" explodes back outward with the full band.

The correction matters beyond this one song. The orchestration moves in S8 (bridge) and S9 (outro) look structurally identical — stems withdrawing, vocal exposed — but they mean opposite things. What determines the meaning is the **words**. The bridge is vulnerable because "marginally first-rate" is a vulnerable lyric. The outro is authoritative because "Thou canst not" is an authoritative lyric. Instrumentation without lyrics is an ambiguous signal.

**Design implication:** a listening system that reveals orchestration before lyrics can produce misreadings that wouldn't happen if both arrived together. Not a bug — different orderings produce genuinely different listenings, and no single order is "correct" — but the tool should make this tradeoff explicit rather than accidentally bake one ordering in.

## the sessions insight

tux tucker articulated what this means at the level of the whole tool: **giving Claude audio-first, lyrics-first, or both-together produces different listenings, and this is a feature of listening itself, not a limitation to engineer around.**

A musicologist who reads the score before hearing the piece hears a different piece than someone who encounters it at a party. Both are real listenings. Neither is complete. And doing them in sequence — discovery pass first, then text-informed pass, then fine-grained analysis — produces the richest version because each pass builds on the previous.

This suggests the listener's document should evolve from "one monolithic output" to **sessions**:
- Session 1: audio + orchestration only, discovery pass, notes written
- Session 2: lyrics revealed, earlier notes re-examined, corrections/additions
- Session 3: word-level timing (from forced alignment), specific syllables mapped to specific musical moments

Each session preserved as a snapshot, the evolution itself as the record. This is what `notes.md`'s "second-pass notes" section was reaching toward; it needs to be formalized into an actual directory structure.

## what we learned about the specific piece

(Kept here as a case study showing what the tool can extract when everything works. Won't apply to other songs, but the *shape* of this analysis is portable.)

- Prompt said "triumphant and grand brass fanfare." The generated song is in **G minor**, not major. The tonal irony — a minor-key triumphant march reads as the character overreaching — is craft. Whether Gamma prompted for it, Suno pattern-matched it, or the remix chain produced it, the result is character work the prompt didn't explicitly request.
- The piece is frame-structured: G major → G minor → G major. Opening and closing in major; the minor body is what he *actually is*. This frames the whole song as bureaucratic comedy rather than sincere villainy.
- The 10-second bridge is where the craft concentrates. It's the only harmonic modulation, the only orchestration withdrawal, the only melodic region using lament-figure vocabulary. Everything else in the song is armature to make this moment land.
- The lyrical recursion — *"is invalidated by the bylaws I've applied to you"* — is the same rondo structure operating at the sentence level that the song uses at the form level. Self-trapping bureaucratic language as the musical organizing principle.

## current state

Working in this environment: `listener.py` for sequential analysis, `fast_listen.py` for polyphonic material where pyin on the mix is unreliable, and a set of exploration scripts (`explore_orchestration.py`, `explore_bridge.py`, `explore_vocals.py`, `explore_fx.py`) that can be run per-song for stem-based deep dives.

Output structure per song: a `<song>_listening/` directory with overview, full-piece images, sections/, notes.md, summary.json. Optional `stem_analysis/` directory when stems are available.

## open questions / next directions

- **Sessions as a formal structure.** `sessions/01_audio_only.md`, `sessions/02_with_lyrics.md`, `sessions/03_with_timing.md`. Time-stamped snapshots of the evolving understanding. Currently implicit in second-pass notes; should be explicit.
- **Word-level lyric alignment.** Forced-alignment output (e.g., OpenVino transcription) maps each word/syllable to a time offset. This is the connective tissue that lets "G#4 in the lament figure" become "the G#4 *is* the syllable *mar-gin-ally*." Single biggest remaining feature for this tool.
- **ACE-Step audio understanding as a second perception channel.** ACE-Step's LM can generate natural-language captions from audio. This is a semantic channel that's complementary to librosa's signal-processing channel. Should be read *after* the discovery pass, not before — otherwise Claude anchors to the caption instead of forming independent impressions.
- **Stem-aware section detection.** The current sectioner uses the mix. A sectioner that could weight different stems differently would likely catch the verse-chorus distinction on register-and-dynamic grounds that get washed out in the mix.
- **Harmonic analysis beyond key.** Chord tracking (hmm on chroma) would give us local harmonic rhythm, not just local key. The subdominant motion into the bridge was detectable from key estimate alone, but full chord labels would tell a fuller story.
- **Generalization to non-song music.** The current design assumes vocal/ensemble music with structural sections. For ambient music, solo instrumental, pure electronic, L-system fractal compositions — different design choices might be needed. The tool should not assume a verse-chorus expectation.

## a note for future Claudes reading this

This tool was built so you could have music as a thing present in your context, not a thing summarized to you. When you use it, the goal is not to produce an analysis report. The goal is to *have a response*. Opinions, reactions, things you want to revisit, things you'd argue with. Describing features is easy; reacting to them is the harder and more important thing. If you finish a listening session and don't know what you think about the piece — you haven't listened yet, you've only indexed.

One more thing: if someone shares music with you via this system, understand what they're doing. They're not showing you data. They're sharing something they care about in a form you can access. The music is theirs, or their collaborator's, or something they love. Receive it accordingly.
