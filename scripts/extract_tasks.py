from __future__ import annotations

import ast
import copy
import csv
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
QUIXBUGS = PROJECT_ROOT / "external" / "QuixBugs"

BUGGY_DIR = QUIXBUGS / "python_programs"
CORRECT_DIR = QUIXBUGS / "correct_python_programs"

OUTPUT_DIR = PROJECT_ROOT / "results" / "preparation"
OUTPUT_CSV = OUTPUT_DIR / "tasks.csv"
OUTPUT_JSON = OUTPUT_DIR / "tasks.json"


PROGRAMS = [
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


def load_source(path: Path) -> str:
    return path.read_text(
        encoding="utf-8",
        errors="replace",
    )


def parse_module(source: str) -> ast.Module:
    return ast.parse(source)


def find_target_function(
    tree: ast.Module,
    program: str,
) -> ast.FunctionDef | ast.AsyncFunctionDef:
    functions = [
        node
        for node in tree.body
        if isinstance(
            node,
            (ast.FunctionDef, ast.AsyncFunctionDef),
        )
    ]

    for function in functions:
        if function.name.lower() == program.lower():
            return function

    if len(functions) == 1:
        return functions[0]

    names = [
        function.name
        for function in functions
    ]

    raise RuntimeError(
        f"Ne mogu jednoznacno da odredim funkciju za {program}. "
        f"Pronadjene funkcije: {names}"
    )


def format_argument(argument: ast.arg) -> str:
    if argument.annotation is None:
        return argument.arg

    return (
        f"{argument.arg}: "
        f"{ast.unparse(argument.annotation)}"
    )


def extract_signature(
    function: ast.FunctionDef | ast.AsyncFunctionDef,
) -> str:
    args = function.args
    parts: list[str] = []

    positional = (
        list(args.posonlyargs)
        + list(args.args)
    )

    default_offset = (
        len(positional)
        - len(args.defaults)
    )

    for index, argument in enumerate(positional):
        text = format_argument(argument)

        if index >= default_offset:
            default = args.defaults[
                index - default_offset
            ]

            text += "=" + ast.unparse(default)

        parts.append(text)

    if args.vararg is not None:
        parts.append(
            "*" + format_argument(args.vararg)
        )
    elif args.kwonlyargs:
        parts.append("*")

    for argument, default in zip(
        args.kwonlyargs,
        args.kw_defaults,
    ):
        text = format_argument(argument)

        if default is not None:
            text += "=" + ast.unparse(default)

        parts.append(text)

    if args.kwarg is not None:
        parts.append(
            "**" + format_argument(args.kwarg)
        )

    signature = (
        f"{function.name}("
        + ", ".join(parts)
        + ")"
    )

    if function.returns is not None:
        signature += (
            " -> "
            + ast.unparse(function.returns)
        )

    return signature


def looks_like_specification(text: str) -> bool:
    normalized = text.lower()

    markers = [
        "input:",
        "output:",
        "precondition:",
        "postcondition:",
        "example:",
    ]

    marker_count = sum(
        marker in normalized
        for marker in markers
    )

    # Some QuixBugs specs only contain Input and Output.
    return marker_count >= 2


def is_specification_node(node: ast.AST) -> bool:
    if not isinstance(node, ast.Expr):
        return False

    if not isinstance(node.value, ast.Constant):
        return False

    if not isinstance(node.value.value, str):
        return False

    return looks_like_specification(
        node.value.value
    )


def extract_specification(
    tree: ast.Module,
) -> str:
    """
    QuixBugs stores natural-language specifications as standalone
    triple-quoted strings at module level, usually after the function.
    """

    blocks: list[str] = []

    for node in tree.body:
        if is_specification_node(node):
            text = node.value.value.strip()

            if text:
                blocks.append(text)

    # Preserve order while removing duplicates.
    unique_blocks = list(
        dict.fromkeys(blocks)
    )

    return "\n\n".join(
        unique_blocks
    )


def create_code_only_source(
    tree: ast.Module,
) -> str:
    """
    Return the buggy Python source without benchmark specification
    blocks. Imports, helper definitions, and implementation code remain.
    """

    clean_tree = copy.deepcopy(tree)

    clean_tree.body = [
        node
        for node in clean_tree.body
        if not is_specification_node(node)
    ]

    ast.fix_missing_locations(
        clean_tree
    )

    return (
        ast.unparse(clean_tree).strip()
        + "\n"
    )


def extract_task(program: str) -> dict:
    buggy_path = (
        BUGGY_DIR
        / f"{program}.py"
    )

    correct_path = (
        CORRECT_DIR
        / f"{program}.py"
    )

    if not buggy_path.exists():
        raise FileNotFoundError(
            buggy_path
        )

    if not correct_path.exists():
        raise FileNotFoundError(
            correct_path
        )

    buggy_source = load_source(
        buggy_path
    )

    correct_source = load_source(
        correct_path
    )

    tree = parse_module(
        buggy_source
    )

    function = find_target_function(
        tree,
        program,
    )

    signature = extract_signature(
        function
    )

    specification = extract_specification(
        tree
    )

    code_only_source = (
        create_code_only_source(
            tree
        )
    )

    return {
        "program": program,
        "function_name": function.name,
        "signature": signature,
        "specification": specification,
        "code_only_source": code_only_source,
        "buggy_source": buggy_source,
        "correct_source": correct_source,
        "has_specification": bool(
            specification.strip()
        ),
        "code_only_loc": len(
            code_only_source.splitlines()
        ),
        "buggy_file_loc": len(
            buggy_source.splitlines()
        ),
        "correct_file_loc": len(
            correct_source.splitlines()
        ),
    }


def save_json(tasks: list[dict]) -> None:
    OUTPUT_JSON.write_text(
        json.dumps(
            tasks,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def save_csv(tasks: list[dict]) -> None:
    """
    CSV contains only summary fields and the specification.
    Full source code remains in tasks.json.
    """

    fields = [
        "program",
        "function_name",
        "signature",
        "has_specification",
        "code_only_loc",
        "buggy_file_loc",
        "correct_file_loc",
        "specification",
    ]

    with OUTPUT_CSV.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fields,
        )

        writer.writeheader()

        for task in tasks:
            writer.writerow(
                {
                    field: task[field]
                    for field in fields
                }
            )


def preview_specification(
    specification: str,
) -> str:
    if not specification:
        return "-"

    nonempty_lines = [
        line.strip()
        for line in specification.splitlines()
        if line.strip()
    ]

    if not nonempty_lines:
        return "-"

    preview = " | ".join(
        nonempty_lines[:3]
    )

    if len(preview) > 70:
        preview = (
            preview[:67]
            + "..."
        )

    return preview


def main() -> None:
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    tasks: list[dict] = []

    print(
        "Izvlacim QuixBugs zadatke..."
    )
    print()

    for program in PROGRAMS:
        task = extract_task(
            program
        )

        tasks.append(
            task
        )

        status = (
            "YES"
            if task["has_specification"]
            else "NO"
        )

        print(
            f"{program:<30} "
            f"function={task['function_name']:<30} "
            f"spec={status:<3} "
            f"codeLOC={task['code_only_loc']}"
        )

        if task["has_specification"]:
            print(
                "    "
                + preview_specification(
                    task["specification"]
                )
            )

    save_json(
        tasks
    )

    save_csv(
        tasks
    )

    missing_specs = [
        task["program"]
        for task in tasks
        if not task[
            "has_specification"
        ]
    ]

    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print(
        f"Tasks: {len(tasks)}"
    )

    print(
        "With specification: "
        f"{len(tasks) - len(missing_specs)}"
    )

    print(
        "Without specification: "
        f"{len(missing_specs)}"
    )

    if missing_specs:
        print()
        print(
            "Programs without specification:"
        )

        for program in missing_specs:
            print(
                f"  - {program}"
            )

    print()
    print(
        f"CSV:  {OUTPUT_CSV}"
    )

    print(
        f"JSON: {OUTPUT_JSON}"
    )


if __name__ == "__main__":
    main()