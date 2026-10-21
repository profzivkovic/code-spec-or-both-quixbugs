from __future__ import annotations

import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

OUTPUT_FILE = (
    PROJECT_ROOT
    / "results"
    / "preparation"
    / "experiment_environment.json"
)

MODEL = "qwen2.5-coder:7b"


def run(command: list[str]) -> str:
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )

    output = (
        result.stdout.strip()
        or result.stderr.strip()
    )

    return output


def main() -> None:
    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    data = {
        "captured_at_utc": datetime.now(
            timezone.utc
        ).isoformat(),

        "model": MODEL,

        "ollama_version": run(
            ["ollama", "--version"]
        ),

        "ollama_list": run(
            ["ollama", "list"]
        ),

        "ollama_show": run(
            ["ollama", "show", MODEL]
        ),

        "python_executable": sys.executable,

        "python_version": sys.version,

        "platform": platform.platform(),

        "processor": platform.processor(),

        "pip_freeze": run(
            [
                sys.executable,
                "-m",
                "pip",
                "freeze",
            ]
        ),

        "nvidia_smi": run(
            ["nvidia-smi"]
        ),
    }

    OUTPUT_FILE.write_text(
        json.dumps(
            data,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(
        f"Environment saved to:\n{OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()