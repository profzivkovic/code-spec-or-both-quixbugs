# v1.0.1

Archival update for the reproducibility artifact accompanying:

**Code, Specification, or Both? Evaluating LLM-Generated Unit Tests on QuixBugs**

This release removes redundant execution logs, JUnit XML files, individual
coverage JSON files, and unused Java benchmark material in order to reduce the
archive file count.

The reproducibility-critical artifacts are retained:

- exact CODE, SPEC, and BOTH prompts;
- all 99 generated pytest suites;
- raw Ollama responses and generation metadata;
- task preparation and validation artifacts;
- evaluation and per-test result datasets;
- the final analysis script and derived tables/figures;
- the QuixBugs Python benchmark material used by the experiment.

The final analysis was rerun after cleanup and reproduces the reported strict
and filtered detection results exactly.
