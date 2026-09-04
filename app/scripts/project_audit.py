from __future__ import annotations

import platform
import subprocess
import sys
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
AUDIT_DIR = PROJECT_ROOT / "docs" / "project_audit"
AUDIT_FILE = AUDIT_DIR / "PROJECT_AUDIT.md"

IGNORED_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
}


def run_command(command: list[str]) -> str:
    """Executa um comando e devolve sua saída."""
    try:
        result = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

        output = result.stdout.strip()

        if not output:
            output = result.stderr.strip()

        return output or "Sem saída."

    except Exception as exc:
        return f"Erro ao executar comando: {exc}"


def get_project_tree() -> str:
    """Gera uma árvore simples da estrutura atual do projeto."""
    lines: list[str] = []

    for path in sorted(PROJECT_ROOT.rglob("*")):
        relative = path.relative_to(PROJECT_ROOT)

        if any(part in IGNORED_DIRS for part in relative.parts):
            continue

        # Evita que o próprio artefato de audit apareça na árvore.
        if path == AUDIT_FILE:
            continue

        depth = len(relative.parts) - 1
        prefix = "    " * depth

        if path.is_dir():
            lines.append(f"{prefix}[DIR] {path.name}/")
        else:
            lines.append(f"{prefix}[FILE] {path.name}")

    return "\n".join(lines)


def get_python_metrics() -> dict[str, int]:
    """Calcula métricas simples dos arquivos Python do projeto."""
    python_files = [
        path
        for path in PROJECT_ROOT.rglob("*.py")
        if not any(part in IGNORED_DIRS for part in path.parts)
    ]

    total_lines = 0
    effective_lines = 0
    functions = 0
    classes = 0

    for path in python_files:
        content = path.read_text(encoding="utf-8")
        lines = content.splitlines()

        total_lines += len(lines)

        effective_lines += sum(
            1
            for line in lines
            if line.strip() and not line.strip().startswith("#")
        )

        functions += sum(
            1
            for line in lines
            if line.lstrip().startswith(("def ", "async def "))
        )

        classes += sum(
            1
            for line in lines
            if line.lstrip().startswith("class ")
        )

    return {
        "python_files": len(python_files),
        "total_lines": total_lines,
        "effective_lines": effective_lines,
        "functions": functions,
        "classes": classes,
    }


def get_git_info() -> str:
    """Obtém informações básicas do repositório Git."""
    branch = run_command(["git", "branch", "--show-current"])
    commit = run_command(["git", "rev-parse", "--short", "HEAD"])
    status = run_command(["git", "status", "--short"])

    if status == "Sem saída.":
        status = "Working tree clean."

    return (
        f"- Branch: {branch}\n"
        f"- Commit: {commit}\n"
        f"- Status: {status}"
    )


def get_tests() -> str:
    """Executa pytest e captura o resultado."""
    return run_command([sys.executable, "-m", "pytest", "-q"])


def get_dependencies() -> str:
    """Lista as dependências instaladas no ambiente atual."""
    return run_command([sys.executable, "-m", "pip", "freeze"])


def build_audit() -> str:
    """Monta o documento Markdown da auditoria."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    metrics = get_python_metrics()

    return f"""# PROJECT AUDIT — LinkedIn Agent System

Generated: {timestamp}

## Environment

- Python: {platform.python_version()}
- Executable: {sys.executable}
- Platform: {platform.platform()}

## Code Metrics

- Python files: {metrics["python_files"]}
- Total lines: {metrics["total_lines"]}
- Effective lines: {metrics["effective_lines"]}
- Functions: {metrics["functions"]}
- Classes: {metrics["classes"]}

## Project Structure

```text
{get_project_tree()}
```

## Tests

```text
{get_tests()}
```

## Git

{get_git_info()}

## Dependencies

```text
{get_dependencies()}
```

## Development Context

This audit is an automated snapshot of the current technical
state of the LinkedIn Agent System project.

It is intended to support development continuity, technical
review, debugging, and context recovery between development sessions.
"""


def main() -> None:
    """Gera e sobrescreve a auditoria atual do projeto."""
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)

    audit = build_audit()
    AUDIT_FILE.write_text(audit, encoding="utf-8")

    print("Audit generated successfully:")
    print(AUDIT_FILE)


if __name__ == "__main__":
    main()