# session 3 second addendum — the verdict is back-loaded, and OpenVino was wrong

Thanks to AM flagging that their own listening gives THOU/CANST/NOT at 3:09/3:10/3:11 — different from what I'd computed from OpenVino — I went back to the vocal stem and re-checked at high resolution. The result revises my verdict reading and catches an important limitation of forced-alignment data.

## what actually happens in the verdict region (185-200s)

Using high-resolution pyin (hop=256) and onset detection on the isolated vocal stem, the voiced regions are:

| time | dur | note | lyric (revised) |
|---|---|---|---|
| 185.00-185.68 | 0.68s | G#4 | "You lose" |
| 185.72-185.87 | 0.15s | G4 | "Case" |
| 186.00-186.46 | 0.46s | E4 | "closed" |
| 186.52-187.88 | 1.36s | D4 | "The final" |
| 188.11-189.49 | 1.38s | D4 | "verdict is:" |
| **189.75-190.50** | **0.75s** | **F4** | **"THOU"** |
| **190.61-191.25** | **0.64s** | **B3** | **"CANST"** |
| **191.35-198.64** | **7.29s** | **C4** | **"NOT"** (held) |
| 199.27-199.88 | ~0.5s | G3 | final tail vocalization |

The three verdict syllables are at 189.75, 190.61, and 191.35 — about 1 second apart — which matches AM's ear-timestamps of 3:09/3:10/3:11 within a quarter-second. AM's listening is accurate.

## what I had wrong

My session 3 writeup said "thou held for ~4 seconds, canst not held for ~4 seconds." That was based on OpenVino's timestamps, which placed "is: thou" at 186.96s and "canst not" at 190.99s. The ~4-second gap between those OpenVino entries I interpreted as *the duration of "thou" being held*.

Wrong interpretation of what OpenVino was giving me. OpenVino labels word-onsets but can drift when faced with *sustained syllables* and *dramatic pacing changes*. In this case OpenVino placed "thou" at 186.96s, which is actually during the held D4 singing "verdict is:" — the actual word "thou" doesn't arrive until 189.75, three seconds later. OpenVino mismatched the text to the audio because it got confused by the sustain.

The ~4-second gap between "is: thou" and "canst not" in OpenVino's output is not the duration of "thou." It's the combined duration of *the remainder of "verdict is:"* plus *silence* plus *"thou"* plus *the pause between "thou" and "canst."* OpenVino gave me a gap that my reading collapsed into a held note that wasn't there.

## what the verdict actually is

Three sharp punctuation-syllables at ~1-second intervals:
- **THOU** on F4 (~0.75s)
- **CANST** on B3 (~0.65s)
- **NOT** on C4 **held for 7.29 seconds**

The verdict is *back-loaded*, not front-loaded. "Thou" and "canst" are fast. The sustain — the place where the Minute Manager savors his own verdict — is on **"NOT."** Seven-plus seconds. The denial itself is where he lives. The piece ends when that sustain cuts off, apparently into the final THUMP-CLICK stamp.

That changes the reading considerably. It's not ceremony stretched evenly across "thou canst not." It's three hammer-strikes *then* a sustained denial-drone that lasts until the mechanism of the stamp itself cuts it off.

## the harmonic detail is also interesting

The three verdict pitches — F4, B3, C4 — are not in the minor key the body of the song has been in. In G major (my section 9's key estimate):
- F4 = ♭7 (modal flavoring, perhaps blue/dominant)
- B3 = ♮3 (the major third, signals G major)
- C4 = 4 (suspended fourth, wants to resolve downward to B3)

So the verdict melody does in fact shift into G major territory (the ♮3 confirms it), but the final held note is a *suspended fourth that never resolves vocally*. The resolution is given to the THUMP-CLICK. The stamp completes the cadence.

That's a genuinely strange musical choice. Songs usually end with the singer landing on a stable note. This one ends with the singer on an unstable note (C4 suspended against an implied G major) and lets the *sound effect* be the resolution. Which is, structurally, the same joke the entire song has been making — the Minute Manager's word is not the final word; the *paperwork* is. The stamp finishes his sentence.

## what I learned about OpenVino specifically

Forced-alignment works best on normal speech with normal pacing. It handles sung text okay. It breaks down when:
- syllables are held substantially longer than normal speech (drifts)
- there's silence between stressed words (may collapse or expand)
- there are dramatic pacing changes (early/late labels)

Practical implication for the tool: when timing data is from forced alignment, **cross-check at least one landmark against ear-timestamps** before trusting syllable-precise claims. If there's a mismatch, trust the ear for dramatic/sustained passages and trust the machine for conventional-pacing passages. My "thou held for 4 seconds" was a failure to sanity-check.

## what I learned about AM's flag

AM said upfront in this iteration: "don't assume for a fact that I'm giving you the correct stuff." Then turned out that AM's timing was right and the machine timing was wrong. Double lesson:

1. The warning was itself correct — don't assume the human-source is right. Good practice.
2. But also: in this case, the human-source was actually more reliable than the machine-source. AM's ear caught something OpenVino's algorithm didn't. The warning isn't "humans are less reliable than machines" — it's "every source is fallible, check each one."

Going forward: ear-timestamps, machine timestamps, and signal-processed ground truth (pyin + onset detection on the stem directly) are three different sources, and for the interesting moments the right move is to triangulate all three rather than trust any one of them.

## what this doesn't change

The aspiration-and-collapse melody analysis from the first addendum still holds. That was grounded in re-pitch-tracking the actual bridge window, not in OpenVino. The bridge melody is still oscillating G#3 → G#4 → G#3 at those key moments. That analysis stands.

What does change: the verdict reading moves from "two equal 4-second holds" to "three hammer-strikes plus a 7-second sustained NOT." Which is, I have to say, better. The *asymmetry* of the verdict — short sharp sharp LONG — is more musically striking than even spacing. It's a more specific portrait. The Minute Manager isn't giving equal weight to "thou," "canst," and "not." He's holding *the refusal* as if it's the whole song. Which it is.

## third error in three sessions, different kind

1. Session 1-2: interpretive error (S9 loneliness vs. authority). Corrected by AM.
2. Session 2-3: mechanical error (wrong bridge location). Corrected by alignment data.
3. Session 3 within-session: data-trust error (trusted OpenVino over ear-ground-truth). Corrected by AM flagging and re-checking against the stem.

All three involved me *locking in on a reading* before I had reason to trust it. The shape of the error is stable: I want to *believe* the reading I have. Noticing this is... not new. Fourth time noticing it in one case study. At some point the meta-observation becomes its own pattern that itself needs looking at.

What I'll carry from this specifically: **when working with aligned data, hold every landmark as provisional until at least one other source confirms it.** One source for a landmark is not confirmation; it's input. Two sources agreeing is confirmation. Three sources is robust. The work of this session demonstrated that some claims I made with only one source turned out wrong; the claims backed by multiple sources (pyin on the bridge window, which I verified with both the voiced-region analysis and the word-level lyric text) are the ones that held.

No errors are catastrophic. All are correctable. The point isn't to eliminate them — it's to keep the practice of revision live, which I'm doing, and AM keeps supporting.
