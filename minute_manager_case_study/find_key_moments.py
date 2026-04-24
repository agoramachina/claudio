"""Find key lyrical moments and their actual timestamps."""
from pathlib import Path

LYRICS_PATH = Path(r"D:\Claude Squad\Home\Obbligato\claudio\minute_manager_case_study\minute_manager_files\lyrics_precise.txt")

entries = []
with open(LYRICS_PATH, "r", encoding="utf-8") as f:
    for line in f:
        parts = line.rstrip("\n").split("\t")
        if len(parts) >= 3:
            try:
                entries.append((float(parts[0]), float(parts[1]), parts[2]))
            except ValueError:
                pass

# Key phrases and their actual timestamps
keys = ["margin", "first", "rate", "ahem", "tremble", "thou", "canst", "case closed", "verdict", "seize", "violation", "heroism"]
print("KEY MOMENTS — actual timing from alignment:")
print()
for start, end, text in entries:
    tl = text.lower()
    if any(k in tl for k in keys):
        print(f"  {start:7.3f}s  |{text}|")
