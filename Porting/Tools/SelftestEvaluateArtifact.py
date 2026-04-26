#!/usr/bin/env python3
from __future__ import annotations

from EvaluateArtifact import is_candidate_hint


def expect(name: str, actual: object, expected: object) -> None:
    if actual != expected:
        raise AssertionError(f"{name}: expected {expected!r}, got {actual!r}")


def main() -> int:
    true_cases = ["candidate", "Candidate", "yes", "YES", "ready", " ready "]
    false_cases = ["", "no", "unknown", "blocked", "candidate-ish"]

    for value in true_cases:
        expect(f"candidate_hint:{value}", is_candidate_hint(value), True)

    for value in false_cases:
        expect(f"candidate_hint:{value}", is_candidate_hint(value), False)

    print("evaluate-artifact-selftest=ok")
    print(f"case_count={len(true_cases) + len(false_cases)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
