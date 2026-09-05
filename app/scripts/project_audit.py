from __future__ import annotations

import hashlib
import platform
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

AUDIT_DIR = PROJECT_ROOT / "docs" / "project_audit"
AUDIT_FILE = AUDIT_DIR / "PROJECT_AUDIT.md"

CONTEXT_FILE = PROJECT_ROOT / "docs" / "context" / "PROJECT_CONTEXT.md"
REQUIREMENTS_FILE = PROJECT_ROOT / "requirements.txt"

IGNORED_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
}

FINGERPRINT_EXCLUDED_FILES = {
    AUDIT_FILE,
}


# ============================================================
# COMMAND EXECUTION
# ============================================================


def run_command(
    command: list[str],
    timeout: int = 120,
) -> str:
    """
    Executa um comando no diretório raiz do projeto e devolve
    stdout e stderr, preservando ambas as saídas.
    """
    try:
        result = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout,
        )

        stdout = result.stdout.strip()
        stderr = result.stderr.strip()

        parts: list[str] = []

        if stdout:
            parts.append(stdout)

        if stderr:
            parts.append(stderr)

        return "\n".join(parts) if parts else "Sem saída."

    except subprocess.TimeoutExpired:
        return (
            "Erro: comando excedeu o tempo limite "
            f"de {timeout} segundos."
        )

    except Exception as exc:
        return f"Erro ao executar comando: {exc}"


# ============================================================
# PROJECT STRUCTURE
# ============================================================


def is_ignored(path: Path) -> bool:
    """Informa se um caminho deve ser ignorado pela auditoria."""
    try:
        relative = path.relative_to(PROJECT_ROOT)
    except ValueError:
        return True

    return any(part in IGNORED_DIRS for part in relative.parts)


def get_project_tree() -> str:
    """Gera uma árvore simples da estrutura atual do projeto."""
    lines: list[str] = []

    for path in sorted(PROJECT_ROOT.rglob("*")):
        if is_ignored(path):
            continue

        if path == AUDIT_FILE:
            continue

        relative = path.relative_to(PROJECT_ROOT)
        depth = len(relative.parts) - 1
        prefix = "    " * depth

        if path.is_dir():
            lines.append(f"{prefix}[DIR] {path.name}/")
        else:
            lines.append(f"{prefix}[FILE] {path.name}")

    return "\n".join(lines)


# ============================================================
# PYTHON METRICS
# ============================================================


def get_python_files() -> list[Path]:
    """Retorna todos os arquivos Python relevantes do projeto."""
    return [
        path
        for path in PROJECT_ROOT.rglob("*.py")
        if not is_ignored(path)
    ]


def get_python_metrics() -> dict[str, int]:
    """
    Calcula métricas simples dos arquivos Python.

    AST permanece fora do escopo da v1.6.
    """
    python_files = get_python_files()

    total_lines = 0
    effective_lines = 0
    functions = 0
    classes = 0

    for path in python_files:
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

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


# ============================================================
# GIT
# ============================================================


def get_git_branch() -> str:
    """Retorna a branch Git atual."""
    return run_command(["git", "branch", "--show-current"])


def get_git_commit() -> str:
    """Retorna o hash curto do HEAD atual."""
    return run_command(["git", "rev-parse", "--short", "HEAD"])


def get_git_status() -> str:
    """Retorna o estado resumido do working tree."""
    status = run_command(["git", "status", "--short"])

    if status == "Sem saída.":
        return "Working tree clean."

    return status


def get_git_info() -> str:
    """Obtém informações centrais do repositório Git."""
    branch = get_git_branch()
    commit = get_git_commit()
    status = get_git_status()

    return (
        f"- Branch: {branch}\n"
        f"- Commit: {commit}\n"
        f"- Status: {status}"
    )


def get_recent_commits(limit: int = 10) -> str:
    """Lista os commits mais recentes."""
    return run_command(
        [
            "git",
            "log",
            f"-{limit}",
            "--date=iso",
            "--pretty=format:%h | %ad | %s",
        ]
    )


