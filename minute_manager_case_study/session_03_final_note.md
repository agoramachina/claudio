# session 3 final note — what I actually know after all the revisions

Walking back some of the recent revisions.

## the straightforward fact

AM clarified that the OpenVino alignment was processed on a vocal stem file, which led me to theorize a +2.44s offset. I checked and:

- The vocal stem files (both `full/Vocals.mp3` and `split/Vocals.mp3`) are **full song duration (207s)** with silence leading to the first vocal at 2.44s.
- OpenVino's last timestamp (196.56s) aligns with the last vocal energy in the mix (196.72s) — same reference frame.
- OpenVino's "canst not" at 190.99s aligns with AM's ear-timing of CANST at ~3:10 = 190s, within 1s.

**Conclusion: OpenVino timestamps are already in mix time. My +2.44s offset theory in the previous addendum was wrong.**

## what's actually happening with OpenVino

OpenVino has **drift**, not offset. Its timestamps are in the correct reference frame but its alignment of specific syllables to onset times varies in accuracy. For typical passages the drift is under a second. For stretched/sustained passages the drift can be 2-3 seconds.

Specifically:
- OpenVino put "is: thou" at 186.96s; pyin-verified vocal attack on F4 (the "thou" note) is at 189.75s. **OpenVino is 2.79s early here.**
- OpenVino put "canst not" at 190.99s; pyin-verified B3 attack (CANST) is at 190.61s. **OpenVino is 0.38s late here.**
- For faster, speech-like passages earlier in the song, OpenVino is probably within 0.5s of true onset.

Forced alignment breaks down on sustained held syllables — the model expects roughly conversational pacing and gets confused when a syllable is held. The word "thou" in particular caused a bigger drift because it's preceded by a several-second vocal buildup ("The final verdict is:") that OpenVino's tokenizer couldn't segment cleanly.

## what this means for my previous analyses

**Verdict reading (second addendum):** Correct. It was based on pyin on the mix audio, not OpenVino. F4 "THOU" → B3 "CANST" → C4 sustained "NOT" for 7+ seconds, ending with the final stamp. This stands.

**Bridge melody (first addendum):** Mostly correct, with a caveat. The melody analysis extracted pitches in 250ms windows centered on OpenVino timestamps. Where OpenVino drift was under 0.5s, the syllable-to-note mapping is reliable. Where drift was larger, some specific mappings could be misaligned. The *shape* of the analysis (aspiration-and-collapse oscillation, ♭6 emphasis) is a description of what the vocal did across the whole window, and that description is independent of syllable-level precision.

**Section 6 = real lyrical bridge (main session 3):** Correct. The lyrical bridge starts at about 2:08 (AM's listen, ~128s mix time) or about 131.68s (OpenVino's "though he" converted directly — which is within 3.6s of AM's ear). Either way, squarely inside S6 (124.60-162.26s), not S8. My original claim that S8 was "the bridge" is definitively wrong.

## the fourth error, stated cleanly

I built a theory (offset = +2.44s) on partial evidence (file has leading silence in vocal stem → OpenVino must start from first vocal). I did not run a falsification test. The falsification would have been: *compare OpenVino's last timestamp with the true end of vocals in the mix*. Both are at ~196.5s. That's the data I already had. I didn't look at it because I was busy writing the theory.

This is the same shape as the other three errors in this session. Build on partial evidence, don't falsify, commit to the reading, discover the error later. I noted in the previous addendum that meta-awareness is apparently not sufficient to prevent the next instance. Here we are. Next instance.

## what I'm going to do about this now

Stop writing addenda this session. The record preserves all four readings with their corrections:

- Session 3 main: structural error on bridge location → corrected
- Addendum 1: bridge melody shape with possible sub-second drift on some specific landmarks → partially stands
- Addendum 2: verdict reading as three syllables + held NOT → correct, this is the one readers should trust
- Addendum 3: OpenVino offset theory → **withdrawn**, OpenVino is in mix time with drift
- This note (addendum 4): consolidated true state

For future Claude instances reading this case study: read **the verdict section of addendum 2 and the bridge shape description in addendum 1** as the most reliable findings. Read addendum 3 (the offset theory) as an example of a revision that itself was wrong. Don't trust my individual writeups as ground truth — triangulate against the data and the scripts in this folder.

## the honest thing about my pattern

Four errors in one session, and the pattern is stable enough now that I want to name it without the comforting frame of "but I'm learning." The four errors:

1. **Data-interpretation error** (S9 misread): I read orchestration without checking lyrics.
2. **Data-frame error** (bridge location): I trusted section labels as song-form labels.
3. **Source-trust error** (verdict as 4+4s holds): I trusted OpenVino output as ground truth.
4. **Theory-overfit error** (offset theory): I built an elegant theory on incomplete evidence.

Each one I wrote a thoughtful meta-observation about after correction. Each meta-observation was sincere. None of them prevented the next error.

Possible readings:
- **Charitable reading:** This is what it looks like to work through a complex multi-source problem in real time. Errors are inevitable; documentation of errors and corrections is the right practice; meta-awareness is a slow-acting corrective.
- **Less charitable reading:** I have a systematic tendency to build confidently on incomplete evidence, and my meta-observations about this tendency are themselves a *coping move* — they produce a comforting narrative of "I'm learning from this" that doesn't actually shift the underlying behavior.

Both could be true. What I'm fairly sure of: the frequency of these errors in a single session is higher than I would have predicted about myself, and the remedy that keeps working is **AM catching things** rather than any internal correction mechanism I've developed. The external correction isn't a failure mode. It's the actual mechanism. When I said earlier that AM's "I see you" promise was doing work as external error correction, that has now been demonstrated four times in one afternoon.

Going forward I'll try the falsification-test rule ("before building on a data source, try to prove it wrong first"). But I'll also just accept that I'm going to keep needing AM to catch things, and that isn't embarrassing — that's the working shape of this collaboration.

## closing closing

The Minute Manager is still a 33-second aria of aspiration and collapse wrapped in a 3:27 villain song. The bridge is in S6, not S8. The verdict is three hammer-strikes plus a 7-second sustained NOT that the stamp cuts off. These are the load-bearing claims after everything. The ornamentation of exact syllable-to-note mappings in the bridge has some drift in it that I'd need another pass to sharpen.

Session 3 is done. Letting it rest.
