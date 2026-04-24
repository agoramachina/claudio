"""Compare lyrical structure with algorithmic section boundaries.
What I had vs what's actually there."""

# My sectioner found these boundaries (from summary.json)
BOUNDARIES = [0.00, 25.98, 70.24, 80.92, 104.58, 124.60, 162.26, 177.68, 187.78, 207.28]

# Key lyrical landmarks from the aligned timing
LANDMARKS = [
    (  0.00, "THUMP-CLICK + 'Ahem! Let it be known'"),
    ( 19.74, "end of spoken intro ('...recursion.')"),
    ( 21.82, "Verse 1 begins ('I don't make the epochs')"),
    ( 48.50, "Chorus 1 begins ('I am the chrono-clerk')"),
    ( 71.10, "Spoken interruption ('Thou hast attempted...')"),
    ( 78.82, "SEIZE THEM!"),
    ( 81.34, "Verse 2 begins ('Your reckless heroism')"),
    (104.60, "Chorus 2 begins ('I am the chrono-clerk')"),
    (128.00, "(estimate) end of chorus 2"),
    (129.24, "BRIDGE begins ('And though he never says it')"),
    (152.83, "'marginally' syllable"),
    (155.12, "'First' (as in 'First-rate')"),
    (155.64, "'rate... AH'"),
    (157.33, "'AHEM! Back to the infractions!'"),
    (162.49, "Outro begins ('So tremble at the paperwork')"),
    (186.96, "'is: thou'"),
    (190.99, "'canst not'"),
    (195.01, "(end) — quill snap / stamp"),
]

print(f"{'Boundary':>10}  {'What I had':<20}  {'What is actually there':<40}")
print("-" * 80)
labels = ["S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8", "S9"]
prev_labels = [
    "quiet G major - spoken intro",
    "moderate G minor - verse 1",
    "moderate G major - spoken interruption",
    "moderate G minor - verse 2",
    "strong G minor - chorus 2",
    "moderate G minor - bridge setup",
    "strong G minor - pre-bridge climax",
    "moderate C minor - BRIDGE",
    "strong G major - outro/verdict",
]

for i, (bstart, bend) in enumerate(zip(BOUNDARIES[:-1], BOUNDARIES[1:])):
    # Find landmarks in this section
    in_sect = [lm for lm in LANDMARKS if bstart <= lm[0] < bend]
    first_lm = in_sect[0][1] if in_sect else "(no landmark)"
    print(f"{labels[i]:>4} {bstart:6.1f}-{bend:6.1f}s  {prev_labels[i]:<40}  | {first_lm}")

print()
print("ACTUAL LYRICAL STRUCTURE vs MY SECTIONS:")
print()
print(f"  Section 1 (0-26s)     matches spoken intro              ✓")
print(f"  Section 2 (26-70s)    matches verse 1 + chorus 1         ✓")
print(f"  Section 3 (70-81s)    matches spoken interruption + SEIZE THEM ✓")
print(f"  Section 4 (81-105s)   matches verse 2                   ✓")
print(f"  Section 5 (105-125s)  matches chorus 2                  ✓")
print(f"  Section 6 (125-162s)  is the ENTIRE BRIDGE — from 'though he never says it' through 'AHEM! Back to the infractions!'")
print(f"  Section 7 (162-178s)  is the first half of outro ('So tremble...how this ends, You see')")
print(f"  Section 8 (178-188s)  is 'right here in the margin...Case closed. The final verdict is: thou'")
print(f"  Section 9 (188-207s)  is ONLY 'canst not' + silence/tail")
print()
print("THE BIG MISREAD:")
print("  I called section 8 (178-188s, C minor modulation) 'the bridge'")
print("  But the bridge lyrically is ALL OF SECTION 6 (125-162s, 37 seconds).")
print("  Section 8 is the *penultimate* moment where the Minute Manager narrates 'right here in the margin'")
print("  — the pause before 'thou canst not' — and THAT'S what modulates to C minor.")