def get_working_tree_summary() -> str:
    """Resume trabalho modificado, staged e untracked."""
    status = run_command(["git", "status", "--short"])

    if status == "Sem saída.":
        return (
            "State: CLEAN\n\n"
            "No modified, staged, or untracked files."
        )

    unstaged_stat = run_command(["git", "diff", "--stat"])
    staged_stat = run_command(["git", "diff", "--cached", "--stat"])

    parts = [
        "State: DIRTY",
        "",
        "Files:",
        status,
    ]

    if unstaged_stat != "Sem saída.":
        parts.extend(["", "Unstaged diff:", unstaged_stat])

    if staged_stat != "Sem saída.":
        parts.extend(["", "Staged diff:", staged_stat])

    return "\n".join(parts)


# ============================================================
# SNAPSHOT FINGERPRINT / INTEGRITY
# ============================================================


def get_fingerprint_files() -> list[Path]:
    """
    Retorna arquivos usados no fingerprint real do projeto.

    O artefato gerado pelo próprio audit é excluído para evitar
    que a geração do snapshot invalide o próprio snapshot.
    """
    files: list[Path] = []

    for path in PROJECT_ROOT.rglob("*"):
        if not path.is_file():
            continue

        if is_ignored(path):
            continue

        if path in FINGERPRINT_EXCLUDED_FILES:
            continue

        files.append(path)

    return sorted(
        files,
        key=lambda item: item.relative_to(PROJECT_ROOT).as_posix(),
    )


def get_project_fingerprint() -> str:
    """
    Calcula SHA-256 determinístico considerando caminho relativo
    e conteúdo de todos os arquivos relevantes do projeto.
    """
    digest = hashlib.sha256()

    for path in get_fingerprint_files():
        relative = path.relative_to(PROJECT_ROOT).as_posix()

        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")

        try:
            digest.update(path.read_bytes())
        except OSError as exc:
            digest.update(
                f"<READ_ERROR:{type(exc).__name__}:{exc}>".encode("utf-8")
            )

        digest.update(b"\0")

    return digest.hexdigest()


def get_snapshot_signature() -> dict[str, str]:
    """
    Captura HEAD, Git status e fingerprint real de conteúdo.
    """
    return {
        "head": get_git_commit(),
        "status": get_git_status(),
        "fingerprint": get_project_fingerprint(),
    }


def evaluate_snapshot_integrity(
    before: dict[str, str],
    after: dict[str, str],
) -> str:
    """
    Verifica se HEAD, status ou conteúdo mudaram durante a coleta.
    """
    same_head = before["head"] == after["head"]
    same_status = before["status"] == after["status"]
    same_fingerprint = (
        before["fingerprint"] == after["fingerprint"]
    )

    if same_head and same_status and same_fingerprint:
        return (
            "PASS\n\n"
            f"- HEAD before: {before['head']}\n"
            f"- HEAD after: {after['head']}\n"
            f"- Fingerprint before: {before['fingerprint']}\n"
            f"- Fingerprint after: {after['fingerprint']}\n"
            "- Repository content remained stable during "
            "audit collection."
        )

    changes: list[str] = []

    if not same_head:
        changes.append("- HEAD changed during audit collection.")

    if not same_status:
        changes.append("- Git status changed during audit collection.")

    if not same_fingerprint:
        changes.append(
            "- File content fingerprint changed during audit collection."
        )

    return (
        "WARNING\n\n"
        f"- HEAD before: {before['head']}\n"
        f"- HEAD after: {after['head']}\n"
        f"- Fingerprint before: {before['fingerprint']}\n"
        f"- Fingerprint after: {after['fingerprint']}\n"
        + "\n".join(changes)
        + "\n\nStatus before:\n"
        + before["status"]
        + "\n\nStatus after:\n"
        + after["status"]
    )


# ============================================================
# TESTS
# ============================================================


def get_tests() -> str:
    """Executa a suíte de testes."""
    return run_command(
        [sys.executable, "-m", "pytest", "-q"],
        timeout=180,
    )


def get_collected_tests() -> str:
    """
    Lista os testes descobertos. Os nomes funcionam como
    especificação comportamental de baixo custo.
    """
    return run_command(
        [
            sys.executable,
            "-m",
            "pytest",
            "--collect-only",
            "-q",
        ],
        timeout=180,
    )


