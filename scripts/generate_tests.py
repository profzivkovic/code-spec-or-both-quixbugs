from __future__ import annotations

import argparse
import csv
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from ollama import chat
from pydantic import BaseModel


PROJECT_ROOT = Path(__file__).resolve().parents[1]

GENERATION_PLAN_FILE = (
    PROJECT_ROOT
    / "prompts"
    / "generation_plan.csv"
)

OUTPUT_ROOT = (
    PROJECT_ROOT
    / "generated_tests"
)

RAW_RESPONSE_ROOT = (
    PROJECT_ROOT
    / "results"
    / "raw"
    / "ollama_responses"
)

METADATA_FILE = (
    PROJECT_ROOT
    / "results"
    / "raw"
    / "generation_metadata.csv"
)


MODEL = "qwen2.5-coder:7b"

TEMPERATURE = 0.7
NUM_CTX = 8192
NUM_PREDICT = 4096

SEEDS = {
    1: 101,
    2: 202,
    3: 303,
}


SYSTEM_PROMPT = """
You generate pytest unit tests for Python functions.

Return the generated test suite only through the requested structured output.

Rules:
- Generate executable pytest code.
- Do not use Markdown code fences.
- Do not provide explanations.
- Do not redefine or reimplement the function under test.
- Do not modify the function under test.
- Do not include an import statement for the function under test.
- The evaluation framework will make the function under test available.
- You may import pytest and Python standard-library modules when needed.
- Test observable behavior rather than implementation details.
- Do not access the network, filesystem, or external services.
""".strip()


class TestGeneration(BaseModel):
    code: str


def ns_to_seconds(value) -> float:
    if value is None:
        return 0.0

    return round(
        float(value) / 1_000_000_000,
        6,
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


def select_runs(
    rows: list[dict],
    mode: str,
) -> list[dict]:
    if mode == "all":
        return rows

    if mode == "smoke":
        return [
            row
            for row in rows
            if (
                row["program"] == "gcd"
                and int(row["generation"]) == 1
            )
        ]

    raise ValueError(
        f"Unknown mode: {mode}"
    )


def load_prompt(row: dict) -> str:
    path = (
        PROJECT_ROOT
        / row["prompt_file"]
    )

    return path.read_text(
        encoding="utf-8",
    )


def get_seed(row: dict) -> int:
    generation = int(
        row["generation"]
    )

    return SEEDS[generation]


def output_path(row: dict) -> Path:
    directory = (
        OUTPUT_ROOT
        / row["condition"].lower()
        / row["program"]
    )

    directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    return (
        directory
        / f"generation_{row['generation']}.py"
    )


def raw_response_path(row: dict) -> Path:
    RAW_RESPONSE_ROOT.mkdir(
        parents=True,
        exist_ok=True,
    )

    return (
        RAW_RESPONSE_ROOT
        / f"{row['run_id']}.json"
    )


def save_raw_response(
    response,
    path: Path,
) -> None:
    try:
        data = response.model_dump(
            mode="json"
        )
    except Exception:
        data = {
            "model": getattr(
                response,
                "model",
                "",
            ),
            "created_at": str(
                getattr(
                    response,
                    "created_at",
                    "",
                )
            ),
            "done": getattr(
                response,
                "done",
                "",
            ),
            "done_reason": getattr(
                response,
                "done_reason",
                "",
            ),
            "total_duration": getattr(
                response,
                "total_duration",
                "",
            ),
            "load_duration": getattr(
                response,
                "load_duration",
                "",
            ),
            "prompt_eval_count": getattr(
                response,
                "prompt_eval_count",
                "",
            ),
            "prompt_eval_duration": getattr(
                response,
                "prompt_eval_duration",
                "",
            ),
            "eval_count": getattr(
                response,
                "eval_count",
                "",
            ),
            "eval_duration": getattr(
                response,
                "eval_duration",
                "",
            ),
            "message_content": getattr(
                getattr(
                    response,
                    "message",
                    None,
                ),
                "content",
                "",
            ),
        }

    path.write_text(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
            default=str,
        ),
        encoding="utf-8",
    )


