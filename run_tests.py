"""run_tests.py - runs every sample in test_errors.txt and reports the match rate.
Samples are separated by a line containing only -----
Run with:  python run_tests.py
"""
from pathlib import Path

from matcher import analyze

text = Path(__file__).with_name("test_errors.txt").read_text(encoding="utf-8")
cases = [c.strip() for c in text.split("-----") if c.strip()]

hits = 0
for i, case in enumerate(cases, 1):
    result = analyze(case)
    last_line = case.splitlines()[-1]
    if result["matched"]:
        hits += 1
        print(f"[OK]   {i:>2}. {last_line}")
    else:
        print(f"[MISS] {i:>2}. {last_line}")

if cases:
    print(f"\n{hits}/{len(cases)} matched ({hits / len(cases):.0%})")
else:
    print("No test cases found.")
