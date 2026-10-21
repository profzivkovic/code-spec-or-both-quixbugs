from __future__ import annotations

import itertools
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

GENERATION_FILE = (
    PROJECT_ROOT
    / "results"
    / "raw"
    / "generation_metadata.csv"
)

VALIDATION_FILE = (
    PROJECT_ROOT
    / "results"
    / "preparation"
    / "generated_test_validation.csv"
)

EVALUATION_FILE = (
    PROJECT_ROOT
    / "results"
    / "raw"
    / "evaluation_results.csv"
)

PER_TEST_FILE = (
    PROJECT_ROOT
    / "results"
    / "raw"
    / "per_test_results.csv"
)

OUTPUT_ROOT = (
    PROJECT_ROOT
    / "results"
    / "paper"
)

TABLE_DIR = (
    OUTPUT_ROOT
    / "tables"
)

FIGURE_DIR = (
    OUTPUT_ROOT
    / "figures"
)

MASTER_FILE = (
    OUTPUT_ROOT
    / "master_results.csv"
)

SUMMARY_FILE = (
    OUTPUT_ROOT
    / "paper_results_summary.txt"
)


CONDITIONS = [
    "CODE",
    "SPEC",
    "BOTH",
]

BOOTSTRAP_ITERATIONS = 10_000
BOOTSTRAP_SEED = 2026


def ensure_directories() -> None:
    TABLE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    FIGURE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


def boolean_series(
    series: pd.Series,
) -> pd.Series:
    if pd.api.types.is_bool_dtype(
        series
    ):
        return series.fillna(False)

    return (
        series
        .astype(str)
        .str.strip()
        .str.lower()
        .map(
            {
                "true": True,
                "false": False,
                "1": True,
                "0": False,
            }
        )
        .fillna(False)
        .astype(bool)
    )


def numeric_series(
    series: pd.Series,
) -> pd.Series:
    return pd.to_numeric(
        series,
        errors="coerce",
    )


def percent(
    numerator: float,
    denominator: float,
) -> float:
    if denominator == 0:
        return 0.0

    return round(
        numerator
        / denominator
        * 100,
        2,
    )


def load_data() -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
    pd.DataFrame,
]:
    generation = pd.read_csv(
        GENERATION_FILE
    )

    validation = pd.read_csv(
        VALIDATION_FILE
    )

    evaluation = pd.read_csv(
        EVALUATION_FILE
    )

    per_test = pd.read_csv(
        PER_TEST_FILE
    )

    return (
        generation,
        validation,
        evaluation,
        per_test,
    )


def prepare_master(
    generation: pd.DataFrame,
    validation: pd.DataFrame,
    evaluation: pd.DataFrame,
) -> pd.DataFrame:
    evaluation = evaluation.copy()

    bool_columns = [
        "syntax_valid",
        "correct_executable",
        "oracle_correct",
        "bug_detected",
        "correct_timeout",
        "buggy_timeout",
    ]

    for column in bool_columns:
        if column in evaluation:
            evaluation[column] = (
                boolean_series(
                    evaluation[column]
                )
            )

    generation_columns = [
        "run_id",
        "model",
        "temperature",
        "prompt_tokens",
        "output_tokens",
        "wall_time_seconds",
        "total_duration_seconds",
        "load_duration_seconds",
        "prompt_eval_seconds",
        "generation_seconds",
        "output_tokens_per_second",
        "output_chars",
        "output_lines",
        "prompt_sha256",
    ]

    generation_subset = (
        generation[
            [
                column
                for column
                in generation_columns
                if column
                in generation.columns
            ]
        ]
        .copy()
    )

    validation_columns = [
        "run_id",
        "validation_passed",
        "target_redefined",
        "target_imported",
        "test_function_count",
        "assert_count",
        "pytest_raises_count",
        "parametrize_count",
    ]

    validation_subset = (
        validation[
            [
                column
                for column
                in validation_columns
                if column
                in validation.columns
            ]
        ]
        .copy()
    )

    master = evaluation.merge(
        generation_subset,
        on="run_id",
        how="left",
    )

    master = master.merge(
        validation_subset,
        on="run_id",
        how="left",
    )

    master["condition"] = (
        master["condition"]
        .astype(str)
        .str.upper()
    )

    master["generation"] = (
        numeric_series(
            master["generation"]
        )
    )

    additional_bool_columns = [
        "validation_passed",
        "target_redefined",
        "target_imported",
    ]

    for column in additional_bool_columns:
        if column in master:
            master[column] = (
                boolean_series(
                    master[column]
                )
            )

    numeric_columns = [
        "test_function_count",
        "assert_count",
        "pytest_raises_count",
        "parametrize_count",
        "prompt_tokens",
        "output_tokens",
        "wall_time_seconds",
        "total_duration_seconds",
        "generation_seconds",
        "output_tokens_per_second",
        "output_chars",
        "output_lines",
        "correct_collected",
        "correct_passed",
        "correct_failed",
        "correct_errors",
        "correct_line_coverage_percent",
        "correct_branch_coverage_percent",
        "buggy_collected",
        "buggy_passed",
        "buggy_failed",
        "buggy_errors",
        "buggy_line_coverage_percent",
        "buggy_branch_coverage_percent",
    ]

    for column in numeric_columns:
        if column in master:
            master[column] = (
                numeric_series(
                    master[column]
                )
            )

    master["execution_timeout"] = (
        master["correct_timeout"]
    )

    def report_outcome(
        row: pd.Series,
    ) -> str:
        if not row["syntax_valid"]:
            return "invalid_syntax"

        if row["correct_timeout"]:
            return "execution_timeout"

        return str(
            row["classification"]
        )

    master["report_outcome"] = (
        master.apply(
            report_outcome,
            axis=1,
        )
    )

    master = master.sort_values(
        [
            "program",
            "condition",
            "generation",
        ]
    ).reset_index(drop=True)

    master.to_csv(
        MASTER_FILE,
        index=False,
    )

    return master


