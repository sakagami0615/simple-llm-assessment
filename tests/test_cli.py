from pathlib import Path

from local_llm_eval.cli import main


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def create_files(root: Path) -> Path:
    write(
        root / "config" / "models" / "ollama.yaml",
        """
id: ollama-llama3
provider: openai_compatible
base_url: http://localhost:11434/v1
model: llama3.1:8b
generation: {}
""",
    )
    write(
        root / "config" / "benchmarks" / "mmlu.yaml",
        """
id: mmlu
runner: lm-evaluation-harness
task: mmlu
metrics:
  - acc
""",
    )
    suite = root / "config" / "suites" / "baseline.yaml"
    write(
        suite,
        """
id: baseline
models:
  - models/ollama.yaml
benchmarks:
  - benchmarks/mmlu.yaml
""",
    )
    return suite


def test_validate_command_returns_success(tmp_path: Path) -> None:
    suite = create_files(tmp_path)

    assert main(["validate", str(suite)]) == 0


def test_run_dry_run_returns_success(tmp_path: Path) -> None:
    suite = create_files(tmp_path)

    assert main(["run", str(suite), "--dry-run", "--runs-dir", str(tmp_path / "runs")]) == 0
    assert any((tmp_path / "runs").iterdir())