def extract_passing_test_count(test_output: str) -> int | None:
    """Extrai a quantidade de testes aprovados do resumo do pytest."""
    match = re.search(r"(\d+)\s+passed\b", test_output)

    if match is None:
        return None

    return int(match.group(1))


# ============================================================
# DEPENDENCIES
# ============================================================


def get_declared_dependencies() -> str:
    """Lê requirements.txt."""
    if not REQUIREMENTS_FILE.exists():
        return "requirements.txt not found."

    content = REQUIREMENTS_FILE.read_text(encoding="utf-8").strip()
    return content or "requirements.txt is empty."


def get_installed_dependencies() -> str:
    """Lista dependências instaladas no ambiente atual."""
    return run_command([sys.executable, "-m", "pip", "freeze"])


# ============================================================
# HUMAN DEVELOPMENT CONTEXT
# ============================================================


def get_project_context() -> str:
    """Carrega o contexto humano do projeto."""
    if not CONTEXT_FILE.exists():
        return (
            "> PROJECT_CONTEXT.md not found.\n>\n"
            "> Create:\n"
            "> `docs/context/PROJECT_CONTEXT.md`\n>\n"
            "> Context recovery is incomplete until this file "
            "is available."
        )

    content = CONTEXT_FILE.read_text(encoding="utf-8").strip()

    if not content:
        return "> PROJECT_CONTEXT.md exists but is empty."

    return content


def get_context_section(
    context: str,
    heading: str,
) -> str | None:
    """
    Extrai o conteúdo de uma seção Markdown de nível 2.
    """
    pattern = re.compile(
        rf"^##\s+{re.escape(heading)}\s*$"
        rf"(.*?)(?=^##\s+|\Z)",
        re.MULTILINE | re.DOTALL,
    )

    match = pattern.search(context)

    if match is None:
        return None

    value = match.group(1).strip()
    return value or None


def extract_declared_baseline(context: str) -> str | None:
    """
    Extrai o primeiro hash Git curto/longo da seção
    Current Stable Baseline.
    """
    section = get_context_section(
        context,
        "Current Stable Baseline",
    )

    if section is None:
        return None

    match = re.search(r"\b[0-9a-fA-F]{7,40}\b", section)

    if match is None:
        return None

    return match.group(0)


def extract_declared_test_baseline(context: str) -> int | None:
    """
    Extrai a contagem declarada de testes da seção
    Current Development Status.
    """
    section = get_context_section(
        context,
        "Current Development Status",
    )

    if section is None:
        return None

    match = re.search(
        r"(\d+)\s+(?:passing\s+)?tests?\b",
        section,
        re.IGNORECASE,
    )

    if match is None:
        return None

    return int(match.group(1))


