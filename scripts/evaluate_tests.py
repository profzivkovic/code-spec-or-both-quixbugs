from __future__ import annotations

import argparse
import ast
import csv
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

TASKS_FILE = (
    PROJECT_ROOT
    / "results"
    / "preparation"
    / "tasks.json"
)

GENERATION_METADATA = (
    PROJECT_ROOT
    / "results"
    / "raw"
    / "generation_metadata.csv"
)

EVALUATION_RESULTS = (
    PROJECT_ROOT
    / "results"
    / "raw"
    / "evaluation_results.csv"
)

PER_TEST_RESULTS = (
    PROJECT_ROOT
    / "results"
    / "raw"
    / "per_test_results.csv"
)

LOG_DIR = (
    PROJECT_ROOT
    / "results"
    / "raw"
    / "evaluation_logs"
)

JUNIT_DIR = (
    PROJECT_ROOT
    / "results"
    / "raw"
    / "junit"
)

COVERAGE_DIR = (
    PROJECT_ROOT
    / "results"
    / "raw"
    / "coverage"
)


TIMEOUT_SECONDS = 20

SMOKE_RUNS = {
    "gcd__CODE__g1",
    "gcd__SPEC__g1",
    "gcd__BOTH__g1",
    "is_valid_parenthesization__CODE__g1",
    "mergesort__BOTH__g1",
}


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


