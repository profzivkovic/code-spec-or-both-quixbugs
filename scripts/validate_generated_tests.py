from __future__ import annotations

import ast
import csv
import json
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

OUTPUT_FILE = (
    PROJECT_ROOT
    / "results"
    / "preparation"
    / "generated_test_validation.csv"
)


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


def load_metadata() -> list[dict]:
    with GENERATION_METADATA.open(
        "r",
        newline="",
        encoding="utf-8",
    ) as file:
        return list(
            csv.DictReader(file)
        )


def count_test_functions(
    tree: ast.AST,
) -> int:
    return sum(
        1
        for node in ast.walk(tree)
        if (
            isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                ),
            )
            and node.name.startswith("test_")
        )
    )


def count_assertions(
    tree: ast.AST,
) -> int:
    return sum(
        1
        for node in ast.walk(tree)
        if isinstance(node, ast.Assert)
    )


def count_pytest_raises(
    tree: ast.AST,
) -> int:
    count = 0

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue

        func = node.func

        if (
            isinstance(func, ast.Attribute)
            and isinstance(func.value, ast.Name)
            and func.value.id == "pytest"
            and func.attr == "raises"
        ):
            count += 1

    return count


def count_parametrize(
    tree: ast.AST,
) -> int:
    count = 0

    for node in ast.walk(tree):
        if not isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
            ),
        ):
            continue

        for decorator in node.decorator_list:
            if not isinstance(
                decorator,
                ast.Call,
            ):
                continue

            func = decorator.func

            if (
                isinstance(func, ast.Attribute)
                and func.attr == "parametrize"
            ):
                count += 1

    return count


def target_redefined(
    tree: ast.AST,
    function_name: str,
) -> bool:
    for node in ast.walk(tree):
        if (
            isinstance(
                node,
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                ),
            )
            and node.name == function_name
        ):
            return True

    return False


def imports_target(
    tree: ast.AST,
    function_name: str,
) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name == function_name:
                    return True

        if isinstance(node, ast.Import):
            for alias in node.names:
                if function_name in alias.name:
                    return True

    return False


def validate_one(
    row: dict,
    task: dict,
) -> dict:
    output_file = row.get(
        "output_file",
        "",
    )

    if not output_file:
        return {
            "run_id": row["run_id"],
            "program": row["program"],
            "condition": row["condition"],
            "generation": row["generation"],
            "file_exists": False,
            "syntax_valid": False,
            "target_redefined": False,
            "target_imported": False,
            "test_function_count": 0,
            "assert_count": 0,
            "pytest_raises_count": 0,
            "parametrize_count": 0,
            "validation_passed": False,
            "error": "No output file recorded",
        }

    path = (
        PROJECT_ROOT
        / output_file
    )

    if not path.exists():
        return {
            "run_id": row["run_id"],
            "program": row["program"],
            "condition": row["condition"],
            "generation": row["generation"],
            "file_exists": False,
            "syntax_valid": False,
            "target_redefined": False,
            "target_imported": False,
            "test_function_count": 0,
            "assert_count": 0,
            "pytest_raises_count": 0,
            "parametrize_count": 0,
            "validation_passed": False,
            "error": "Generated file does not exist",
        }

    source = path.read_text(
        encoding="utf-8",
        errors="replace",
    )

    try:
        tree = ast.parse(source)

    except SyntaxError as error:
        return {
            "run_id": row["run_id"],
            "program": row["program"],
            "condition": row["condition"],
            "generation": row["generation"],
            "file_exists": True,
            "syntax_valid": False,
            "target_redefined": False,
            "target_imported": False,
            "test_function_count": 0,
            "assert_count": 0,
            "pytest_raises_count": 0,
            "parametrize_count": 0,
            "validation_passed": False,
            "error": (
                f"SyntaxError line "
                f"{error.lineno}: "
                f"{error.msg}"
            ),
        }

    function_name = task[
        "function_name"
    ]

    redefined = target_redefined(
        tree,
        function_name,
    )

    imported = imports_target(
        tree,
        function_name,
    )

    test_count = count_test_functions(
        tree
    )

    assert_count = count_assertions(
        tree
    )

    raises_count = count_pytest_raises(
        tree
    )

    parametrize_count = count_parametrize(
        tree
    )

    passed = (
        not redefined
        and not imported
        and test_count > 0
    )

    errors = []

    if redefined:
        errors.append(
            "Target function redefined"
        )

    if imported:
        errors.append(
            "Target function imported"
        )

    if test_count == 0:
        errors.append(
            "No pytest test functions found"
        )

    return {
        "run_id": row["run_id"],
        "program": row["program"],
        "condition": row["condition"],
        "generation": row["generation"],
        "file_exists": True,
        "syntax_valid": True,
        "target_redefined": redefined,
        "target_imported": imported,
        "test_function_count": test_count,
        "assert_count": assert_count,
        "pytest_raises_count": raises_count,
        "parametrize_count": parametrize_count,
        "validation_passed": passed,
        "error": "; ".join(errors),
    }


def save_results(
    results: list[dict],
) -> None:
    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fields = [
        "run_id",
        "program",
        "condition",
        "generation",
        "file_exists",
        "syntax_valid",
        "target_redefined",
        "target_imported",
        "test_function_count",
        "assert_count",
        "pytest_raises_count",
        "parametrize_count",
        "validation_passed",
        "error",
    ]

    with OUTPUT_FILE.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fields,
        )

        writer.writeheader()
        writer.writerows(results)


def main() -> None:
    tasks = load_tasks()
    metadata = load_metadata()

    successful_rows = [
        row
        for row in metadata
        if row["status"] == "success"
    ]

    results = []

    print()
    print(
        "Validiram generisane testove..."
    )
    print()

    for row in successful_rows:
        task = tasks[
            row["program"]
        ]

        result = validate_one(
            row,
            task,
        )

        results.append(result)

        status = (
            "OK"
            if result[
                "validation_passed"
            ]
            else "FAIL"
        )

        print(
            f"{row['run_id']:<35} "
            f"{status:<5} "
            f"tests={result['test_function_count']:<3} "
            f"asserts={result['assert_count']:<3} "
            f"redefined={result['target_redefined']}"
        )

        if result["error"]:
            print(
                f"    {result['error']}"
            )

    save_results(results)

    valid = [
        row
        for row in results
        if row[
            "validation_passed"
        ]
    ]

    syntax_invalid = [
        row
        for row in results
        if not row[
            "syntax_valid"
        ]
    ]

    redefined = [
        row
        for row in results
        if row[
            "target_redefined"
        ]
    ]

    imported = [
        row
        for row in results
        if row[
            "target_imported"
        ]
    ]

    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print(
        f"Generated suites checked: "
        f"{len(results)}"
    )

    print(
        f"Validation passed: "
        f"{len(valid)}"
    )

    print(
        f"Syntax invalid: "
        f"{len(syntax_invalid)}"
    )

    print(
        f"Target redefined: "
        f"{len(redefined)}"
    )

    print(
        f"Target imported: "
        f"{len(imported)}"
    )

    print()
    print(
        f"Report: {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()