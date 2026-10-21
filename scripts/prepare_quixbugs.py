from __future__ import annotations

import csv
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]

REPOSITORY_URL = "https://github.com/jkoppel/QuixBugs.git"

QUIXBUGS_DIRECTORY = (
    PROJECT_ROOT
    / "external"
    / "QuixBugs"
)

RESULTS_DIRECTORY = (
    PROJECT_ROOT
    / "results"
    / "preparation"
)

LOGS_DIRECTORY = (
    RESULTS_DIRECTORY
    / "logs"
)

OUTPUT_CSV = (
    RESULTS_DIRECTORY
    / "candidate_validation.csv"
)

ENVIRONMENT_FILE = (
    RESULTS_DIRECTORY
    / "environment.txt"
)


CANDIDATES = [
    "bitcount",
    "gcd",
    "get_factors",
    "is_valid_parenthesization",
    "max_sublist_sum",
    "mergesort",
    "next_palindrome",
    "next_permutation",
    "powerset",
    "quicksort",
    "sieve",
    "to_base",
]


def run_command(
    command: list[str],
    cwd: Path,
    timeout: int = 60,
) -> dict[str, Any]:
    started = time.perf_counter()

    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )

        duration = (
            time.perf_counter()
            - started
        )

        return {
            "exit_code": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "duration_seconds": round(
                duration,
                4,
            ),
            "timed_out": False,
        }

    except subprocess.TimeoutExpired as error:
        duration = (
            time.perf_counter()
            - started
        )

        stdout = error.stdout or ""
        stderr = error.stderr or ""

        if isinstance(stdout, bytes):
            stdout = stdout.decode(
                "utf-8",
                errors="replace",
            )

        if isinstance(stderr, bytes):
            stderr = stderr.decode(
                "utf-8",
                errors="replace",
            )

        return {
            "exit_code": "",
            "stdout": stdout,
            "stderr": stderr,
            "duration_seconds": round(
                duration,
                4,
            ),
            "timed_out": True,
        }


def clone_repository() -> None:
    if QUIXBUGS_DIRECTORY.exists():
        print(
            "QuixBugs već postoji:"
        )
        print(
            QUIXBUGS_DIRECTORY
        )
        return

    QUIXBUGS_DIRECTORY.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    print(
        "Kloniram QuixBugs..."
    )

    completed = subprocess.run(
        [
            "git",
            "clone",
            REPOSITORY_URL,
            str(QUIXBUGS_DIRECTORY),
        ],
        cwd=PROJECT_ROOT,
        check=False,
    )

    if completed.returncode != 0:
        raise RuntimeError(
            "Git clone nije uspeo."
        )


def get_commit_sha() -> str:
    completed = subprocess.run(
        [
            "git",
            "rev-parse",
            "HEAD",
        ],
        cwd=QUIXBUGS_DIRECTORY,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )

    if completed.returncode != 0:
        return "UNKNOWN"

    return completed.stdout.strip()


def save_environment(
    commit_sha: str,
) -> None:
    pytest_version = run_command(
        [
            sys.executable,
            "-m",
            "pytest",
            "--version",
        ],
        cwd=PROJECT_ROOT,
    )

    lines = [
        f"Python executable: {sys.executable}",
        f"Python version: {sys.version}",
        "",
        (
            "pytest: "
            + pytest_version[
                "stdout"
            ].strip()
        ),
        "",
        f"QuixBugs repository: {REPOSITORY_URL}",
        f"QuixBugs commit: {commit_sha}",
    ]

    ENVIRONMENT_FILE.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def check_candidate_files(
    program: str,
) -> tuple[bool, list[str]]:
    required_files = [
        (
            QUIXBUGS_DIRECTORY
            / "python_programs"
            / f"{program}.py"
        ),
        (
            QUIXBUGS_DIRECTORY
            / "correct_python_programs"
            / f"{program}.py"
        ),
        (
            QUIXBUGS_DIRECTORY
            / "python_testcases"
            / f"test_{program}.py"
        ),
    ]

    missing = [
        str(path)
        for path in required_files
        if not path.exists()
    ]

    return (
        len(missing) == 0,
        missing,
    )