def load_existing_metadata() -> list[dict]:
    if not METADATA_FILE.exists():
        return []

    with METADATA_FILE.open(
        "r",
        newline="",
        encoding="utf-8",
    ) as file:
        return list(
            csv.DictReader(file)
        )


def save_metadata(
    rows: list[dict],
) -> None:
    METADATA_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fields = [
        "run_id",
        "program",
        "condition",
        "generation",
        "seed",
        "model",
        "temperature",
        "num_ctx",
        "num_predict",
        "timestamp_utc",
        "status",
        "done_reason",
        "wall_time_seconds",
        "total_duration_seconds",
        "load_duration_seconds",
        "prompt_eval_seconds",
        "generation_seconds",
        "prompt_tokens",
        "output_tokens",
        "output_tokens_per_second",
        "output_chars",
        "output_lines",
        "prompt_sha256",
        "output_file",
        "raw_response_file",
        "error",
    ]

    with METADATA_FILE.open(
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


def merge_metadata(
    old_rows: list[dict],
    new_rows: list[dict],
) -> list[dict]:
    by_id = {
        row["run_id"]: row
        for row in old_rows
    }

    for row in new_rows:
        by_id[row["run_id"]] = row

    return sorted(
        by_id.values(),
        key=lambda row: row["run_id"],
    )


def generate_one(
    row: dict,
) -> dict:
    prompt = load_prompt(row)
    seed = get_seed(row)

    test_path = output_path(row)
    raw_path = raw_response_path(row)

    timestamp = datetime.now(
        timezone.utc
    ).isoformat()

    started = time.perf_counter()

    try:
        response = chat(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            format=(
                TestGeneration
                .model_json_schema()
            ),
            options={
                "temperature": TEMPERATURE,
                "seed": seed,
                "num_ctx": NUM_CTX,
                "num_predict": NUM_PREDICT,
            },
        )

        wall_time = (
            time.perf_counter()
            - started
        )

        structured = (
            TestGeneration
            .model_validate_json(
                response.message.content
            )
        )

        code = structured.code

        # Save exactly the code returned in the
        # structured-output field. No manual repair.
        test_path.write_text(
            code,
            encoding="utf-8",
        )

        save_raw_response(
            response,
            raw_path,
        )

        total_seconds = ns_to_seconds(
            response.total_duration
        )

        load_seconds = ns_to_seconds(
            response.load_duration
        )

        prompt_eval_seconds = (
            ns_to_seconds(
                response.prompt_eval_duration
            )
        )

        generation_seconds = (
            ns_to_seconds(
                response.eval_duration
            )
        )

        prompt_tokens = (
            response.prompt_eval_count
            or 0
        )

        output_tokens = (
            response.eval_count
            or 0
        )

        if generation_seconds > 0:
            tokens_per_second = round(
                output_tokens
                / generation_seconds,
                3,
            )
        else:
            tokens_per_second = 0.0

        return {
            "run_id": row["run_id"],
            "program": row["program"],
            "condition": row["condition"],
            "generation": row[
                "generation"
            ],
            "seed": seed,
            "model": MODEL,
            "temperature": TEMPERATURE,
            "num_ctx": NUM_CTX,
            "num_predict": NUM_PREDICT,
            "timestamp_utc": timestamp,
            "status": "success",
            "done_reason": getattr(
                response,
                "done_reason",
                "",
            ),
            "wall_time_seconds": round(
                wall_time,
                6,
            ),
            "total_duration_seconds": (
                total_seconds
            ),
            "load_duration_seconds": (
                load_seconds
            ),
            "prompt_eval_seconds": (
                prompt_eval_seconds
            ),
            "generation_seconds": (
                generation_seconds
            ),
            "prompt_tokens": (
                prompt_tokens
            ),
            "output_tokens": (
                output_tokens
            ),
            "output_tokens_per_second": (
                tokens_per_second
            ),
            "output_chars": len(code),
            "output_lines": len(
                code.splitlines()
            ),
            "prompt_sha256": row[
                "prompt_sha256"
            ],
            "output_file": str(
                test_path.relative_to(
                    PROJECT_ROOT
                )
            ).replace("\\", "/"),
            "raw_response_file": str(
                raw_path.relative_to(
                    PROJECT_ROOT
                )
            ).replace("\\", "/"),
            "error": "",
        }

    except Exception as error:
        wall_time = (
            time.perf_counter()
            - started
        )

        return {
            "run_id": row["run_id"],
            "program": row["program"],
            "condition": row["condition"],
            "generation": row[
                "generation"
            ],
            "seed": seed,
            "model": MODEL,
            "temperature": TEMPERATURE,
            "num_ctx": NUM_CTX,
            "num_predict": NUM_PREDICT,
            "timestamp_utc": timestamp,
            "status": "error",
            "done_reason": "",
            "wall_time_seconds": round(
                wall_time,
                6,
            ),
            "total_duration_seconds": "",
            "load_duration_seconds": "",
            "prompt_eval_seconds": "",
            "generation_seconds": "",
            "prompt_tokens": "",
            "output_tokens": "",
            "output_tokens_per_second": "",
            "output_chars": "",
            "output_lines": "",
            "prompt_sha256": row[
                "prompt_sha256"
            ],
            "output_file": "",
            "raw_response_file": "",
            "error": (
                f"{type(error).__name__}: "
                f"{error}"
            ),
        }


def main() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--mode",
        choices=[
            "smoke",
            "all",
        ],
        default="smoke",
    )

    parser.add_argument(
        "--force",
        action="store_true",
    )

    args = parser.parse_args()

    plan = load_generation_plan()

    selected = select_runs(
        plan,
        args.mode,
    )

    old_metadata = (
        load_existing_metadata()
    )

    successful_ids = {
        row["run_id"]
        for row in old_metadata
        if row["status"] == "success"
    }

    print()
    print("=" * 70)
    print("LLM TEST GENERATION")
    print("=" * 70)

    print(
        f"Model: {MODEL}"
    )

    print(
        f"Temperature: {TEMPERATURE}"
    )

    print(
        f"Seeds: {SEEDS}"
    )

    print(
        f"Mode: {args.mode}"
    )

    print(
        f"Selected runs: "
        f"{len(selected)}"
    )

    print()

    new_rows = []

    for index, row in enumerate(
        selected,
        start=1,
    ):
        run_id = row["run_id"]

        if (
            run_id in successful_ids
            and not args.force
        ):
            print(
                f"[{index}/{len(selected)}] "
                f"{run_id:<40} SKIP"
            )

            continue

        print(
            f"[{index}/{len(selected)}] "
            f"{run_id:<40}",
            end=" ",
            flush=True,
        )

        result = generate_one(row)

        new_rows.append(result)

        if result["status"] == "success":
            print(
                "OK "
                f"({result['total_duration_seconds']:.2f}s, "
                f"{result['output_tokens']} tokens)"
            )
        else:
            print("ERROR")
            print(
                f"    {result['error']}"
            )

        merged = merge_metadata(
            old_metadata,
            new_rows,
        )

        save_metadata(merged)

    final_metadata = (
        load_existing_metadata()
    )

    selected_ids = {
        row["run_id"]
        for row in selected
    }

    selected_results = [
        row
        for row in final_metadata
        if row["run_id"]
        in selected_ids
    ]

    successful = [
        row
        for row in selected_results
        if row["status"] == "success"
    ]

    failed = [
        row
        for row in selected_results
        if row["status"] != "success"
    ]

    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print(
        f"Selected runs: "
        f"{len(selected)}"
    )

    print(
        f"Successful: "
        f"{len(successful)}"
    )

    print(
        f"Errors: "
        f"{len(failed)}"
    )

    print()
    print(
        f"Metadata: {METADATA_FILE}"
    )


if __name__ == "__main__":
    main()