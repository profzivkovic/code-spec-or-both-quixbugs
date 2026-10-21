# Reproducibility

## 1. Experimental design

The study compares three prompt conditions for LLM-generated pytest suites:

- **CODE** = common generation instruction + cleaned buggy implementation.
- **SPEC** = common generation instruction + function signature + benchmark specification.
- **BOTH** = common generation instruction + cleaned buggy implementation + benchmark specification.

For CODE, the QuixBugs docstring/specification was removed, including natural-language description, preconditions, and worked examples. SPEC and BOTH contain the original benchmark specification, including examples when present.

The correct implementation was never included in a model prompt.

Eleven programs, three conditions, and three fixed seeds produced 99 generated suites.

## 2. Generation configuration

- Ollama model tag: `qwen2.5-coder:7b`
- quantization: `Q4_K_M`
- configured context window: `8192`
- output limit: `4096`
- temperature: `0.7`
- seeds: `101`, `202`, `303`
- structured response: JSON schema containing generated Python code

The raw model responses and generation metadata are committed under `results/raw/`.

## 3. Evaluation definitions

### Syntax validity

A generated suite must parse as valid Python.

### Executability

A syntactically valid suite is executed with pytest against the correct implementation with a 20 s timeout.

### Oracle correctness

A suite is **oracle-correct** only if all its tests pass on the correct implementation.

### Strict bug detection

A strict detection occurs when an oracle-correct suite fails on the corresponding buggy implementation.

### Filtered bug detection

For the secondary filtered analysis, individual tests that fail on the correct implementation are discarded. A suite is counted as detecting when at least one remaining test fails or errors on the buggy implementation.

### Per-test analysis

Correct and buggy test outcomes are aligned using:

- `run_id`
- test class
- test name

An individual test is oracle-correct when it passes on the correct implementation. An oracle-correct individual test is bug-revealing when it fails or errors on the buggy implementation.

## 4. Reproduce the final analysis

The committed raw and intermediate data are sufficient to reproduce the paper-level analysis without generating new LLM responses.

### Windows PowerShell

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python scripts\analyze_results.py
```

### Linux/macOS

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python scripts/analyze_results.py
```

The final analysis reads:

- `results/raw/generation_metadata.csv`
- `results/preparation/generated_test_validation.csv`
- `results/raw/evaluation_results.csv`
- `results/raw/per_test_results.csv`

and writes derived results to:

- `results/paper/master_results.csv`
- `results/paper/tables/`
- `results/paper/figures/`
- `results/paper/paper_results_summary.txt`

## 5. Expected headline results

Strict suite-level detection:

- CODE: 9/33 (27.27%), 4/11 distinct bugs
- SPEC: 18/33 (54.55%), 8/11 distinct bugs
- BOTH: 16/33 (48.48%), 8/11 distinct bugs

Filtered suite-level detection:

- CODE: 23/33 (69.70%), 9/11 distinct bugs
- SPEC: 30/33 (90.91%), 11/11 distinct bugs
- BOTH: 31/33 (93.94%), 11/11 distinct bugs

The program-cluster bootstrap difference for strict SPEC minus CODE detection is +27.27 percentage points with a 95% CI of [-6.06, +54.55].

## 6. Repeating the full experiment

The repository also contains the scripts used for preparation, prompt creation, generation, validation, and evaluation.

Logical order:

1. `scripts/prepare_quixbugs.py`
2. `scripts/extract_tasks.py`
3. `scripts/build_prompts.py`
4. `scripts/validate_prompts.py`
5. `scripts/generate_tests.py`
6. `scripts/validate_generated_tests.py`
7. `scripts/evaluate_tests.py`
8. `scripts/analyze_results.py`

A full re-run additionally requires Ollama and the `qwen2.5-coder:7b` model.

Because LLM runtime behavior can depend on model runtime versions and hardware, the committed prompts, raw responses, generated suites, and evaluation files are the archival record of the experiment reported in the manuscript.

## 7. Environment information

Experiment-environment metadata captured during the study are retained under:

- `results/preparation/environment.txt`
- `results/preparation/experiment_environment.json`

The pinned `requirements.txt` records the Python package versions verified to reproduce the final analysis in a clean Python 3.11 virtual environment.
