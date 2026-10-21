# Code, Specification, or Both?

Research artifact accompanying the TELFOR 2026 manuscript:

**Code, Specification, or Both? Evaluating LLM-Generated Unit Tests on QuixBugs**

**Authors:** Tamara Zivkovic and Miodrag Zivkovic  
**Affiliation:** Faculty of Informatics and Computing, Singidunum University, Belgrade, Serbia

## Overview

This repository contains the complete experimental artifact for a controlled comparison of three prompt-context conditions for LLM-generated Python unit tests:

- **CODE** — the buggy implementation only, with the QuixBugs docstring/specification removed.
- **SPEC** — the function signature plus the original QuixBugs natural-language specification.
- **BOTH** — the same cleaned buggy implementation together with the same specification.

The correct implementation was never shown to the model and was used only as an evaluation oracle.

The final experiment contains **99 generated pytest suites**: 11 QuixBugs programs × 3 prompt conditions × 3 fixed seeds.

The 11 programs are:

`gcd`, `get_factors`, `is_valid_parenthesization`, `max_sublist_sum`, `mergesort`, `next_palindrome`, `next_permutation`, `powerset`, `quicksort`, `sieve`, and `to_base`.

A twelfth candidate, `sqrt`, was removed during pre-validation because the benchmark reference tests did not distinguish its buggy and correct implementations.

## Model and generation configuration

Generation was performed locally through Ollama using:

- model tag: `qwen2.5-coder:7b`
- quantization: `Q4_K_M`
- configured context window: `8192` tokens
- maximum generated output: `4096` tokens
- temperature: `0.7`
- seeds: `101`, `202`, `303`
- structured output: JSON schema containing the generated Python test code

No generated suite was manually corrected.

## Repository structure

```text
external/QuixBugs/          Vendored QuixBugs benchmark snapshot
generated_tests/            All 99 generated pytest suites
prompts/                    Exact prompts for CODE, SPEC, and BOTH
results/
  preparation/              Task extraction and pre-validation artifacts
  raw/                      Raw model responses and evaluation outputs
  paper/                    Derived tables, figures, and result summaries
scripts/                    Preparation, generation, evaluation, and analysis code
requirements.txt            Pinned Python dependencies for analysis/evaluation
REPRODUCIBILITY.md          Metric definitions and reproduction workflow
THIRD_PARTY.md              QuixBugs attribution and licensing notice
CITATION.cff                Citation metadata
.zenodo.json                Zenodo release metadata
```

## Key results

### Strict suite-level criterion

A generated suite is oracle-correct only if all its tests pass on the correct implementation. A strict detection occurs when such a suite fails on the buggy implementation.

| Condition | Strict detection | Distinct bugs |
|---|---:|---:|
| CODE | 9/33 (27.27%) | 4/11 |
| SPEC | 18/33 (54.55%) | 8/11 |
| BOTH | 16/33 (48.48%) | 8/11 |

### Filtered criterion

Individual tests that fail on the correct implementation are discarded. A suite is counted as detecting if at least one remaining test fails or errors on the buggy implementation.

| Condition | Filtered detection | Distinct bugs |
|---|---:|---:|
| CODE | 23/33 (69.70%) | 9/11 |
| SPEC | 30/33 (90.91%) | 11/11 |
| BOTH | 31/33 (93.94%) | 11/11 |

## Reproducing the paper analysis

A clean Python 3.11 environment is recommended.

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python scripts\analyze_results.py
```

Linux/macOS:

```bash
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python scripts/analyze_results.py
```

The analysis reads the committed experimental data and regenerates the paper-level tables and figures under `results/paper/`.

The expected headline output includes:

```text
FILTERED SUITE-LEVEL DETECTION
CODE: strict 9/33 (27.27%), filtered 23/33 (69.70%), unique bugs 9/11
SPEC: strict 18/33 (54.55%), filtered 30/33 (90.91%), unique bugs 11/11
BOTH: strict 16/33 (48.48%), filtered 31/33 (93.94%), unique bugs 11/11
```

See `REPRODUCIBILITY.md` for the complete workflow and metric definitions.

## Full experimental artifacts

The repository retains:

- exact prompt text for every program and condition;
- all generated test suites;
- raw Ollama responses;
- generation metadata, including prompt hashes and token counts;
- syntax and structural validation outputs;
- correct- and buggy-version execution results;
- per-test outcomes;
- coverage output;
- derived paper tables and figures.

Local absolute filesystem paths in public runtime artifacts may be replaced by neutral placeholders. This sanitization does not change generated tests, experimental outcomes, or reported metrics.

## Third-party material

QuixBugs is vendored under `external/QuixBugs/` for reproducibility. Its original license and legal notes are preserved. The upstream project is:

https://github.com/jkoppel/QuixBugs

See `THIRD_PARTY.md`.

## License

Original code and research-artifact material authored for this study are released under the MIT License; see `LICENSE`.

Vendored third-party material remains under its original terms.

## Citation

Citation metadata are provided in `CITATION.cff`.

After the GitHub release is archived by Zenodo, the resulting DOI should be added here and to the manuscript.
