from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

TASKS_FILE = (
    PROJECT_ROOT
    / "results"
    / "preparation"
    / "tasks.json"
)

MANIFEST_FILE = (
    PROJECT_ROOT
    / "prompts"
    / "prompt_manifest.csv"
)

GENERATION_PLAN_FILE = (
    PROJECT_ROOT
    / "prompts"
    / "generation_plan.csv"
)

REPORT_FILE = (
    PROJECT_ROOT
    / "results"
    / "preparation"
    / "prompt_validation.csv"
)


EXPECTED_CONDITIONS = {
    "CODE",
    "SPEC",
    "BOTH",
}

EXPECTED_GENERATIONS_PER_CONDITION = 3

FORBIDDEN_HINT_PATTERNS = [
    r"\bbuggy\b",
    r"\bdefective\b",
    r"\bincorrect implementation\b",
    r"\bfind the bug\b",
    r"\bdetect the bug\b",
    r"\bknown bug\b",
]


def load_tasks() -> dict[str, dict]:
    with TASKS_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        tasks = json.load(file)

    return {
        task["program"]: task
        for task in tasks
    }


def load_manifest() -> list[dict]:
    with MANIFEST_FILE.open(
        "r",
        newline="",
        encoding="utf-8",
    ) as file:
        return list(
            csv.DictReader(file)
        )


def load_generation_plan() -> list[dict]:
    with GENERATION_PLAN_FILE.open(
        "r",
        newline="",
        encoding="utf-8",
    ) as file:
        return list(
            csv.DictReader(file)
        )


def normalize(text: str) -> str:
    return (
        text
        .replace("\r\n", "\n")
        .strip()
    )


def contains_forbidden_hint(
    prompt: str,
) -> list[str]:
    found = []

    for pattern in FORBIDDEN_HINT_PATTERNS:
        if re.search(
            pattern,
            prompt,
            flags=re.IGNORECASE,
        ):
            found.append(pattern)

    return found


def validate_prompt(
    record: dict,
    task: dict,
) -> dict:
    program = record["program"]
    condition = record["condition"]

    prompt_path = (
        PROJECT_ROOT
        / record["prompt_file"]
    )

    errors: list[str] = []

    if not prompt_path.exists():
        return {
            "program": program,
            "condition": condition,
            "valid": False,
            "errors": "Prompt file missing",
        }

    prompt = normalize(
        prompt_path.read_text(
            encoding="utf-8",
        )
    )

    code = normalize(
        task["code_only_source"]
    )

    specification = normalize(
        task["specification"]
    )

    correct_source = normalize(
        task["correct_source"]
    )

    has_code = (
        code in prompt
    )

    has_specification = (
        specification in prompt
    )

    has_correct_source = (
        correct_source in prompt
    )

    forbidden_hints = (
        contains_forbidden_hint(
            prompt
        )
    )

    if condition == "CODE":
        if not has_code:
            errors.append(
                "CODE does not contain implementation"
            )

        if has_specification:
            errors.append(
                "CODE leaks specification"
            )

    elif condition == "SPEC":
        if not has_specification:
            errors.append(
                "SPEC does not contain specification"
            )

        if has_code:
            errors.append(
                "SPEC leaks implementation"
            )

    elif condition == "BOTH":
        if not has_code:
            errors.append(
                "BOTH does not contain implementation"
            )

        if not has_specification:
            errors.append(
                "BOTH does not contain specification"
            )

    else:
        errors.append(
            f"Unknown condition: {condition}"
        )

    if has_correct_source:
        errors.append(
            "Correct implementation leaked into prompt"
        )

    if forbidden_hints:
        errors.append(
            "Prompt contains bug hint: "
            + ", ".join(
                forbidden_hints
            )
        )

    if (
        "Return only executable Python code."
        not in prompt
    ):
        errors.append(
            "Missing executable-code instruction"
        )

    if (
        "Do not redefine or reimplement "
        "the function under test."
        not in prompt
    ):
        errors.append(
            "Missing no-reimplementation instruction"
        )

    if (
        task["function_name"]
        not in prompt
    ):
        errors.append(
            "Function name missing"
        )

    return {
        "program": program,
        "condition": condition,
        "has_code": has_code,
        "has_specification": has_specification,
        "correct_source_leaked": has_correct_source,
        "forbidden_hint_count": len(
            forbidden_hints
        ),
        "valid": len(errors) == 0,
        "errors": "; ".join(errors),
    }


