from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

TASKS_FILE = (
    PROJECT_ROOT
    / "results"
    / "preparation"
    / "tasks.json"
)

PROMPTS_DIR = PROJECT_ROOT / "prompts"

CODE_DIR = PROMPTS_DIR / "code"
SPEC_DIR = PROMPTS_DIR / "spec"
BOTH_DIR = PROMPTS_DIR / "both"

MANIFEST_CSV = (
    PROMPTS_DIR
    / "prompt_manifest.csv"
)

MANIFEST_JSON = (
    PROMPTS_DIR
    / "prompt_manifest.json"
)

GENERATION_PLAN_CSV = (
    PROMPTS_DIR
    / "generation_plan.csv"
)

GENERATIONS_PER_CONDITION = 3


COMMON_INSTRUCTIONS = """You are generating unit tests for a Python function.

Generate a complete pytest test suite using only the information provided below.

Requirements:
- Return only executable Python code.
- Do not use Markdown code fences.
- Do not include explanations.
- Do not redefine or reimplement the function under test.
- Do not modify the function under test.
- Do not include an import statement for the function under test; the evaluation framework will provide it.
- You may import pytest and Python standard-library modules when needed.
- Include normal cases, boundary cases, edge cases, and relevant exceptional behavior when supported by the provided information.
- Test observable behavior rather than implementation details.
- Do not access the network, filesystem, or external services.
"""


def load_tasks() -> list[dict]:
    if not TASKS_FILE.exists():
        raise FileNotFoundError(
            f"Tasks file not found: {TASKS_FILE}"
        )

    with TASKS_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        tasks = json.load(file)

    if not isinstance(tasks, list):
        raise ValueError(
            "tasks.json must contain a list."
        )

    return tasks


def validate_task(task: dict) -> None:
    required = [
        "program",
        "function_name",
        "signature",
        "specification",
        "code_only_source",
        "has_specification",
    ]

    missing = [
        key
        for key in required
        if key not in task
    ]

    if missing:
        raise ValueError(
            f"{task.get('program', 'UNKNOWN')}: "
            f"missing fields: {missing}"
        )

    if not task["has_specification"]:
        raise ValueError(
            f"{task['program']}: no specification"
        )

    if not task["specification"].strip():
        raise ValueError(
            f"{task['program']}: empty specification"
        )

    if not task["code_only_source"].strip():
        raise ValueError(
            f"{task['program']}: empty code"
        )


def create_code_prompt(task: dict) -> str:
    return f"""{COMMON_INSTRUCTIONS}

Function implementation:

{task["code_only_source"].strip()}

Generate tests for the function `{task["function_name"]}`.
"""


def create_spec_prompt(task: dict) -> str:
    return f"""{COMMON_INSTRUCTIONS}

Function signature:

{task["signature"]}

Specification:

{task["specification"].strip()}

Generate tests for the function `{task["function_name"]}`.
"""


def create_both_prompt(task: dict) -> str:
    return f"""{COMMON_INSTRUCTIONS}

Function implementation:

{task["code_only_source"].strip()}

Specification:

{task["specification"].strip()}

Generate tests for the function `{task["function_name"]}`.
"""


def sha256_text(text: str) -> str:
    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


def save_prompt(
    directory: Path,
    program: str,
    prompt: str,
) -> Path:
    directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    path = directory / f"{program}.txt"

    path.write_text(
        prompt.strip() + "\n",
        encoding="utf-8",
    )

    return path


def relative_path(path: Path) -> str:
    return str(
        path.relative_to(
            PROJECT_ROOT
        )
    ).replace("\\", "/")


def create_prompt_record(
    task: dict,
    condition: str,
    prompt: str,
    path: Path,
) -> dict:
    return {
        "program": task["program"],
        "function_name": task["function_name"],
        "condition": condition,
        "prompt_file": relative_path(path),
        "prompt_sha256": sha256_text(prompt),
        "prompt_chars": len(prompt),
        "prompt_lines": len(
            prompt.splitlines()
        ),
    }


def save_manifest_csv(
    records: list[dict],
) -> None:
    fields = [
        "program",
        "function_name",
        "condition",
        "prompt_file",
        "prompt_sha256",
        "prompt_chars",
        "prompt_lines",
    ]

    with MANIFEST_CSV.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fields,
        )

        writer.writeheader()
        writer.writerows(records)


def save_manifest_json(
    records: list[dict],
) -> None:
    MANIFEST_JSON.write_text(
        json.dumps(
            records,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def save_generation_plan(
    records: list[dict],
) -> None:
    fields = [
        "run_id",
        "program",
        "function_name",
        "condition",
        "generation",
        "prompt_file",
        "prompt_sha256",
    ]

    rows = []

    for record in records:
        for generation in range(
            1,
            GENERATIONS_PER_CONDITION + 1,
        ):
            run_id = (
                f"{record['program']}"
                f"__{record['condition']}"
                f"__g{generation}"
            )

            rows.append(
                {
                    "run_id": run_id,
                    "program": record[
                        "program"
                    ],
                    "function_name": record[
                        "function_name"
                    ],
                    "condition": record[
                        "condition"
                    ],
                    "generation": generation,
                    "prompt_file": record[
                        "prompt_file"
                    ],
                    "prompt_sha256": record[
                        "prompt_sha256"
                    ],
                }
            )

    with GENERATION_PLAN_CSV.open(
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
    PROMPTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    tasks = load_tasks()

    records = []

    print(
        "Gradim kontrolisane promptove..."
    )
    print()

    for task in tasks:
        validate_task(task)

        prompts = {
            "CODE": (
                create_code_prompt(task),
                CODE_DIR,
            ),
            "SPEC": (
                create_spec_prompt(task),
                SPEC_DIR,
            ),
            "BOTH": (
                create_both_prompt(task),
                BOTH_DIR,
            ),
        }

        for condition, (
            prompt,
            directory,
        ) in prompts.items():
            path = save_prompt(
                directory,
                task["program"],
                prompt,
            )

            record = create_prompt_record(
                task,
                condition,
                prompt,
                path,
            )

            records.append(record)

            print(
                f"{task['program']:<30} "
                f"{condition:<5} "
                f"chars={len(prompt):<5} "
                f"sha={record['prompt_sha256'][:10]}"
            )

    save_manifest_csv(records)
    save_manifest_json(records)
    save_generation_plan(records)

    expected_prompts = (
        len(tasks) * 3
    )

    expected_runs = (
        len(tasks)
        * 3
        * GENERATIONS_PER_CONDITION
    )

    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print(
        f"Programs: {len(tasks)}"
    )

    print(
        f"Prompt conditions: 3"
    )

    print(
        f"Prompt files: {len(records)} "
        f"(expected {expected_prompts})"
    )

    print(
        f"Generations per condition: "
        f"{GENERATIONS_PER_CONDITION}"
    )

    print(
        f"Planned LLM generations: "
        f"{expected_runs}"
    )

    print()
    print(
        f"Manifest: {MANIFEST_CSV}"
    )

    print(
        f"Generation plan: "
        f"{GENERATION_PLAN_CSV}"
    )


if __name__ == "__main__":
    main()