def create_condition_summary(
    master: pd.DataFrame,
) -> pd.DataFrame:
    rows = []

    program_count = (
        master["program"].nunique()
    )

    for condition in CONDITIONS:
        data = master[
            master["condition"]
            == condition
        ]

        n = len(data)

        syntax = int(
            data["syntax_valid"].sum()
        )

        executable = int(
            data[
                "correct_executable"
            ].sum()
        )

        oracle = int(
            data["oracle_correct"].sum()
        )

        detected = int(
            data["bug_detected"].sum()
        )

        oracle_errors = int(
            (
                data["classification"]
                == "oracle_error"
            ).sum()
        )

        timeouts = int(
            data[
                "correct_timeout"
            ].sum()
        )

        invalid = int(
            (
                ~data["syntax_valid"]
            ).sum()
        )

        detected_programs = int(
            data.groupby(
                "program"
            )["bug_detected"]
            .any()
            .sum()
        )

        rows.append(
            {
                "condition": condition,
                "suites": n,

                "syntax_valid_n": syntax,
                "syntax_valid_pct": percent(
                    syntax,
                    n,
                ),

                "executable_n": executable,
                "executable_pct": percent(
                    executable,
                    n,
                ),

                "oracle_correct_n": oracle,
                "oracle_correct_pct": (
                    percent(
                        oracle,
                        n,
                    )
                ),

                "bug_detecting_n": (
                    detected
                ),
                "bug_detecting_pct": (
                    percent(
                        detected,
                        n,
                    )
                ),

                "oracle_error_n": (
                    oracle_errors
                ),
                "oracle_error_pct": (
                    percent(
                        oracle_errors,
                        n,
                    )
                ),

                "execution_timeout_n": (
                    timeouts
                ),

                "invalid_syntax_n": (
                    invalid
                ),

                "unique_bugs_detected_n": (
                    detected_programs
                ),

                "unique_bugs_detected_pct": (
                    percent(
                        detected_programs,
                        program_count,
                    )
                ),

                "oracle_correct_among_executable_pct": (
                    percent(
                        oracle,
                        executable,
                    )
                ),
            }
        )

    result = pd.DataFrame(rows)

    result.to_csv(
        TABLE_DIR
        / "condition_summary.csv",
        index=False,
    )

    return result


def create_outcome_table(
    master: pd.DataFrame,
) -> pd.DataFrame:
    categories = [
        "bug_detecting",
        "oracle_error",
        "execution_timeout",
        "invalid_syntax",
        "valid_no_detection",
        "not_executable",
    ]

    rows = []

    for condition in CONDITIONS:
        data = master[
            master["condition"]
            == condition
        ]

        n = len(data)

        for category in categories:
            count = int(
                (
                    data[
                        "report_outcome"
                    ]
                    == category
                ).sum()
            )

            rows.append(
                {
                    "condition": (
                        condition
                    ),
                    "outcome": category,
                    "count": count,
                    "percent": percent(
                        count,
                        n,
                    ),
                }
            )

    result = pd.DataFrame(rows)

    result.to_csv(
        TABLE_DIR
        / "outcome_distribution.csv",
        index=False,
    )

    return result


def create_program_results(
    master: pd.DataFrame,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
]:
    rows = []

    for (
        program,
        condition,
    ), data in master.groupby(
        [
            "program",
            "condition",
        ]
    ):
        rows.append(
            {
                "program": program,
                "condition": condition,
                "runs": len(data),
                "syntax_valid": int(
                    data[
                        "syntax_valid"
                    ].sum()
                ),
                "oracle_correct": int(
                    data[
                        "oracle_correct"
                    ].sum()
                ),
                "bug_detections": int(
                    data[
                        "bug_detected"
                    ].sum()
                ),
                "bug_detected_any": bool(
                    data[
                        "bug_detected"
                    ].any()
                ),
                "oracle_errors": int(
                    (
                        data[
                            "classification"
                        ]
                        == "oracle_error"
                    ).sum()
                ),
                "execution_timeouts": int(
                    data[
                        "correct_timeout"
                    ].sum()
                ),
            }
        )

    long = pd.DataFrame(rows)

    long.to_csv(
        TABLE_DIR
        / "program_condition_results.csv",
        index=False,
    )

    matrix = (
        long.pivot(
            index="program",
            columns="condition",
            values="bug_detections",
        )
        .reindex(
            columns=CONDITIONS
        )
        .fillna(0)
        .astype(int)
    )

    matrix.to_csv(
        TABLE_DIR
        / "bug_detection_matrix.csv"
    )

    return long, matrix


def create_stability_results(
    program_results: pd.DataFrame,
) -> pd.DataFrame:
    rows = []

    for condition in CONDITIONS:
        data = program_results[
            program_results[
                "condition"
            ]
            == condition
        ]

        counts = (
            data[
                "bug_detections"
            ]
            .value_counts()
        )

        rows.append(
            {
                "condition": condition,
                "detected_0_of_3": int(
                    counts.get(
                        0,
                        0,
                    )
                ),
                "detected_1_of_3": int(
                    counts.get(
                        1,
                        0,
                    )
                ),
                "detected_2_of_3": int(
                    counts.get(
                        2,
                        0,
                    )
                ),
                "detected_3_of_3": int(
                    counts.get(
                        3,
                        0,
                    )
                ),
                "programs_detected_any": int(
                    (
                        data[
                            "bug_detections"
                        ]
                        > 0
                    ).sum()
                ),
                "programs_detected_all": int(
                    (
                        data[
                            "bug_detections"
                        ]
                        == 3
                    ).sum()
                ),
            }
        )

    result = pd.DataFrame(rows)

    result.to_csv(
        TABLE_DIR
        / "detection_stability.csv",
        index=False,
    )

    return result