def load_generation_metadata() -> list[dict]:
    with GENERATION_METADATA.open(
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
    rows = [
        row
        for row in rows
        if row["status"] == "success"
    ]

    if mode == "all":
        return rows

    return [
        row
        for row in rows
        if row["run_id"] in SMOKE_RUNS
    ]


def syntax_valid(
    source: str,
) -> tuple[bool, str]:
    try:
        ast.parse(source)
        return True, ""

    except SyntaxError as error:
        return (
            False,
            (
                f"SyntaxError line "
                f"{error.lineno}: "
                f"{error.msg}"
            ),
        )


def parse_junit(
    path: Path,
    run_id: str,
    variant: str,
) -> tuple[dict, list[dict]]:
    if not path.exists():
        return (
            {
                "collected": 0,
                "passed": 0,
                "failed": 0,
                "errors": 0,
                "skipped": 0,
                "junit_time_seconds": "",
            },
            [],
        )

    tree = ET.parse(path)
    root = tree.getroot()

    testcases = list(
        root.iter("testcase")
    )

    passed = 0
    failed = 0
    errors = 0
    skipped = 0

    per_test = []

    total_time = 0.0

    for testcase in testcases:
        failure = testcase.find("failure")
        error = testcase.find("error")
        skip = testcase.find("skipped")

        if failure is not None:
            status = "failed"
            failed += 1

        elif error is not None:
            status = "error"
            errors += 1

        elif skip is not None:
            status = "skipped"
            skipped += 1

        else:
            status = "passed"
            passed += 1

        try:
            test_time = float(
                testcase.attrib.get(
                    "time",
                    "0",
                )
            )
        except ValueError:
            test_time = 0.0

        total_time += test_time

        message = ""
        error_type = ""

        result_node = (
            failure
            if failure is not None
            else error
        )

        if result_node is not None:
            message = result_node.attrib.get(
                "message",
                "",
            )

            error_type = result_node.attrib.get(
                "type",
                "",
            )

        per_test.append(
            {
                "run_id": run_id,
                "variant": variant,
                "classname": testcase.attrib.get(
                    "classname",
                    "",
                ),
                "test_name": testcase.attrib.get(
                    "name",
                    "",
                ),
                "status": status,
                "time_seconds": round(
                    test_time,
                    6,
                ),
                "failure_type": error_type,
                "failure_message": message,
            }
        )

    return (
        {
            "collected": len(testcases),
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "skipped": skipped,
            "junit_time_seconds": round(
                total_time,
                6,
            ),
        },
        per_test,
    )


def parse_coverage(
    path: Path,
) -> dict:
    empty = {
        "line_coverage_percent": "",
        "covered_lines": "",
        "total_statements": "",
        "branch_coverage_percent": "",
        "covered_branches": "",
        "total_branches": "",
    }

    if not path.exists():
        return empty

    try:
        data = json.loads(
            path.read_text(
                encoding="utf-8",
            )
        )

        totals = data["totals"]

        covered_lines = int(
            totals.get(
                "covered_lines",
                0,
            )
        )

        total_statements = int(
            totals.get(
                "num_statements",
                0,
            )
        )

        covered_branches = int(
            totals.get(
                "covered_branches",
                0,
            )
        )

        total_branches = int(
            totals.get(
                "num_branches",
                0,
            )
        )

        if total_statements:
            line_percent = round(
                (
                    covered_lines
                    / total_statements
                )
                * 100,
                2,
            )
        else:
            line_percent = ""

        if total_branches:
            branch_percent = round(
                (
                    covered_branches
                    / total_branches
                )
                * 100,
                2,
            )
        else:
            branch_percent = ""

        return {
            "line_coverage_percent": (
                line_percent
            ),
            "covered_lines": (
                covered_lines
            ),
            "total_statements": (
                total_statements
            ),
            "branch_coverage_percent": (
                branch_percent
            ),
            "covered_branches": (
                covered_branches
            ),
            "total_branches": (
                total_branches
            ),
        }

    except Exception:
        return empty


def save_log(
    path: Path,
    command: list[str],
    result: dict,
) -> None:
    text = [
        "COMMAND",
        "=" * 70,
        subprocess.list2cmdline(
            command
        ),
        "",
        "EXIT CODE",
        "=" * 70,
        str(
            result["exit_code"]
        ),
        "",
        "TIMEOUT",
        "=" * 70,
        str(
            result["timeout"]
        ),
        "",
        "WALL TIME",
        "=" * 70,
        str(
            result["wall_time_seconds"]
        ),
        "",
        "STDOUT",
        "=" * 70,
        result["stdout"],
        "",
        "STDERR",
        "=" * 70,
        result["stderr"],
    ]

    path.write_text(
        "\n".join(text),
        encoding="utf-8",
    )


def run_variant(
    run_id: str,
    function_name: str,
    generated_source: str,
    sut_source: str,
    variant: str,
) -> tuple[dict, list[dict]]:
    with tempfile.TemporaryDirectory() as temp:
        work = Path(temp)

        sut_file = (
            work
            / "sut.py"
        )

        test_file = (
            work
            / "test_generated.py"
        )

        junit_file = (
            work
            / "junit.xml"
        )

        coverage_file = (
            work
            / "coverage.json"
        )

        sut_file.write_text(
            sut_source.strip()
            + "\n",
            encoding="utf-8",
        )

        harness_source = (
            f"from sut import "
            f"{function_name}\n\n"
            + generated_source
        )

        test_file.write_text(
            harness_source,
            encoding="utf-8",
        )

        command = [
            sys.executable,
            "-m",
            "coverage",
            "run",
            "--branch",
            "--source=sut",
            "-m",
            "pytest",
            "-q",
            "--disable-warnings",
            f"--junitxml={junit_file}",
            str(test_file),
        ]

        environment = os.environ.copy()

        # Stabilize Python hash iteration.
        environment[
            "PYTHONHASHSEED"
        ] = "0"

        started = time.perf_counter()

        timed_out = False

        try:
            completed = subprocess.run(
                command,
                cwd=work,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=TIMEOUT_SECONDS,
                check=False,
                env=environment,
            )

            exit_code = (
                completed.returncode
            )

            stdout = completed.stdout
            stderr = completed.stderr

        except subprocess.TimeoutExpired as error:
            timed_out = True
            exit_code = ""

            stdout = (
                error.stdout
                or ""
            )

            stderr = (
                error.stderr
                or ""
            )

            if isinstance(
                stdout,
                bytes,
            ):
                stdout = stdout.decode(
                    "utf-8",
                    errors="replace",
                )

            if isinstance(
                stderr,
                bytes,
            ):
                stderr = stderr.decode(
                    "utf-8",
                    errors="replace",
                )

        wall_time = (
            time.perf_counter()
            - started
        )

        execution = {
            "exit_code": exit_code,
            "timeout": timed_out,
            "wall_time_seconds": round(
                wall_time,
                6,
            ),
            "stdout": stdout,
            "stderr": stderr,
        }

        LOG_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        save_log(
            LOG_DIR
            / f"{run_id}__{variant}.txt",
            command,
            execution,
        )

        junit_summary, per_test = (
            parse_junit(
                junit_file,
                run_id,
                variant,
            )
        )

        JUNIT_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        if junit_file.exists():
            shutil.copy2(
                junit_file,
                JUNIT_DIR
                / (
                    f"{run_id}"
                    f"__{variant}.xml"
                ),
            )

        coverage_stats = {
            "line_coverage_percent": "",
            "covered_lines": "",
            "total_statements": "",
            "branch_coverage_percent": "",
            "covered_branches": "",
            "total_branches": "",
        }

        coverage_data = (
            work
            / ".coverage"
        )

        if (
            not timed_out
            and coverage_data.exists()
        ):
            coverage_command = [
                sys.executable,
                "-m",
                "coverage",
                "json",
                "-o",
                str(
                    coverage_file
                ),
            ]

            subprocess.run(
                coverage_command,
                cwd=work,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=False,
            )

            if coverage_file.exists():
                coverage_stats = (
                    parse_coverage(
                        coverage_file
                    )
                )

                COVERAGE_DIR.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                shutil.copy2(
                    coverage_file,
                    COVERAGE_DIR
                    / (
                        f"{run_id}"
                        f"__{variant}.json"
                    ),
                )

        result = {
            "exit_code": exit_code,
            "timeout": timed_out,
            "wall_time_seconds": round(
                wall_time,
                6,
            ),
            **junit_summary,
            **coverage_stats,
        }

        return (
            result,
            per_test,
        )


def prefix_dict(
    prefix: str,
    data: dict,
) -> dict:
    return {
        f"{prefix}_{key}": value
        for key, value in data.items()
    }


def classify_detection(
    correct: dict,
    buggy: dict,
) -> tuple[
    bool,
    bool,
    bool,
    str,
    str,
]:
    correct_executable = (
        not correct["timeout"]
        and correct["collected"] > 0
        and correct["exit_code"]
        in (0, 1)
    )

    oracle_correct = (
        correct_executable
        and correct["exit_code"] == 0
        and correct["failed"] == 0
        and correct["errors"] == 0
    )

    defect_manifested = (
        buggy["timeout"]
        or buggy["failed"] > 0
        or buggy["errors"] > 0
    )

    bug_detected = (
        oracle_correct
        and defect_manifested
    )

    if not correct_executable:
        classification = (
            "not_executable"
        )

    elif not oracle_correct:
        classification = (
            "oracle_error"
        )

    elif bug_detected:
        classification = (
            "bug_detecting"
        )

    else:
        classification = (
            "valid_no_detection"
        )

    if not defect_manifested:
        detection_type = "none"

    elif buggy["timeout"]:
        detection_type = "timeout"

    elif (
        buggy["failed"] > 0
        and buggy["errors"] > 0
    ):
        detection_type = "mixed"

    elif buggy["errors"] > 0:
        detection_type = (
            "runtime_error"
        )

    else:
        detection_type = (
            "assertion_failure"
        )

    return (
        correct_executable,
        oracle_correct,
        bug_detected,
        classification,
        detection_type,
    )


def save_evaluation(
    rows: list[dict],
) -> None:
    EVALUATION_RESULTS.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not rows:
        return

    with EVALUATION_RESULTS.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=list(
                rows[0].keys()
            ),
        )

        writer.writeheader()
        writer.writerows(rows)


