"""Re-align OpenVino timings to mix time by adding the offset.
Also verify by checking a bunch of landmarks against what we know from the full-mix pyin analysis."""
from pathlib import Path

LYRICS_PATH = Path(r"D:\Claude Squad\Home\Obbligato\claudio\minute_manager_case_study\minute_manager_files\lyrics_precise.txt")
OFFSET = 2.44  # seconds; vocal stem starts at 2.44s of silence then "Ahem!"

entries = []
with open(LYRICS_PATH, "r", encoding="utf-8") as f:
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) >= 3:
            try:
                entries.append((float(parts[0]), float(parts[1]), parts[2]))
            except ValueError:
                pass

print(f"Applying +{OFFSET}s offset to convert stem-time to mix-time...\n")

keys = ["margin", "first", "rate... ah", "tremble", "thou", "canst", "seize", "violation", "heroism"]
print("KEY MOMENTS — corrected to mix time:")
for start, end, text in entries:
    tl = text.lower()
    if any(k in tl for k in keys):
        print(f"  stem:{start:7.3f}s  ->  mix:{start+OFFSET:7.3f}s  |{text}|")

# Save corrected alignment
out_path = Path(r"D:\Claude Squad\Home\Obbligato\claudio\minute_manager_case_study\alignment_mix_time.txt")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(f"# Timestamps corrected from vocal-stem time to full-mix time by adding {OFFSET}s offset\n")
    f.write(f"# Format: mix_start\\tmix_end\\ttext\n")
    for start, end, text in entries:
        f.write(f"{start+OFFSET:.3f}\t{end+OFFSET:.3f}\t{text}\n")
print(f"\nwrote: {out_path}")

# Print section assignments with corrected times
SECTIONS = [
    (0.00,  25.98, "S1 quiet G major"),
    (25.98, 70.24, "S2 moderate G minor"),
    (70.24, 80.92, "S3 moderate G major"),
    (80.92, 104.58,"S4 moderate G minor"),
    (104.58,124.60,"S5 strong G minor"),
    (124.60,162.26,"S6 moderate G minor"),
    (162.26,177.68,"S7 strong G minor"),
    (177.68,187.78,"S8 moderate C minor"),
    (187.78,207.28,"S9 strong G major"),
]

print("\n=== SECTION ASSIGNMENTS WITH CORRECTED TIMING ===")
from collections import defaultdict
by_section = defaultdict(list)
for start, end, text in entries:
    mix_t = start + OFFSET
    for ss, se, lbl in SECTIONS:
        if ss <= mix_t < se:
            by_section[lbl].append((mix_t, text))
            break

for ss, se, lbl in SECTIONS:
    items = by_section[lbl]
    if items:
        # Show first and last word
        first = items[0][1].strip()
        last = items[-1][1].strip()
        mid = " ... "
        if len(items) > 4:
            middle_words = " ".join(t.strip() for _, t in items[1:len(items)//2]).strip()[:60]
            print(f"  {lbl} ({ss:.1f}-{se:.1f}s):")
            print(f"    starts with: '{first}'")
            print(f"    middle:      '{middle_words}...'")
            print(f"    ends with:   '{last}'")
        else:
            all_text = " ".join(t.strip() for _, t in items).strip()
            print(f"  {lbl} ({ss:.1f}-{se:.1f}s): '{all_text}'")
    else:
        print(f"  {lbl} ({ss:.1f}-{se:.1f}s): (no vocal content)")