def create_cumulative_detection(
    master: pd.DataFrame,
) -> pd.DataFrame:
    rows = []

    for condition in CONDITIONS:
        condition_data = master[
            master["condition"]
            == condition
        ]

        programs = sorted(
            condition_data[
                "program"
            ].unique()
        )

        for budget in [
            1,
            2,
            3,
        ]:
            observed = 0

            for program in programs:
                data = condition_data[
                    condition_data[
                        "program"
                    ]
                    == program
                ]

                detected = data[
                    data["generation"]
                    <= budget
                ][
                    "bug_detected"
                ].any()

                observed += int(
                    detected
                )

            permutation_expected = 0.0

            for program in programs:
                values = (
                    condition_data[
                        condition_data[
                            "program"
                        ]
                        == program
                    ]
                    .sort_values(
                        "generation"
                    )[
                        "bug_detected"
                    ]
                    .astype(bool)
                    .tolist()
                )

                permutations = list(
                    itertools.permutations(
                        values
                    )
                )

                probabilities = [
                    any(
                        permutation[
                            :budget
                        ]
                    )
                    for permutation
                    in permutations
                ]

                permutation_expected += (
                    float(
                        np.mean(
                            probabilities
                        )
                    )
                )

            rows.append(
                {
                    "condition": (
                        condition
                    ),
                    "generation_budget": (
                        budget
                    ),
                    "observed_programs_detected": (
                        observed
                    ),
                    "observed_pct": percent(
                        observed,
                        len(programs),
                    ),
                    "permutation_expected_programs_detected": round(
                        permutation_expected,
                        3,
                    ),
                    "permutation_expected_pct": round(
                        permutation_expected
                        / len(programs)
                        * 100,
                        2,
                    ),
                }
            )

    result = pd.DataFrame(rows)

    result.to_csv(
        TABLE_DIR
        / "cumulative_detection.csv",
        index=False,
    )

    return result


def describe_metric(
    values: pd.Series,
) -> dict:
    values = (
        pd.to_numeric(
            values,
            errors="coerce",
        )
        .dropna()
    )

    if len(values) == 0:
        return {
            "n": 0,
            "mean": np.nan,
            "median": np.nan,
            "std": np.nan,
            "min": np.nan,
            "max": np.nan,
        }

    return {
        "n": len(values),
        "mean": round(
            float(values.mean()),
            3,
        ),
        "median": round(
            float(values.median()),
            3,
        ),
        "std": round(
            float(values.std()),
            3,
        ),
        "min": round(
            float(values.min()),
            3,
        ),
        "max": round(
            float(values.max()),
            3,
        ),
    }


def create_coverage_summary(
    master: pd.DataFrame,
) -> pd.DataFrame:
    rows = []

    scopes = {
        "all_executable": (
            master[
                "correct_executable"
            ]
        ),
        "oracle_correct_only": (
            master[
                "oracle_correct"
            ]
        ),
        "oracle_error_only": (
            master[
                "classification"
            ]
            == "oracle_error"
        ),
    }

    for scope_name, scope_mask in (
        scopes.items()
    ):
        scope = master[
            scope_mask
        ]

        for condition in CONDITIONS:
            data = scope[
                scope["condition"]
                == condition
            ]

            line = describe_metric(
                data[
                    "correct_line_coverage_percent"
                ]
            )

            branch = describe_metric(
                data[
                    "correct_branch_coverage_percent"
                ]
            )

            rows.append(
                {
                    "scope": scope_name,
                    "condition": condition,

                    "line_n": line["n"],
                    "line_mean": line[
                        "mean"
                    ],
                    "line_median": line[
                        "median"
                    ],
                    "line_std": line[
                        "std"
                    ],
                    "line_min": line[
                        "min"
                    ],
                    "line_max": line[
                        "max"
                    ],

                    "branch_n": branch[
                        "n"
                    ],
                    "branch_mean": branch[
                        "mean"
                    ],
                    "branch_median": branch[
                        "median"
                    ],
                    "branch_std": branch[
                        "std"
                    ],
                    "branch_min": branch[
                        "min"
                    ],
                    "branch_max": branch[
                        "max"
                    ],
                }
            )

    result = pd.DataFrame(rows)

    result.to_csv(
        TABLE_DIR
        / "coverage_summary.csv",
        index=False,
    )

    return result


def create_structure_summary(
    master: pd.DataFrame,
) -> pd.DataFrame:
    rows = []

    metrics = [
        "test_function_count",
        "assert_count",
        "pytest_raises_count",
        "parametrize_count",
        "correct_collected",
    ]

    valid = master[
        master["syntax_valid"]
    ]

    for condition in CONDITIONS:
        data = valid[
            valid["condition"]
            == condition
        ]

        row = {
            "condition": condition,
            "n": len(data),
        }

        for metric in metrics:
            stats = describe_metric(
                data[metric]
            )

            row[
                f"{metric}_mean"
            ] = stats["mean"]

            row[
                f"{metric}_median"
            ] = stats["median"]

        rows.append(row)

    result = pd.DataFrame(rows)

    result.to_csv(
        TABLE_DIR
        / "test_structure_summary.csv",
        index=False,
    )

    return result


def create_generation_summary(
    master: pd.DataFrame,
) -> pd.DataFrame:
    rows = []

    metrics = [
        "prompt_tokens",
        "output_tokens",
        "total_duration_seconds",
        "generation_seconds",
        "output_tokens_per_second",
        "output_chars",
        "output_lines",
    ]

    for condition in CONDITIONS:
        data = master[
            master["condition"]
            == condition
        ]

        row = {
            "condition": condition,
            "n": len(data),
        }

        for metric in metrics:
            stats = describe_metric(
                data[metric]
            )

            row[
                f"{metric}_mean"
            ] = stats["mean"]

            row[
                f"{metric}_median"
            ] = stats["median"]

        detected = int(
            data[
                "bug_detected"
            ].sum()
        )

        total_tokens = float(
            data[
                "output_tokens"
            ]
            .fillna(0)
            .sum()
        )

        total_seconds = float(
            data[
                "total_duration_seconds"
            ]
            .fillna(0)
            .sum()
        )

        row[
            "bug_detections"
        ] = detected

        row[
            "detections_per_1000_output_tokens"
        ] = (
            round(
                detected
                / total_tokens
                * 1000,
                4,
            )
            if total_tokens > 0
            else 0.0
        )

        row[
            "detections_per_generation_minute"
        ] = (
            round(
                detected
                / (
                    total_seconds
                    / 60
                ),
                4,
            )
            if total_seconds > 0
            else 0.0
        )

        rows.append(row)

    result = pd.DataFrame(rows)

    result.to_csv(
        TABLE_DIR
        / "generation_summary.csv",
        index=False,
    )

    return result


