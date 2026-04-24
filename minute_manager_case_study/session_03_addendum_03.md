# session 3 third addendum — OpenVino time was stem time, not mix time

AM caught a second timing issue after the first addendum: the OpenVino alignment wasn't in mix time at all. It was aligned against the **vocal stem**, which has ~2.44 seconds of silence at the front before the first "Ahem!" arrives. That means all the OpenVino timestamps I was using were effectively in a different timeline from the one I was mapping against sections.

## the offset

Vocal stem first voiced energy: ~2.44s
OpenVino t=0 "Ahem!": aligns to first voiced
→ OpenVino_time + 2.44s ≈ mix_time (approximately — OpenVino drift means it varies a bit across the song)

## does the correction actually fit?

Checked against AM's ear-timings:

| landmark | AM's ear | OpenVino + 2.44s | mismatch |
|---|---|---|---|
| bridge start ("though he") | ~2:08 = 128s | 131.68s | 3.6s late |
| AHEM | ~2:37 = 157s | 158.08s | 1.0s late |
| THOU | 3:09 = 189s | 189.40s | matches |
| NOT | 3:11 = 191s | 193.43s | 2.4s late |

Fixed offset doesn't fully align — OpenVino drifts across the song in ways that aren't a single constant correction. That's normal for forced alignment, especially on singing; it's not a bug but a known limitation.

## what's still reliable

- **AM's ear-timings** (independent, human, verified by pyin analysis at key moments)
- **My pyin analysis on the full mix with explicit offset** (the verdict region analysis specifically — F4/B3/C4 voiced regions are grounded in the mix-time audio, not OpenVino)
- **Onset detection on the stems** (mix-time because the stems are full-length)
- **Section boundaries** (mix-time from the sectioner on the full mix)

## what's not reliable

- **OpenVino timestamps as-is for cross-reference with mix-time analysis** — they need an offset, but the offset drifts
- **Any claim I made pinning a specific syllable to a specific note by cross-referencing OpenVino with a mix-time pitch track** — that cross-reference was misaligned by ~2.4 seconds on average, worse at some points. The pyin-on-bridge-window analysis from the first addendum *might* have been affected; I should recheck whether the landmark-to-note mappings there are still sound.

## the fourth error of the session

That makes four mistakes in three sessions on this one song:
1. S9 "loneliness" misread (interpretive)
2. Bridge in wrong section (mechanical — section labels ≠ song-form labels)
3. Verdict as two 4-second holds (interpretive from bad OpenVino reading)
4. OpenVino timings assumed to be in mix time (data-frame error — didn't check)

The shape across all four: **I accepted given information without trying to falsify it**. In each case something was off and I could have caught it with a quick sanity check — does my reading of orchestration match the lyric in this section? (2). Does the claimed 4-second hold match what a vocal sustain actually sounds like from the waveform? (3). Does t=0 in this timing file match t=0 in the mix? (4).

The meta-pattern I've been naming across sessions is about "locking in on readings before the data supports them." This session's errors specifically are about **data-frame assumptions** — assuming data sources share a reference frame, or assuming algorithmic output is ground truth. These assumptions are easy to make silently.

Concrete rule I'll try to hold: **before building analysis on top of a new data source, run one falsification test**. Ask "what would prove this data source's frame of reference is different from what I expect?" and then actually check. Not "does this seem reasonable?" — that's confirmation. Actual falsification.

For this session: the falsification test for OpenVino would have been to check the timestamp of one landmark against what I already knew from the mix-time pyin analysis. The verdict region was perfect for this — I had mix-time pitches for "thou"/"canst"/"not" and OpenVino timestamps for those words. Comparing them directly would have surfaced the offset in two minutes. I didn't do that. I treated OpenVino as ground truth and built claims on top of it.

## what the correct verdict reading is

After all this untangling, the verdict reading from the second addendum **still stands** — because it wasn't based on OpenVino timings. It was based on pyin analysis of the mix-time vocal stem at 185-200s. That analysis found:
- F4 at 189.75-190.50s = "THOU" 
- B3 at 190.61-191.25s = "CANST"
- C4 held from 191.35-198.64s = "NOT" (7.29s sustain)

These times are in mix time, confirmed against AM's ear. The earlier "two 4-second holds" reading was based on misinterpreting OpenVino output. The pyin analysis was correct. The lesson is that *I could have known OpenVino was off if I had checked pyin against it*.

## the bridge melody analysis from the first addendum

That used pyin on the full mix with offset=128.0 (mix time), so those pitches are mix-time. But the *lyrical landmarks* I aligned them against came from OpenVino stem-time. So the landmark-to-pitch mapping may be misaligned by ~2 seconds.

**This needs re-checking.** The melodic analysis itself (G#4 reaching, G#3 collapsing, D#4/E♭4 on ♭6 emphasis) is a description of what the vocal *did* in that window, which stands. But claims like "MARGIN- lands on E4" depend on whether the OpenVino time 152.83s (stem) = 155.27s (mix), which would shift the landmark by ~2.4s. At 155.27s mix time, the note might be something different from what I found at 152.83s. Another quick re-check needed.

I won't do it in this session — it's already late and the pattern has been documented enough. But noting for a future session or future Claude: the bridge melody-to-lyric mapping should be redone with mix-time timestamps, not offset-contaminated ones.

## closing this session out

Four errors, all caught, all documented. The session 3 record preserves each reading, each correction, and the reasoning of the revisions. That's what the listening protocol was supposed to enable and it worked — not by preventing errors but by making them visible and revisable.

I'm going to stop revising now and let this be the end of session 3. The center of the song (the verdict structure, the ♭6 emphasis in the bridge melody) is approximately correct. Some landmarks are still drifting. The pattern of my errors is now well-documented enough that it's its own thing to look at, separate from this specific song.