def save_per_test(
    rows: list[dict],
) -> None:
    PER_TEST_RESULTS.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fields = [
        "run_id",
        "variant",
        "classname",
        "test_name",
        "status",
        "time_seconds",
        "failure_type",
        "failure_message",
    ]

    with PER_TEST_RESULTS.open(
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
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--mode",
        choices=[
            "smoke",
            "all",
        ],
        default="smoke",
    )

    args = parser.parse_args()

    tasks = load_tasks()

    metadata = (
        load_generation_metadata()
    )

    rows = select_runs(
        metadata,
        args.mode,
    )

    results = []
    all_per_test = []

    print()
    print("=" * 70)
    print("TEST SUITE EVALUATION")
    print("=" * 70)

    print(
        f"Mode: {args.mode}"
    )

    print(
        f"Suites selected: "
        f"{len(rows)}"
    )

    print(
        f"Timeout: "
        f"{TIMEOUT_SECONDS}s"
    )

    print()

    for index, row in enumerate(
        rows,
        start=1,
    ):
        run_id = row["run_id"]
        program = row["program"]
        condition = row[
            "condition"
        ]

        generated_path = (
            PROJECT_ROOT
            / row["output_file"]
        )

        generated_source = (
            generated_path.read_text(
                encoding="utf-8",
                errors="replace",
            )
        )

        valid_syntax, syntax_error = (
            syntax_valid(
                generated_source
            )
        )

        print(
            f"[{index}/{len(rows)}] "
            f"{run_id:<42}",
            end=" ",
            flush=True,
        )

        base = {
            "run_id": run_id,
            "program": program,
            "condition": condition,
            "generation": row[
                "generation"
            ],
            "seed": row["seed"],
            "syntax_valid": (
                valid_syntax
            ),
        }

        if not valid_syntax:
            result = {
                **base,
                "correct_executable": False,
                "oracle_correct": False,
                "bug_detected": False,
                "classification": (
                    "invalid_syntax"
                ),
                "detection_type": "none",
                "syntax_error": (
                    syntax_error
                ),
            }

            empty = {
                "exit_code": "",
                "timeout": False,
                "wall_time_seconds": "",
                "collected": 0,
                "passed": 0,
                "failed": 0,
                "errors": 0,
                "skipped": 0,
                "junit_time_seconds": "",
                "line_coverage_percent": "",
                "covered_lines": "",
                "total_statements": "",
                "branch_coverage_percent": "",
                "covered_branches": "",
                "total_branches": "",
            }

            result.update(
                prefix_dict(
                    "correct",
                    empty,
                )
            )

            result.update(
                prefix_dict(
                    "buggy",
                    empty,
                )
            )

            results.append(result)

            print(
                "INVALID SYNTAX"
            )

            continue

        task = tasks[program]

        correct, correct_tests = (
            run_variant(
                run_id=run_id,
                function_name=task[
                    "function_name"
                ],
                generated_source=(
                    generated_source
                ),
                sut_source=task[
                    "correct_source"
                ],
                variant="correct",
            )
        )

        buggy, buggy_tests = (
            run_variant(
                run_id=run_id,
                function_name=task[
                    "function_name"
                ],
                generated_source=(
                    generated_source
                ),
                sut_source=task[
                    "code_only_source"
                ],
                variant="buggy",
            )
        )

        all_per_test.extend(
            correct_tests
        )

        all_per_test.extend(
            buggy_tests
        )

        (
            correct_executable,
            oracle_correct,
            bug_detected,
            classification,
            detection_type,
        ) = classify_detection(
            correct,
            buggy,
        )

        result = {
            **base,
            "correct_executable": (
                correct_executable
            ),
            "oracle_correct": (
                oracle_correct
            ),
            "bug_detected": (
                bug_detected
            ),
            "classification": (
                classification
            ),
            "detection_type": (
                detection_type
            ),
            "syntax_error": "",
        }

        result.update(
            prefix_dict(
                "correct",
                correct,
            )
        )

        result.update(
            prefix_dict(
                "buggy",
                buggy,
            )
        )

        results.append(result)

        print(
            f"{classification:<18} "
            f"correct="
            f"{correct['passed']}/"
            f"{correct['collected']} "
            f"buggy_fail="
            f"{buggy['failed']} "
            f"buggy_err="
            f"{buggy['errors']} "
            f"detected="
            f"{bug_detected}"
        )

        # Save incrementally.
        save_evaluation(
            results
        )

        save_per_test(
            all_per_test
        )

    save_evaluation(
        results
    )

    save_per_test(
        all_per_test
    )

    syntax_valid_count = sum(
        bool(row["syntax_valid"])
        for row in results
    )

    executable_count = sum(
        bool(row["correct_executable"])
        for row in results
    )

    oracle_correct_count = sum(
        bool(row["oracle_correct"])
        for row in results
    )

    detected_count = sum(
        bool(row["bug_detected"])
        for row in results
    )

    oracle_errors = sum(
        row["classification"]
        == "oracle_error"
        for row in results
    )

    no_detection = sum(
        row["classification"]
        == "valid_no_detection"
        for row in results
    )

    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print(
        f"Suites evaluated: "
        f"{len(results)}"
    )

    print(
        f"Syntax valid: "
        f"{syntax_valid_count}"
    )

    print(
        f"Executable on correct: "
        f"{executable_count}"
    )

    print(
        f"Oracle correct: "
        f"{oracle_correct_count}"
    )

    print(
        f"Bug detecting: "
        f"{detected_count}"
    )

    print(
        f"Oracle errors: "
        f"{oracle_errors}"
    )

    print(
        f"Valid but no detection: "
        f"{no_detection}"
    )

    print()
    print(
        f"Evaluation results: "
        f"{EVALUATION_RESULTS}"
    )

    print(
        f"Per-test results: "
        f"{PER_TEST_RESULTS}"
    )


if __name__ == "__main__":
    main()