def create_per_test_analysis(
    per_test: pd.DataFrame,
    master: pd.DataFrame,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
]:
    correct = per_test[
        per_test["variant"]
        == "correct"
    ].copy()

    buggy = per_test[
        per_test["variant"]
        == "buggy"
    ].copy()

    keys = [
        "run_id",
        "classname",
        "test_name",
    ]

    correct = correct[
        keys
        + [
            "status",
            "time_seconds",
        ]
    ].rename(
        columns={
            "status": (
                "correct_status"
            ),
            "time_seconds": (
                "correct_time_seconds"
            ),
        }
    )

    buggy = buggy[
        keys
        + [
            "status",
            "time_seconds",
        ]
    ].rename(
        columns={
            "status": (
                "buggy_status"
            ),
            "time_seconds": (
                "buggy_time_seconds"
            ),
        }
    )

    paired = correct.merge(
        buggy,
        on=keys,
        how="outer",
    )

    metadata = master[
        [
            "run_id",
            "program",
            "condition",
            "generation",
            "oracle_correct",
        ]
    ].drop_duplicates(
        "run_id"
    )

    paired = paired.merge(
        metadata,
        on="run_id",
        how="left",
    )

    paired[
        "individual_oracle_correct"
    ] = (
        paired[
            "correct_status"
        ]
        == "passed"
    )

    paired[
        "individual_bug_revealing"
    ] = (
        (
            paired[
                "correct_status"
            ]
            == "passed"
        )
        &
        (
            paired[
                "buggy_status"
            ]
            .isin(
                [
                    "failed",
                    "error",
                ]
            )
        )
    )

    paired.to_csv(
        TABLE_DIR
        / "per_test_paired_results.csv",
        index=False,
    )

    rows = []

    for condition in CONDITIONS:
        data = paired[
            paired["condition"]
            == condition
        ]

        oracle_valid_tests = int(
            data[
                "individual_oracle_correct"
            ].sum()
        )

        revealing = int(
            data[
                "individual_bug_revealing"
            ].sum()
        )

        rows.append(
            {
                "condition": condition,
                "matched_test_cases": (
                    len(data)
                ),
                "individual_oracle_correct_tests": (
                    oracle_valid_tests
                ),
                "individual_bug_revealing_tests": (
                    revealing
                ),
                "bug_revealing_among_oracle_correct_pct": (
                    percent(
                        revealing,
                        oracle_valid_tests,
                    )
                ),
            }
        )

    summary = pd.DataFrame(rows)

    summary.to_csv(
        TABLE_DIR
        / "per_test_summary.csv",
        index=False,
    )

    return (
        paired,
        summary,
    )