def validate_manifest_structure(
    tasks: dict[str, dict],
    manifest: list[dict],
) -> list[str]:
    errors = []

    expected_count = (
        len(tasks)
        * len(EXPECTED_CONDITIONS)
    )

    if len(manifest) != expected_count:
        errors.append(
            f"Manifest contains {len(manifest)} prompts; "
            f"expected {expected_count}"
        )

    seen = set()

    for record in manifest:
        key = (
            record["program"],
            record["condition"],
        )

        if key in seen:
            errors.append(
                f"Duplicate prompt: {key}"
            )

        seen.add(key)

    for program in tasks:
        for condition in EXPECTED_CONDITIONS:
            key = (
                program,
                condition,
            )

            if key not in seen:
                errors.append(
                    f"Missing prompt: {program} / {condition}"
                )

    return errors


def validate_generation_plan(
    tasks: dict[str, dict],
    rows: list[dict],
) -> list[str]:
    errors = []

    expected_count = (
        len(tasks)
        * len(EXPECTED_CONDITIONS)
        * EXPECTED_GENERATIONS_PER_CONDITION
    )

    if len(rows) != expected_count:
        errors.append(
            f"Generation plan contains {len(rows)} runs; "
            f"expected {expected_count}"
        )

    run_ids = set()

    counts: dict[
        tuple[str, str],
        int
    ] = {}

    for row in rows:
        run_id = row["run_id"]

        if run_id in run_ids:
            errors.append(
                f"Duplicate run_id: {run_id}"
            )

        run_ids.add(run_id)

        key = (
            row["program"],
            row["condition"],
        )

        counts[key] = (
            counts.get(key, 0)
            + 1
        )

    for program in tasks:
        for condition in EXPECTED_CONDITIONS:
            count = counts.get(
                (
                    program,
                    condition,
                ),
                0,
            )

            if (
                count
                != EXPECTED_GENERATIONS_PER_CONDITION
            ):
                errors.append(
                    f"{program}/{condition}: "
                    f"{count} generations instead of "
                    f"{EXPECTED_GENERATIONS_PER_CONDITION}"
                )

    return errors


def save_report(
    rows: list[dict],
) -> None:
    REPORT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fields = [
        "program",
        "condition",
        "has_code",
        "has_specification",
        "correct_source_leaked",
        "forbidden_hint_count",
        "valid",
        "errors",
    ]

    with REPORT_FILE.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fields,
        )

        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    tasks = load_tasks()
    manifest = load_manifest()
    generation_plan = (
        load_generation_plan()
    )

    print(
        "Validiram eksperimentalne promptove..."
    )
    print()

    structural_errors = (
        validate_manifest_structure(
            tasks,
            manifest,
        )
    )

    plan_errors = (
        validate_generation_plan(
            tasks,
            generation_plan,
        )
    )

    results = []

    for record in manifest:
        program = record["program"]

        if program not in tasks:
            results.append(
                {
                    "program": program,
                    "condition": record[
                        "condition"
                    ],
                    "has_code": "",
                    "has_specification": "",
                    "correct_source_leaked": "",
                    "forbidden_hint_count": "",
                    "valid": False,
                    "errors": (
                        "Program missing from tasks.json"
                    ),
                }
            )

            continue

        result = validate_prompt(
            record,
            tasks[program],
        )

        results.append(result)

        status = (
            "OK"
            if result["valid"]
            else "FAIL"
        )

        print(
            f"{program:<30} "
            f"{record['condition']:<5} "
            f"{status}"
        )

        if not result["valid"]:
            print(
                f"    {result['errors']}"
            )

    save_report(results)

    invalid = [
        result
        for result in results
        if not result["valid"]
    ]

    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print(
        f"Programs: {len(tasks)}"
    )

    print(
        f"Prompts checked: {len(results)}"
    )

    print(
        f"Valid prompts: "
        f"{len(results) - len(invalid)}"
    )

    print(
        f"Invalid prompts: "
        f"{len(invalid)}"
    )

    print(
        f"Planned generations: "
        f"{len(generation_plan)}"
    )

    if structural_errors:
        print()
        print(
            "Manifest errors:"
        )

        for error in structural_errors:
            print(
                f"  - {error}"
            )

    if plan_errors:
        print()
        print(
            "Generation-plan errors:"
        )

        for error in plan_errors:
            print(
                f"  - {error}"
            )

    print()
    print(
        f"Report: {REPORT_FILE}"
    )

    all_valid = (
        not invalid
        and not structural_errors
        and not plan_errors
    )

    if all_valid:
        print()
        print(
            "EXPERIMENTAL PROMPTS ARE VALID."
        )

    else:
        print()
        print(
            "VALIDATION FAILED."
        )

        sys.exit(1)


if __name__ == "__main__":
    main()