def get_context_consistency_checks(
    context: str,
    current_head: str,
    test_output: str,
) -> str:
    """
    Compara contexto humano com fatos observáveis.

    Diferença entre HEAD e stable baseline é informativa, pois
    pode representar WIP legítimo; não é tratada como falha.
    """
    checks: list[str] = []

    if not CONTEXT_FILE.exists():
        return (
            "FAIL — PROJECT_CONTEXT.md is missing. "
            "Semantic context recovery is incomplete."
        )

    declared_baseline = extract_declared_baseline(context)

    if declared_baseline is None:
        checks.append(
            "WARNING — Stable baseline commit was not found "
            "in PROJECT_CONTEXT.md."
        )
    elif current_head.startswith(declared_baseline) or (
        declared_baseline.startswith(current_head)
    ):
        checks.append(
            "PASS — Current HEAD matches the declared stable baseline."
        )
    else:
        checks.append(
            "INFO — Current HEAD differs from the declared stable "
            "baseline. This may represent intentional WIP or a newer "
            "committed state.\n"
            f"  Declared stable baseline: {declared_baseline}\n"
            f"  Current HEAD: {current_head}"
        )

    actual_test_count = extract_passing_test_count(test_output)
    declared_test_count = extract_declared_test_baseline(context)

    if declared_test_count is None:
        checks.append(
            "WARNING — Test baseline was not found in "
            "PROJECT_CONTEXT.md."
        )
    elif actual_test_count is None:
        checks.append(
            "WARNING — Current passing test count could not be "
            "extracted from pytest output."
        )
    elif declared_test_count == actual_test_count:
        checks.append(
            "PASS — Current passing test count matches the "
            f"declared baseline ({actual_test_count})."
        )
    else:
        checks.append(
            "INFO — Current passing test count differs from the "
            "declared stable baseline. This may be expected during "
            "development.\n"
            f"  Declared test baseline: {declared_test_count}\n"
            f"  Current passing tests: {actual_test_count}"
        )

    current_wip = get_context_section(context, "Current WIP")

    if current_wip is None:
        checks.append(
            "WARNING — Current WIP section is missing or empty."
        )
    else:
        checks.append(
            "PASS — Current WIP is explicitly documented."
        )

    next_capability = get_context_section(
        context,
        "Next Planned Capability",
    )

    if next_capability is None:
        checks.append(
            "WARNING — Next Planned Capability is missing or empty."
        )
    else:
        checks.append(
            "PASS — Next Planned Capability is explicitly documented."
        )

    return "\n\n".join(checks)


# ============================================================
# AUDIT BUILD
# ============================================================


def build_audit() -> str:
    """
    Coleta informações e monta o Project Context Snapshot v1.6.
    """
    started_at = datetime.now()
    snapshot_before = get_snapshot_signature()

    metrics = get_python_metrics()
    project_tree = get_project_tree()

    tests = get_tests()
    collected_tests = get_collected_tests()

    git_info = get_git_info()
    current_head = get_git_commit()
    recent_commits = get_recent_commits()
    working_tree = get_working_tree_summary()

    declared_dependencies = get_declared_dependencies()
    installed_dependencies = get_installed_dependencies()

    project_context = get_project_context()

    consistency_checks = get_context_consistency_checks(
        project_context,
        current_head,
        tests,
    )

    snapshot_after = get_snapshot_signature()

    integrity = evaluate_snapshot_integrity(
        snapshot_before,
        snapshot_after,
    )

    finished_at = datetime.now()
    duration = (finished_at - started_at).total_seconds()

    started_text = started_at.strftime("%Y-%m-%d %H:%M:%S")
    finished_text = finished_at.strftime("%Y-%m-%d %H:%M:%S")

    return f"""# PROJECT CONTEXT SNAPSHOT — LinkedIn Agentic AI System

Version: 1.6
Generated: {finished_text}

## Snapshot Integrity

```text
{integrity}
```

- Audit started: {started_text}
- Audit finished: {finished_text}
- Duration: {duration:.2f} seconds

## Context Consistency Checks

```text
{consistency_checks}
```

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
{project_tree}
```

## Test Execution

```text
{tests}
```

## Test Discovery / Behavioral Contracts

```text
{collected_tests}
```

## Git

{git_info}

## Recent Commits

```text
{recent_commits}
```

## Working Tree

```text
{working_tree}
```

## Declared Dependencies

```text
{declared_dependencies}
```

## Installed Dependencies

```text
{installed_dependencies}
```

## Development Context

{project_context}

---

## Context Recovery Purpose

This artifact is an automated snapshot of the current technical
and development state of the LinkedIn Agentic AI System.

Its primary purpose is to support development continuity,
technical review, debugging, handoffs, and context recovery
between human developers and AI coding agents.

For reliable context recovery, the automated repository snapshot
must be interpreted together with the human-maintained
PROJECT_CONTEXT.md.

The stable baseline, current WIP, and next planned capability are
deliberately separate concepts.
"""


# ============================================================
# ENTRY POINT
# ============================================================


def main() -> None:
    """Gera e sobrescreve o snapshot atual do projeto."""
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)

    audit = build_audit()
    AUDIT_FILE.write_text(audit, encoding="utf-8")

    print("Project context snapshot generated successfully:")
    print(AUDIT_FILE)


if __name__ == "__main__":
    main()
