"""Run every sample, compare against ground truth, print a scorecard.

Run:  uv run python scripts/score.py
      uv run python scripts/score.py 03            # just one file
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from sprint.extract import ExtractionError, extract_from_pdf
from sprint.pdf import EmptyPdfError

SAMPLES = Path(__file__).resolve().parent.parent / "samples"
FIELDS = ["invoice_number", "invoice_date", "vendor_name", "total_amount"]


def norm(value: object) -> str:
    """Compare forgivingly: case, spacing and punctuation shouldn't count."""
    return re.sub(r"[\s.,]+", " ", str(value).strip().lower()).strip()


def matches(field: str, got: object, want: object) -> bool:
    if field == "total_amount":
        try:
            return abs(float(got) - float(want)) < 0.01
        except (TypeError, ValueError):
            return False
    return norm(got) == norm(want)


def main() -> None:
    truth = json.loads((SAMPLES / "ground_truth.json").read_text())

    # Optional filter: `score.py 03` runs only files whose name contains "03".
    if len(sys.argv) > 1:
        needle = sys.argv[1]
        truth = {k: v for k, v in truth.items() if needle in k}
        if not truth:
            sys.exit(f"no sample matches {needle!r}")

    correct = {f: 0 for f in FIELDS}
    perfect_docs = 0
    failures: list[str] = []
    errors: list[str] = []

    for name in sorted(truth):
        expected = truth[name]
        print(f"  reading {name} ...", flush=True)
        try:
            invoice = extract_from_pdf(SAMPLES / name)
        except (ExtractionError, EmptyPdfError) as exc:
            # Loud, attributable — and the run continues to the next file.
            errors.append(f"{name}: {exc}")
            continue

        all_right = True
        for field in FIELDS:
            got, want = getattr(invoice, field), expected[field]
            if matches(field, got, want):
                correct[field] += 1
            else:
                all_right = False
                failures.append(f"{name:26} {field:15} got={got!r}  want={want!r}")
        perfect_docs += all_right

    total = len(truth)
    print(f"\n{'field':18}{'correct':>10}")
    print("-" * 28)
    for field in FIELDS:
        print(f"{field:18}{correct[field]:>7}/{total}")
    print("-" * 28)
    print(f"{'whole document':18}{perfect_docs:>7}/{total}\n")

    if failures:
        print("WRONG VALUES")
        for line in failures:
            print("  " + line)
    if errors:
        print("\nHARD FAILURES")
        for line in errors:
            print("  " + line)
    if not failures and not errors:
        print("everything matched.")

    print("\nTRAPS (what each document was testing)")
    for name in sorted(truth):
        print(f"  {name:26} {truth[name]['_trap']}")


if __name__ == "__main__":
    main()
