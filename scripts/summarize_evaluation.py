from __future__ import annotations

import csv
from collections import Counter, defaultdict
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_ROOT
    / "results"
    / "raw"
    / "evaluation_results.csv"
)


def as_bool(value: str) -> bool:
    return value.strip().lower() == "true"


def percent(
    numerator: int,
    denominator: int,
) -> float:
    if denominator == 0:
        return 0.0

    return round(
        numerator / denominator * 100,
        2,
    )


def main() -> None:
    with INPUT_FILE.open(
        "r",
        newline="",
        encoding="utf-8",
    ) as file:
        rows = list(
            csv.DictReader(file)
        )

    print()
    print("=" * 95)
    print("BY CONDITION")
    print("=" * 95)

    print(
        f"{'Condition':<10}"
        f"{'N':>5}"
        f"{'Syntax':>10}"
        f"{'Exec':>10}"
        f"{'Oracle':>12}"
        f"{'Detect':>12}"
        f"{'No detect':>12}"
    )

    for condition in [
        "CODE",
        "SPEC",
        "BOTH",
    ]:
        subset = [
            row
            for row in rows
            if row["condition"] == condition
        ]

        n = len(subset)

        syntax = sum(
            as_bool(row["syntax_valid"])
            for row in subset
        )

        executable = sum(
            as_bool(
                row["correct_executable"]
            )
            for row in subset
        )

        oracle = sum(
            as_bool(row["oracle_correct"])
            for row in subset
        )

        detected = sum(
            as_bool(row["bug_detected"])
            for row in subset
        )

        no_detection = sum(
            row["classification"]
            == "valid_no_detection"
            for row in subset
        )

        print(
            f"{condition:<10}"
            f"{n:>5}"
            f"{syntax:>5}/{n:<4}"
            f"{executable:>5}/{n:<4}"
            f"{oracle:>5}/{n:<6}"
            f"{detected:>5}/{n:<6}"
            f"{no_detection:>5}/{n:<6}"
        )

        print(
            f"{'':10}"
            f"{'':5}"
            f"{percent(syntax, n):>9.2f}%"
            f"{percent(executable, n):>9.2f}%"
            f"{percent(oracle, n):>11.2f}%"
            f"{percent(detected, n):>11.2f}%"
        )

    print()
    print("=" * 95)
    print("CLASSIFICATIONS BY CONDITION")
    print("=" * 95)

    for condition in [
        "CODE",
        "SPEC",
        "BOTH",
    ]:
        subset = [
            row
            for row in rows
            if row["condition"] == condition
        ]

        counts = Counter(
            row["classification"]
            for row in subset
        )

        print()
        print(condition)

        for name, count in sorted(
            counts.items()
        ):
            print(
                f"  {name:<25} "
                f"{count:>3}"
            )

    print()
    print("=" * 95)
    print("DETECTION TYPES")
    print("=" * 95)

    for condition in [
        "CODE",
        "SPEC",
        "BOTH",
    ]:
        subset = [
            row
            for row in rows
            if (
                row["condition"] == condition
                and as_bool(
                    row["bug_detected"]
                )
            )
        ]

        counts = Counter(
            row["detection_type"]
            for row in subset
        )

        print()
        print(condition)

        for name, count in sorted(
            counts.items()
        ):
            print(
                f"  {name:<25} "
                f"{count:>3}"
            )

    print()
    print("=" * 95)
    print("PER PROGRAM / CONDITION")
    print("=" * 95)

    programs = sorted(
        {
            row["program"]
            for row in rows
        }
    )

    print(
        f"{'Program':<32}"
        f"{'CODE':>12}"
        f"{'SPEC':>12}"
        f"{'BOTH':>12}"
    )

    for program in programs:
        values = []

        for condition in [
            "CODE",
            "SPEC",
            "BOTH",
        ]:
            subset = [
                row
                for row in rows
                if (
                    row["program"] == program
                    and row["condition"]
                    == condition
                )
            ]

            detected = sum(
                as_bool(
                    row["bug_detected"]
                )
                for row in subset
            )

            oracle = sum(
                as_bool(
                    row["oracle_correct"]
                )
                for row in subset
            )

            values.append(
                f"{detected}/3 ({oracle}O)"
            )

        print(
            f"{program:<32}"
            f"{values[0]:>12}"
            f"{values[1]:>12}"
            f"{values[2]:>12}"
        )

    print()
    print("=" * 95)
    print("NON-EXECUTABLE / INVALID CASES")
    print("=" * 95)

    for row in rows:
        if (
            not as_bool(
                row["correct_executable"]
            )
        ):
            print(
                f"{row['run_id']:<45} "
                f"{row['classification']:<20} "
                f"correct_exit="
                f"{row.get('correct_exit_code', '')} "
                f"collected="
                f"{row.get('correct_collected', '')} "
                f"timeout="
                f"{row.get('correct_timeout', '')}"
            )

    print()
    print("=" * 95)
    print("ORACLE ERRORS PER PROGRAM")
    print("=" * 95)

    oracle_errors = defaultdict(
        lambda: {
            "CODE": 0,
            "SPEC": 0,
            "BOTH": 0,
        }
    )

    for row in rows:
        if (
            row["classification"]
            == "oracle_error"
        ):
            oracle_errors[
                row["program"]
            ][
                row["condition"]
            ] += 1

    print(
        f"{'Program':<32}"
        f"{'CODE':>8}"
        f"{'SPEC':>8}"
        f"{'BOTH':>8}"
        f"{'Total':>8}"
    )

    for program in programs:
        values = oracle_errors[
            program
        ]

        total = sum(
            values.values()
        )

        print(
            f"{program:<32}"
            f"{values['CODE']:>8}"
            f"{values['SPEC']:>8}"
            f"{values['BOTH']:>8}"
            f"{total:>8}"
        )


if __name__ == "__main__":
    main()