"""
Parse lyrics_precise.txt and examine the word-to-time alignment.
Map syllables to the section boundaries and specific musical moments.
"""
from pathlib import Path

LYRICS_PATH = Path(r"D:\Claude Squad\Home\Obbligato\claudio\minute_manager_case_study\minute_manager_files\lyrics_precise.txt")

# Section boundaries from earlier analysis
SECTIONS = [
    (0.00,  25.98, "S1 quiet G major - spoken intro"),
    (25.98, 70.24, "S2 moderate G minor - verse 1"),
    (70.24, 80.92, "S3 moderate G major - chorus 1 tail / spoken interruption"),
    (80.92, 104.58, "S4 moderate G minor - verse 2"),
    (104.58,124.60, "S5 strong G minor - chorus 2"),
    (124.60,162.26, "S6 moderate G minor - bridge setup"),
    (162.26,177.68, "S7 strong G minor - climax / pre-bridge"),
    (177.68,187.78, "S8 moderate C minor - BRIDGE"),
    (187.78,207.28, "S9 strong G major - outro / verdict"),
]

def parse_alignment(path):
    entries = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t")
            if len(parts) >= 3:
                try:
                    start = float(parts[0])
                    end = float(parts[1])
                    text = parts[2]
                    entries.append((start, end, text))
                except ValueError:
                    pass
    return entries

def section_for_time(t):
    for start, end, label in SECTIONS:
        if start <= t < end:
            return label
    return "?"

entries = parse_alignment(LYRICS_PATH)
print(f"parsed {len(entries)} aligned entries")
print(f"first: {entries[0]}")
print(f"last:  {entries[-1]}")
print()

# Group by section
from collections import defaultdict
by_section = defaultdict(list)
for start, end, text in entries:
    by_section[section_for_time(start)].append((start, end, text))

for label, _, _ in [(l, s, e) for s, e, l in SECTIONS]:
    pass

# Print per-section summary
for sstart, send, label in SECTIONS:
    items = by_section[label]
    if items:
        joined = "".join(t for _, _, t in items).strip()
        print(f"=== {label} ({sstart:.1f}-{send:.1f}s) — {len(items)} entries ===")
        # First words and last words to show boundaries
        first = " ".join(t.strip() for _, _, t in items[:6])
        last = " ".join(t.strip() for _, _, t in items[-6:])
        print(f"  starts: {first!r}")
        print(f"  ends:   {last!r}")
    else:
        print(f"=== {label} — EMPTY ===")

# Save section-grouped alignment for the notes doc
out_path = Path(r"D:\Claude Squad\Home\Obbligato\claudio\minute_manager_case_study\alignment_by_section.txt")
with open(out_path, "w", encoding="utf-8") as f:
    for sstart, send, label in SECTIONS:
        items = by_section[label]
        f.write(f"=== {label} ({sstart:.2f}-{send:.2f}s) ===\n")
        for start, end, text in items:
            f.write(f"  {start:7.3f} - {end:7.3f}  |{text}|\n")
        f.write("\n")
print(f"\nwrote: {out_path}")
