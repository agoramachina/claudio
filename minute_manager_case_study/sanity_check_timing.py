"""Look at the start and end of the lyrics_precise.txt to see what OpenVino said the timing was."""
path = r"D:\Claude Squad\Home\Obbligato\claudio\minute_manager_case_study\minute_manager_files\lyrics_precise.txt"

with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

print(f"total lines: {len(lines)}")
print("\nfirst 10 lines:")
for i, ln in enumerate(lines[:10]):
    print(f"  [{i}] {ln.rstrip()!r}")

print("\nlast 10 lines:")
for i, ln in enumerate(lines[-10:]):
    print(f"  [{len(lines)-10+i}] {ln.rstrip()!r}")

# Now look at what AM's ear-timing says versus where these land in the audio
# AM: "thou canst not" happens around 3:09-3:11 in mix time
# OpenVino puts THOU at 186.96s (which is 3:06.96)
# Full mix thou-singing (from pyin) is at 189.75s (which is 3:09.75)

print("\n\nKEY COMPARISON:")
print(f"  AM's ear: THOU at 3:09 = 189s")
print(f"  OpenVino 'is: thou': 186.96s")
print(f"  My pyin analysis: F4 vocal onset at 189.75s")
print(f"  Difference: OpenVino is 2.79s EARLIER than pyin-verified THOU")

print(f"\n  AM's ear: NOT at 3:11 = 191s")
print(f"  OpenVino 'canst not' onset: 190.99s (which would be AM's CANST, not NOT)")
print(f"  My pyin analysis: C4 vocal onset (held NOT) at 191.35s")
print(f"  Difference: OpenVino 'canst not' at 190.99 actually aligns with CANST starting at 190.61 via pyin")

print("\n\nCONCLUSION:")
print("  If OpenVino labels match AM's ear-timing when we interpret 'canst not' as the CANST onset,")
print("  and the last timestamp (~196.56s) matches last vocal energy (~196.72s),")
print("  then OpenVino IS in mix time — NO offset needed.")
print("  But OpenVino's onset timing is ~2-3 seconds EARLY at some landmarks (like 'thou' at 186.96 vs actual 189.75).")
print("  This isn't offset — this is drift / alignment error within the forced-alignment process itself.")
