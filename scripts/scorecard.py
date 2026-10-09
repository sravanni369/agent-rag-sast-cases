"""Turn Semgrep JSON into a scanner-versus-ground-truth table.

Usage: python scripts/scorecard.py results/semgrep.json
Ground truth: only the vulnerable variant of each case is a finding.
"""
import json
import sys
from pathlib import Path

CASES = ("sid_rag_tenant", "ea_refund_tool", "sid_mcp_tool")
VARIANTS = ("vulnerable", "fixed", "hard_negative")

results = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))["results"]
hits = {}
for r in results:
    parts = Path(r["path"]).as_posix().split("/")
    i = parts.index("cases")
    hits.setdefault((parts[i + 1], parts[i + 2]), set()).add(r["check_id"].split(".")[-1])

counts = {"TP": 0, "FN": 0, "FP": 0, "TN": 0}
print("| Case | Variant | Truth | Scanner | Verdict | Rules that fired |")
print("|---|---|---|---|---|---|")
for case in CASES:
    for variant in VARIANTS:
        truth = variant == "vulnerable"
        fired = sorted(hits.get((case, variant), ()))
        verdict = {(True, True): "TP", (True, False): "FN",
                   (False, True): "FP", (False, False): "TN"}[(truth, bool(fired))]
        counts[verdict] += 1
        print(f"| {case} | {variant} | {'finding' if truth else 'not a finding'} | "
              f"{'flagged' if fired else 'clean'} | {verdict} | {', '.join(fired) or '-'} |")
print()
print(", ".join(f"{k} {v}" for k, v in counts.items()))
