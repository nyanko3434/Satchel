"""Enforces the dependency rule from docs/ARCHITECTURE.md section 2.

Dependencies point inward: adapters and interfaces import the core, and the
core never imports an adapter or the interface.
"""

import ast
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parent.parent / "src"
CORE = SRC / "satchel" / "core"

# Packages the core must not import: the interface and every adapter package.
# Ports are defined in the core itself (decision A-08 in docs/DECISIONS.md), so
# the core never needs anything from these. Extend as adapter packages appear.
FORBIDDEN = (
    "satchel.interface",
    "satchel.providers",
    "satchel.storage",
    "satchel.tracing",
)


def module_name(path: Path) -> str:
    parts = list(path.relative_to(SRC).with_suffix("").parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def imported_modules(source: str, module: str, *, is_package: bool) -> set[str]:
    """Every dotted name the source could be importing, as absolute names."""
    package = module if is_package else module.rpartition(".")[0]
    found: set[str] = set()

    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            base = node.module or ""
            if node.level:
                anchor = package.split(".")
                anchor = anchor[: len(anchor) - (node.level - 1)]
                base = ".".join([*anchor, base] if base else anchor)
            found.add(base)
            # `from satchel import providers` imports satchel.providers.
            found.update(f"{base}.{alias.name}" for alias in node.names)

    return found


def forbidden_imports(source: str, module: str, *, is_package: bool) -> set[str]:
    return {
        name
        for name in imported_modules(source, module, is_package=is_package)
        if any(name == bad or name.startswith(f"{bad}.") for bad in FORBIDDEN)
    }


def test_core_does_not_import_adapters_or_interface() -> None:
    files = sorted(CORE.rglob("*.py"))
    assert files, f"no Python files found under {CORE}"

    violations = {
        str(path.relative_to(SRC)): sorted(bad)
        for path in files
        if (
            bad := forbidden_imports(
                path.read_text(encoding="utf-8"),
                module_name(path),
                is_package=path.name == "__init__.py",
            )
        )
    }

    assert not violations, f"core imports forbidden packages: {violations}"


@pytest.mark.parametrize(
    "source",
    [
        "import satchel.providers",
        "import satchel.providers.anthropic as a",
        "from satchel.providers import anthropic",
        "from satchel import interface",
        "from satchel.interface.cli import main",
        "from .. import providers",
        "from ..interface import cli",
        "from satchel.storage import sessions",
        "import satchel.tracing.jsonl",
        "def f():\n    from satchel.providers import x\n",
    ],
)
def test_checker_catches_forbidden_imports(source: str) -> None:
    assert forbidden_imports(source, "satchel.core.engine", is_package=False)


@pytest.mark.parametrize(
    "source",
    [
        "import json",
        "from pydantic import BaseModel",
        "from satchel.core import messages",
        "from . import messages",
        "from .messages import Message",
        "import satchel.providers_extra",
    ],
)
def test_checker_allows_other_imports(source: str) -> None:
    assert not forbidden_imports(source, "satchel.core.engine", is_package=False)