def save_log(
    path: Path,
    command: list[str],
    result: dict[str, Any],
) -> None:
    lines = [
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
        "TIMED OUT",
        "=" * 70,
        str(
            result["timed_out"]
        ),
        "",
        "DURATION",
        "=" * 70,
        str(
            result[
                "duration_seconds"
            ]
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
        "\n".join(lines),
        encoding="utf-8",
    )


def validate_candidate(
    program: str,
) -> dict[str, Any]:
    files_exist, missing = (
        check_candidate_files(
            program
        )
    )

    if not files_exist:
        return {
            "program": program,
            "files_ok": False,
            "buggy_exit_code": "",
            "correct_exit_code": "",
            "buggy_timeout": False,
            "correct_timeout": False,
            "buggy_duration_seconds": "",
            "correct_duration_seconds": "",
            "bug_exposed_by_reference_tests": False,
            "correct_version_passes": False,
            "candidate_usable": False,
            "note": (
                "Missing: "
                + "; ".join(missing)
            ),
        }

    test_file = (
        "python_testcases/"
        f"test_{program}.py"
    )

    buggy_command = [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        test_file,
        "--disable-warnings",
    ]

    correct_command = [
        sys.executable,
        "-m",
        "pytest",
        "-q",
        "--correct",
        test_file,
        "--disable-warnings",
    ]

    print(
        f"  {program:<30} BUGGY ... ",
        end="",
        flush=True,
    )

    buggy_result = run_command(
        buggy_command,
        cwd=QUIXBUGS_DIRECTORY,
        timeout=60,
    )

    print(
        (
            "TIMEOUT"
            if buggy_result[
                "timed_out"
            ]
            else (
                "PASS"
                if buggy_result[
                    "exit_code"
                ] == 0
                else "FAIL"
            )
        )
    )

    print(
        f"  {program:<30} CORRECT ... ",
        end="",
        flush=True,
    )

    correct_result = run_command(
        correct_command,
        cwd=QUIXBUGS_DIRECTORY,
        timeout=60,
    )

    print(
        (
            "TIMEOUT"
            if correct_result[
                "timed_out"
            ]
            else (
                "PASS"
                if correct_result[
                    "exit_code"
                ] == 0
                else "FAIL"
            )
        )
    )

    save_log(
        LOGS_DIRECTORY
        / f"{program}_buggy.txt",
        buggy_command,
        buggy_result,
    )

    save_log(
        LOGS_DIRECTORY
        / f"{program}_correct.txt",
        correct_command,
        correct_result,
    )

    bug_exposed = (
        not buggy_result["timed_out"]
        and buggy_result["exit_code"] != 0
    )

    correct_passes = (
        not correct_result["timed_out"]
        and correct_result["exit_code"] == 0
    )

    usable = (
        bug_exposed
        and correct_passes
    )

    if usable:
        note = "OK"

    elif not correct_passes:
        note = (
            "Correct version does not pass "
            "reference tests"
        )

    elif not bug_exposed:
        note = (
            "Reference tests do not expose "
            "the buggy version"
        )

    else:
        note = "Not usable"

    return {
        "program": program,
        "files_ok": True,
        "buggy_exit_code": (
            buggy_result[
                "exit_code"
            ]
        ),
        "correct_exit_code": (
            correct_result[
                "exit_code"
            ]
        ),
        "buggy_timeout": (
            buggy_result[
                "timed_out"
            ]
        ),
        "correct_timeout": (
            correct_result[
                "timed_out"
            ]
        ),
        "buggy_duration_seconds": (
            buggy_result[
                "duration_seconds"
            ]
        ),
        "correct_duration_seconds": (
            correct_result[
                "duration_seconds"
            ]
        ),
        "bug_exposed_by_reference_tests": (
            bug_exposed
        ),
        "correct_version_passes": (
            correct_passes
        ),
        "candidate_usable": usable,
        "note": note,
    }


def save_csv(
    results: list[dict[str, Any]],
) -> None:
    if not results:
        return

    with OUTPUT_CSV.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=list(
                results[0].keys()
            ),
        )

        writer.writeheader()
        writer.writerows(results)


def print_summary(
    results: list[dict[str, Any]],
) -> None:
    usable = [
        row["program"]
        for row in results
        if row[
            "candidate_usable"
        ]
    ]

    rejected = [
        row["program"]
        for row in results
        if not row[
            "candidate_usable"
        ]
    ]

    print()
    print("=" * 70)
    print("PREPARATION SUMMARY")
    print("=" * 70)

    print(
        f"Candidates checked: "
        f"{len(results)}"
    )

    print(
        f"Usable: "
        f"{len(usable)}"
    )

    print(
        f"Rejected: "
        f"{len(rejected)}"
    )

    print()

    print(
        "Usable candidates:"
    )

    for program in usable:
        print(
            f"  - {program}"
        )

    if rejected:
        print()
        print(
            "Rejected candidates:"
        )

        for program in rejected:
            print(
                f"  - {program}"
            )

    print()
    print(
        f"CSV: {OUTPUT_CSV}"
    )

    print(
        f"Environment: "
        f"{ENVIRONMENT_FILE}"
    )


def main() -> None:
    RESULTS_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    LOGS_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    clone_repository()

    commit_sha = get_commit_sha()

    print()
    print(
        "QuixBugs commit:"
    )
    print(
        commit_sha
    )

    save_environment(
        commit_sha
    )

    print()
    print(
        "Validiram 12 kandidata..."
    )
    print()

    results = []

    for program in CANDIDATES:
        result = validate_candidate(
            program
        )

        results.append(
            result
        )

    save_csv(
        results
    )

    print_summary(
        results
    )


if __name__ == "__main__":
    main()