def create_filtered_detection(
    paired: pd.DataFrame,
    master: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Secondary suite-level detection after filtering incorrect tests.

    Tests that do not pass on the correct implementation are discarded.
    A suite is filtered-detecting when at least one remaining test fails or
    errors on the buggy implementation. Suites with no remaining test are
    counted as non-detecting.
    """
    per_run_rows = []

    for run_id, run in paired.groupby("run_id", dropna=False):
        retained = run[run["correct_status"] == "passed"]
        filtered_detected = bool(
            retained["buggy_status"].isin(["failed", "error"]).any()
        )

        meta = master[master["run_id"] == run_id].iloc[0]
        per_run_rows.append(
            {
                "run_id": run_id,
                "program": meta["program"],
                "condition": meta["condition"],
                "generation": meta["generation"],
                "strict_bug_detected": bool(meta["bug_detected"]),
                "retained_tests": int(len(retained)),
                "filtered_bug_detected": filtered_detected,
            }
        )

    per_run = pd.DataFrame(per_run_rows)

    # Preserve all generated suites in the denominator, including runs that
    # produced no matchable per-test records (e.g., syntax failure/timeout).
    all_runs = master[[
        "run_id", "program", "condition", "generation", "bug_detected"
    ]].drop_duplicates("run_id")

    per_run = all_runs.merge(
        per_run,
        on=["run_id", "program", "condition", "generation"],
        how="left",
        suffixes=("_master", ""),
    )
    per_run["strict_bug_detected"] = per_run["bug_detected"].astype(bool)
    per_run["retained_tests"] = per_run["retained_tests"].fillna(0).astype(int)
    per_run["filtered_bug_detected"] = (
        per_run["filtered_bug_detected"].fillna(False).astype(bool)
    )
    per_run = per_run.drop(columns=["bug_detected"])

    per_run.to_csv(
        TABLE_DIR / "filtered_detection_per_run.csv",
        index=False,
    )

    rows = []
    program_count = master["program"].nunique()
    for condition in CONDITIONS:
        data = per_run[per_run["condition"] == condition]
        filtered_n = int(data["filtered_bug_detected"].sum())
        strict_n = int(data["strict_bug_detected"].sum())
        filtered_programs = int(
            data.groupby("program")["filtered_bug_detected"].any().sum()
        )
        rows.append(
            {
                "condition": condition,
                "suites": len(data),
                "strict_detecting_n": strict_n,
                "strict_detecting_pct": percent(strict_n, len(data)),
                "filtered_detecting_n": filtered_n,
                "filtered_detecting_pct": percent(filtered_n, len(data)),
                "filtered_unique_bugs_n": filtered_programs,
                "filtered_unique_bugs_pct": percent(filtered_programs, program_count),
            }
        )

    summary = pd.DataFrame(rows)
    summary.to_csv(
        TABLE_DIR / "filtered_detection_summary.csv",
        index=False,
    )

    print()
    print("FILTERED SUITE-LEVEL DETECTION")
    print("-" * 76)
    for _, row in summary.iterrows():
        print(
            f"{row['condition']}: strict {int(row['strict_detecting_n'])}/{int(row['suites'])} "
            f"({row['strict_detecting_pct']:.2f}%), filtered "
            f"{int(row['filtered_detecting_n'])}/{int(row['suites'])} "
            f"({row['filtered_detecting_pct']:.2f}%), unique bugs "
            f"{int(row['filtered_unique_bugs_n'])}/{program_count}"
        )

    return per_run, summary


def cluster_bootstrap(
    program_results: pd.DataFrame,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
]:
    pivot = (
        program_results.pivot(
            index="program",
            columns="condition",
            values="bug_detections",
        )
        .reindex(
            columns=CONDITIONS
        )
        .astype(float)
    )

    suite_rates = (
        pivot
        / 3.0
    )

    any_detection = (
        pivot > 0
    ).astype(float)

    rng = np.random.default_rng(
        BOOTSTRAP_SEED
    )

    n_programs = len(pivot)

    condition_bootstrap = {
        condition: []
        for condition in CONDITIONS
    }

    unique_bootstrap = {
        condition: []
        for condition in CONDITIONS
    }

    pair_names = [
        ("SPEC", "CODE"),
        ("BOTH", "CODE"),
        ("BOTH", "SPEC"),
    ]

    pair_bootstrap = {
        pair: []
        for pair in pair_names
    }

    for _ in range(
        BOOTSTRAP_ITERATIONS
    ):
        indices = rng.integers(
            0,
            n_programs,
            size=n_programs,
        )

        sampled_suite = (
            suite_rates.iloc[
                indices
            ]
        )

        sampled_any = (
            any_detection.iloc[
                indices
            ]
        )

        for condition in CONDITIONS:
            condition_bootstrap[
                condition
            ].append(
                float(
                    sampled_suite[
                        condition
                    ].mean()
                )
            )

            unique_bootstrap[
                condition
            ].append(
                float(
                    sampled_any[
                        condition
                    ].mean()
                )
            )

        for high, low in pair_names:
            difference = float(
                (
                    sampled_suite[high]
                    - sampled_suite[low]
                ).mean()
            )

            pair_bootstrap[
                (high, low)
            ].append(
                difference
            )

    condition_rows = []

    for condition in CONDITIONS:
        suite_values = np.array(
            condition_bootstrap[
                condition
            ]
        )

        unique_values = np.array(
            unique_bootstrap[
                condition
            ]
        )

        observed_suite = float(
            suite_rates[
                condition
            ].mean()
        )

        observed_unique = float(
            any_detection[
                condition
            ].mean()
        )

        condition_rows.append(
            {
                "condition": condition,

                "suite_detection_rate": round(
                    observed_suite
                    * 100,
                    2,
                ),

                "suite_detection_ci_low": round(
                    np.percentile(
                        suite_values,
                        2.5,
                    )
                    * 100,
                    2,
                ),

                "suite_detection_ci_high": round(
                    np.percentile(
                        suite_values,
                        97.5,
                    )
                    * 100,
                    2,
                ),

                "unique_bug_detection_rate": round(
                    observed_unique
                    * 100,
                    2,
                ),

                "unique_bug_detection_ci_low": round(
                    np.percentile(
                        unique_values,
                        2.5,
                    )
                    * 100,
                    2,
                ),

                "unique_bug_detection_ci_high": round(
                    np.percentile(
                        unique_values,
                        97.5,
                    )
                    * 100,
                    2,
                ),
            }
        )

    condition_ci = pd.DataFrame(
        condition_rows
    )

    condition_ci.to_csv(
        TABLE_DIR
        / "bootstrap_condition_intervals.csv",
        index=False,
    )

    pair_rows = []

    for high, low in pair_names:
        values = np.array(
            pair_bootstrap[
                (high, low)
            ]
        )

        observed = float(
            (
                suite_rates[high]
                - suite_rates[low]
            ).mean()
        )

        pair_rows.append(
            {
                "comparison": (
                    f"{high} - {low}"
                ),

                "difference_percentage_points": round(
                    observed
                    * 100,
                    2,
                ),

                "bootstrap_ci_low": round(
                    np.percentile(
                        values,
                        2.5,
                    )
                    * 100,
                    2,
                ),

                "bootstrap_ci_high": round(
                    np.percentile(
                        values,
                        97.5,
                    )
                    * 100,
                    2,
                ),
            }
        )

    pair_ci = pd.DataFrame(
        pair_rows
    )

    pair_ci.to_csv(
        TABLE_DIR
        / "bootstrap_pairwise_differences.csv",
        index=False,
    )

    return (
        condition_ci,
        pair_ci,
    )


def exact_mcnemar_p(
    b: int,
    c: int,
) -> float:
    n = b + c

    if n == 0:
        return 1.0

    smaller = min(
        b,
        c,
    )

    probability = sum(
        math.comb(
            n,
            k,
        )
        for k in range(
            smaller + 1
        )
    ) / (2 ** n)

    return min(
        1.0,
        2 * probability,
    )


def create_pairwise_statistics(
    program_results: pd.DataFrame,
) -> pd.DataFrame:
    pivot = (
        program_results.pivot(
            index="program",
            columns="condition",
            values="bug_detections",
        )
        .reindex(
            columns=CONDITIONS
        )
    )

    any_detected = (
        pivot > 0
    )

    comparisons = [
        ("CODE", "SPEC"),
        ("CODE", "BOTH"),
        ("SPEC", "BOTH"),
    ]

    rows = []

    for first, second in comparisons:
        first_only = int(
            (
                any_detected[first]
                &
                ~any_detected[
                    second
                ]
            ).sum()
        )

        second_only = int(
            (
                ~any_detected[first]
                &
                any_detected[
                    second
                ]
            ).sum()
        )

        both = int(
            (
                any_detected[first]
                &
                any_detected[
                    second
                ]
            ).sum()
        )

        neither = int(
            (
                ~any_detected[first]
                &
                ~any_detected[
                    second
                ]
            ).sum()
        )

        p_value = (
            exact_mcnemar_p(
                first_only,
                second_only,
            )
        )

        rows.append(
            {
                "comparison": (
                    f"{first} vs {second}"
                ),
                f"{first}_only": (
                    first_only
                ),
                f"{second}_only": (
                    second_only
                ),
                "both_detect": both,
                "neither_detect": neither,
                "discordant_pairs": (
                    first_only
                    + second_only
                ),
                "exact_mcnemar_p": round(
                    p_value,
                    6,
                ),
            }
        )

    result = pd.DataFrame(rows)

    result.to_csv(
        TABLE_DIR
        / "pairwise_statistics.csv",
        index=False,
    )

    return result


def figure_outcome_distribution(
    outcome_table: pd.DataFrame,
) -> None:
    labels = [
        "Bug detecting",
        "Oracle error",
        "Execution timeout",
        "Invalid syntax",
    ]

    categories = [
        "bug_detecting",
        "oracle_error",
        "execution_timeout",
        "invalid_syntax",
    ]

    fig, ax = plt.subplots(
        figsize=(8, 5)
    )

    bottom = np.zeros(
        len(CONDITIONS)
    )

    for category, label in zip(
        categories,
        labels,
    ):
        values = []

        for condition in CONDITIONS:
            match = outcome_table[
                (
                    outcome_table[
                        "condition"
                    ]
                    == condition
                )
                &
                (
                    outcome_table[
                        "outcome"
                    ]
                    == category
                )
            ]

            value = (
                float(
                    match[
                        "percent"
                    ].iloc[0]
                )
                if len(match)
                else 0.0
            )

            values.append(value)

        ax.bar(
            CONDITIONS,
            values,
            bottom=bottom,
            label=label,
        )

        bottom += np.array(
            values
        )

    ax.set_ylabel(
        "Generated test suites (%)"
    )

    ax.set_ylim(
        0,
        100,
    )

    ax.legend(
        loc="upper right"
    )

    fig.tight_layout()

    fig.savefig(
        FIGURE_DIR
        / "fig_outcome_distribution.png",
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)


def figure_detection_heatmap(
    matrix: pd.DataFrame,
) -> None:
    data = matrix[
        CONDITIONS
    ].values

    fig_height = max(
        5,
        len(matrix)
        * 0.48,
    )

    fig, ax = plt.subplots(
        figsize=(
            6,
            fig_height,
        )
    )

    image = ax.imshow(
        data,
        aspect="auto",
        vmin=0,
        vmax=3,
    )

    ax.set_xticks(
        range(
            len(CONDITIONS)
        ),
        CONDITIONS,
    )

    ax.set_yticks(
        range(
            len(matrix.index)
        ),
        matrix.index,
    )

    for i in range(
        data.shape[0]
    ):
        for j in range(
            data.shape[1]
        ):
            value = int(data[i, j])
            text_color = (
                "white"
                if value <= 1
                else "black"
            )

            ax.text(
                j,
                i,
                f"{value}/3",
                ha="center",
                va="center",
                color=text_color,
                fontweight="bold",
            )

    colorbar = fig.colorbar(
        image,
        ax=ax,
    )

    colorbar.set_label(
        "Detections out of 3"
    )

    fig.tight_layout()

    fig.savefig(
        FIGURE_DIR
        / "fig_detection_heatmap.png",
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)


def figure_cumulative_detection(
    cumulative: pd.DataFrame,
) -> None:
    fig, ax = plt.subplots(
        figsize=(7, 4.5)
    )

    x_offsets = {
        "CODE": 0.0,
        "SPEC": -0.04,
        "BOTH": 0.04,
    }

    markers = {
        "CODE": "o",
        "SPEC": "s",
        "BOTH": "^",
    }

    line_styles = {
        "CODE": "-",
        "SPEC": "--",
        "BOTH": ":",
    }

    for condition in CONDITIONS:
        data = (
            cumulative[
                cumulative[
                    "condition"
                ]
                == condition
            ]
            .sort_values(
                "generation_budget"
            )
        )

        x_values = (
            data[
                "generation_budget"
            ]
            .astype(float)
            .to_numpy()
            + x_offsets[condition]
        )

        ax.plot(
            x_values,
            data[
                "observed_programs_detected"
            ],
            marker=markers[condition],
            linestyle=line_styles[condition],
            linewidth=1.6,
            markersize=5,
            label=condition,
        )

    ax.set_xticks(
        [
            1,
            2,
            3,
        ]
    )

    ax.set_ylim(
        0,
        11,
    )

    ax.set_xlim(
        0.85,
        3.15,
    )

    ax.set_xlabel(
        "Number of generations per program"
    )

    ax.set_ylabel(
        "Known bugs detected (out of 11)"
    )

    ax.legend()

    fig.tight_layout()

    fig.savefig(
        FIGURE_DIR
        / "fig_cumulative_detection.png",
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)


def condition_boxplot(
    master: pd.DataFrame,
    column: str,
    filename: str,
    ylabel: str,
    title: str,
    oracle_only: bool = False,
) -> None:
    data_source = (
        master[
            master["oracle_correct"]
        ]
        if oracle_only
        else master
    )

    data = []

    for condition in CONDITIONS:
        values = (
            data_source[
                data_source[
                    "condition"
                ]
                == condition
            ][column]
            .dropna()
            .astype(float)
            .values
        )

        data.append(values)

    fig, ax = plt.subplots(
        figsize=(6.5, 4.5)
    )

    ax.boxplot(
        data,
        tick_labels=CONDITIONS,
        showmeans=True,
    )

    ax.set_ylabel(
        ylabel
    )

    ax.set_title(
        title
    )

    fig.tight_layout()

    fig.savefig(
        FIGURE_DIR
        / filename,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)


def figure_detection_stability(
    stability: pd.DataFrame,
) -> None:
    fig, ax = plt.subplots(
        figsize=(7, 4.5)
    )

    bottom = np.zeros(
        len(CONDITIONS)
    )

    for count in range(4):
        column = (
            f"detected_{count}_of_3"
        )

        values = (
            stability
            .set_index(
                "condition"
            )
            .loc[
                CONDITIONS,
                column,
            ]
            .values
        )

        ax.bar(
            CONDITIONS,
            values,
            bottom=bottom,
            label=f"{count}/3",
        )

        bottom += values

    ax.set_ylabel(
        "Programs"
    )

    ax.set_ylim(
        0,
        11,
    )

    ax.set_title(
        "Detection consistency across generations"
    )

    ax.legend(
        title="Detections"
    )

    fig.tight_layout()

    fig.savefig(
        FIGURE_DIR
        / "fig_detection_stability.png",
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)


def figure_oracle_error_rate(
    condition_summary: pd.DataFrame,
) -> None:
    data = (
        condition_summary
        .set_index(
            "condition"
        )
        .loc[
            CONDITIONS
        ]
    )

    fig, ax = plt.subplots(
        figsize=(6.5, 4.5)
    )

    bars = ax.bar(
        CONDITIONS,
        data[
            "oracle_error_pct"
        ],
    )

    ax.set_ylabel(
        "Oracle-error suites (%)"
    )

    ax.set_ylim(
        0,
        100,
    )

    ax.set_title(
        "Oracle error rate by prompt condition"
    )

    for bar, value in zip(
        bars,
        data[
            "oracle_error_pct"
        ],
    ):
        ax.text(
            bar.get_x()
            + bar.get_width()
            / 2,
            bar.get_height()
            + 2,
            f"{value:.1f}%",
            ha="center",
        )

    fig.tight_layout()

    fig.savefig(
        FIGURE_DIR
        / "fig_oracle_error_rate.png",
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)


def figure_coverage_by_outcome(
    master: pd.DataFrame,
) -> None:
    categories = [
        "bug_detecting",
        "oracle_error",
    ]

    data = []

    labels = []

    for category in categories:
        values = (
            master[
                master[
                    "classification"
                ]
                == category
            ][
                "correct_branch_coverage_percent"
            ]
            .dropna()
            .astype(float)
            .values
        )

        if len(values):
            data.append(values)
            labels.append(
                category.replace(
                    "_",
                    " ",
                ).title()
            )

    if not data:
        return

    fig, ax = plt.subplots(
        figsize=(6.5, 4.5)
    )

    ax.boxplot(
        data,
        tick_labels=labels,
        showmeans=True,
    )

    ax.set_ylabel(
        "Branch coverage (%)"
    )

    fig.tight_layout()

    fig.savefig(
        FIGURE_DIR
        / "fig_branch_coverage_by_outcome.png",
        dpi=300,
        bbox_inches="tight",
    )

    plt.close(fig)


def create_figures(
    master: pd.DataFrame,
    condition_summary: pd.DataFrame,
    outcome_table: pd.DataFrame,
    matrix: pd.DataFrame,
    cumulative: pd.DataFrame,
    stability: pd.DataFrame,
) -> None:
    figure_outcome_distribution(
        outcome_table
    )

    figure_detection_heatmap(
        matrix
    )

    figure_cumulative_detection(
        cumulative
    )

    figure_detection_stability(
        stability
    )

    figure_oracle_error_rate(
        condition_summary
    )

    condition_boxplot(
        master=master,
        column=(
            "correct_branch_coverage_percent"
        ),
        filename=(
            "fig_branch_coverage_oracle_correct.png"
        ),
        ylabel="Branch coverage (%)",
        title=(
            "Branch coverage of oracle-correct suites"
        ),
        oracle_only=True,
    )

    condition_boxplot(
        master=master,
        column=(
            "correct_line_coverage_percent"
        ),
        filename=(
            "fig_line_coverage_oracle_correct.png"
        ),
        ylabel="Line coverage (%)",
        title=(
            "Line coverage of oracle-correct suites"
        ),
        oracle_only=True,
    )

    condition_boxplot(
        master=master,
        column="output_tokens",
        filename=(
            "fig_output_tokens.png"
        ),
        ylabel="Output tokens",
        title=(
            "Generated test-suite size in output tokens"
        ),
    )

    condition_boxplot(
        master=master,
        column="total_duration_seconds",
        filename=(
            "fig_generation_time.png"
        ),
        ylabel="Generation time (s)",
        title=(
            "LLM generation time by prompt condition"
        ),
    )

    condition_boxplot(
        master=master,
        column="test_function_count",
        filename=(
            "fig_test_function_count.png"
        ),
        ylabel="Test functions per suite",
        title=(
            "Generated test functions by condition"
        ),
    )

    figure_coverage_by_outcome(
        master
    )


def write_summary(
    master: pd.DataFrame,
    condition_summary: pd.DataFrame,
    stability: pd.DataFrame,
    cumulative: pd.DataFrame,
    condition_ci: pd.DataFrame,
    pair_ci: pd.DataFrame,
    pairwise: pd.DataFrame,
) -> None:
    lines = []

    lines.append(
        "AI-GENERATED TESTS: PAPER RESULTS SUMMARY"
    )

    lines.append(
        "=" * 72
    )

    lines.append("")

    lines.append(
        f"Total generated suites: {len(master)}"
    )

    lines.append(
        f"Programs: {master['program'].nunique()}"
    )

    lines.append(
        f"Conditions: {', '.join(CONDITIONS)}"
    )

    lines.append(
        "Generations per program/condition: 3"
    )

    lines.append("")

    lines.append(
        "OVERALL OUTCOMES"
    )

    lines.append(
        "-" * 72
    )

    lines.append(
        f"Syntax valid: "
        f"{int(master['syntax_valid'].sum())}"
        f"/{len(master)} "
        f"({percent(master['syntax_valid'].sum(), len(master)):.2f}%)"
    )

    lines.append(
        f"Executable on correct implementation: "
        f"{int(master['correct_executable'].sum())}"
        f"/{len(master)} "
        f"({percent(master['correct_executable'].sum(), len(master)):.2f}%)"
    )

    lines.append(
        f"Oracle correct: "
        f"{int(master['oracle_correct'].sum())}"
        f"/{len(master)} "
        f"({percent(master['oracle_correct'].sum(), len(master)):.2f}%)"
    )

    lines.append(
        f"Bug detecting: "
        f"{int(master['bug_detected'].sum())}"
        f"/{len(master)} "
        f"({percent(master['bug_detected'].sum(), len(master)):.2f}%)"
    )

    lines.append(
        f"Oracle errors: "
        f"{int((master['classification'] == 'oracle_error').sum())}"
    )

    lines.append(
        f"Correct-execution timeouts: "
        f"{int(master['correct_timeout'].sum())}"
    )

    lines.append(
        f"Invalid syntax: "
        f"{int((~master['syntax_valid']).sum())}"
    )

    lines.append("")

    lines.append(
        "BY CONDITION"
    )

    lines.append(
        "-" * 72
    )

    for _, row in (
        condition_summary.iterrows()
    ):
        lines.append(
            (
                f"{row['condition']}: "
                f"bug-detecting "
                f"{int(row['bug_detecting_n'])}/"
                f"{int(row['suites'])} "
                f"({row['bug_detecting_pct']:.2f}%), "
                f"oracle-correct "
                f"{int(row['oracle_correct_n'])}/"
                f"{int(row['suites'])} "
                f"({row['oracle_correct_pct']:.2f}%), "
                f"unique bugs "
                f"{int(row['unique_bugs_detected_n'])}/"
                f"{master['program'].nunique()} "
                f"({row['unique_bugs_detected_pct']:.2f}%)"
            )
        )

    lines.append("")

    lines.append(
        "DETECTION CONSISTENCY"
    )

    lines.append(
        "-" * 72
    )

    for _, row in (
        stability.iterrows()
    ):
        lines.append(
            (
                f"{row['condition']}: "
                f"0/3={int(row['detected_0_of_3'])}, "
                f"1/3={int(row['detected_1_of_3'])}, "
                f"2/3={int(row['detected_2_of_3'])}, "
                f"3/3={int(row['detected_3_of_3'])}"
            )
        )

    lines.append("")

    lines.append(
        "CUMULATIVE DETECTION"
    )

    lines.append(
        "-" * 72
    )

    for condition in CONDITIONS:
        data = cumulative[
            cumulative[
                "condition"
            ]
            == condition
        ]

        values = []

        for _, row in data.iterrows():
            values.append(
                (
                    f"{int(row['generation_budget'])} gen: "
                    f"{int(row['observed_programs_detected'])}/11"
                )
            )

        lines.append(
            f"{condition}: "
            + ", ".join(values)
        )

    lines.append("")

    lines.append(
        "CLUSTER BOOTSTRAP 95% INTERVALS"
    )

    lines.append(
        "-" * 72
    )

    for _, row in (
        condition_ci.iterrows()
    ):
        lines.append(
            (
                f"{row['condition']}: "
                f"suite detection "
                f"{row['suite_detection_rate']:.2f}% "
                f"[{row['suite_detection_ci_low']:.2f}, "
                f"{row['suite_detection_ci_high']:.2f}], "
                f"unique-bug detection "
                f"{row['unique_bug_detection_rate']:.2f}% "
                f"[{row['unique_bug_detection_ci_low']:.2f}, "
                f"{row['unique_bug_detection_ci_high']:.2f}]"
            )
        )

    lines.append("")

    lines.append(
        "PAIRWISE BOOTSTRAP DIFFERENCES"
    )

    lines.append(
        "-" * 72
    )

    for _, row in (
        pair_ci.iterrows()
    ):
        lines.append(
            (
                f"{row['comparison']}: "
                f"{row['difference_percentage_points']:+.2f} pp "
                f"[{row['bootstrap_ci_low']:+.2f}, "
                f"{row['bootstrap_ci_high']:+.2f}]"
            )
        )

    lines.append("")

    lines.append(
        "PROGRAM-LEVEL EXACT McNEMAR TEST"
    )

    lines.append(
        "-" * 72
    )

    for _, row in (
        pairwise.iterrows()
    ):
        lines.append(
            (
                f"{row['comparison']}: "
                f"discordant={int(row['discordant_pairs'])}, "
                f"p={row['exact_mcnemar_p']:.6f}"
            )
        )

    lines.append("")

    lines.append(
        "NOTE"
    )

    lines.append(
        "-" * 72
    )

    lines.append(
        (
            "Bootstrap intervals resample programs rather than treating "
            "the three generations for the same program as independent."
        )
    )

    lines.append(
        (
            "McNemar comparisons use program-level detection: a program "
            "is considered detected when at least one of its three "
            "generations exposes the known bug."
        )
    )

    SUMMARY_FILE.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def print_key_results(
    condition_summary: pd.DataFrame,
    pair_ci: pd.DataFrame,
) -> None:
    print()
    print("=" * 76)
    print("KEY RESULTS")
    print("=" * 76)

    print()

    print(
        f"{'Condition':<10}"
        f"{'Detection':>15}"
        f"{'Oracle':>15}"
        f"{'Unique bugs':>18}"
    )

    for _, row in (
        condition_summary.iterrows()
    ):
        print(
            f"{row['condition']:<10}"
            f"{int(row['bug_detecting_n']):>5}/"
            f"{int(row['suites']):<4}"
            f"{row['bug_detecting_pct']:>6.2f}%"
            f"{int(row['oracle_correct_n']):>5}/"
            f"{int(row['suites']):<4}"
            f"{row['oracle_correct_pct']:>6.2f}%"
            f"{int(row['unique_bugs_detected_n']):>7}/11"
            f"{row['unique_bugs_detected_pct']:>7.2f}%"
        )

    print()
    print(
        "Pairwise suite-detection differences:"
    )

    for _, row in (
        pair_ci.iterrows()
    ):
        print(
            f"  {row['comparison']:<14} "
            f"{row['difference_percentage_points']:+.2f} pp "
            f"95% CI "
            f"[{row['bootstrap_ci_low']:+.2f}, "
            f"{row['bootstrap_ci_high']:+.2f}]"
        )

    print()
    print(
        f"Master dataset: {MASTER_FILE}"
    )

    print(
        f"Tables: {TABLE_DIR}"
    )

    print(
        f"Figures: {FIGURE_DIR}"
    )

    print(
        f"Summary: {SUMMARY_FILE}"
    )


def main() -> None:
    ensure_directories()

    (
        generation,
        validation,
        evaluation,
        per_test,
    ) = load_data()

    master = prepare_master(
        generation,
        validation,
        evaluation,
    )

    condition_summary = (
        create_condition_summary(
            master
        )
    )

    outcome_table = (
        create_outcome_table(
            master
        )
    )

    (
        program_results,
        detection_matrix,
    ) = create_program_results(
        master
    )

    stability = (
        create_stability_results(
            program_results
        )
    )

    cumulative = (
        create_cumulative_detection(
            master
        )
    )

    create_coverage_summary(
        master
    )

    create_structure_summary(
        master
    )

    create_generation_summary(
        master
    )

    (
        paired_tests,
        per_test_summary,
    ) = create_per_test_analysis(
        per_test,
        master,
    )

    create_filtered_detection(
        paired_tests,
        master,
    )

    (
        condition_ci,
        pair_ci,
    ) = cluster_bootstrap(
        program_results
    )

    pairwise = (
        create_pairwise_statistics(
            program_results
        )
    )

    create_figures(
        master=master,
        condition_summary=(
            condition_summary
        ),
        outcome_table=(
            outcome_table
        ),
        matrix=(
            detection_matrix
        ),
        cumulative=(
            cumulative
        ),
        stability=(
            stability
        ),
    )

    write_summary(
        master=master,
        condition_summary=(
            condition_summary
        ),
        stability=stability,
        cumulative=cumulative,
        condition_ci=(
            condition_ci
        ),
        pair_ci=pair_ci,
        pairwise=pairwise,
    )

    print_key_results(
        condition_summary,
        pair_ci,
    )


if __name__ == "__main__":
    main()
