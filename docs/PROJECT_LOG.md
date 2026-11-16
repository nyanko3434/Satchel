# Satchel — Project Log

> Started 2026-11-16. A dated record of work done, newest entry first. Add an entry when a piece of work is finished.
> Related docs: [VISION.md](VISION.md), [ARCHITECTURE.md](ARCHITECTURE.md), [ROADMAP.md](ROADMAP.md), [DECISIONS.md](DECISIONS.md)

This log records **what was done**. The reasons behind choices belong in [DECISIONS.md](DECISIONS.md), and what comes next belongs in [ROADMAP.md](ROADMAP.md).

Entry format:

```
## YYYY-MM-DD — short title

**Version:** v0 | v1 | …        **By:** Nayan | Claude Code | both

- What was done, one line per item.

**Decisions:** IDs added or changed, or "none".
**Docs updated:** files touched, or "none".
**Follow-ups:** anything left open, or "none".
```

---

## 2026-11-16 — Project scaffolding for v0

**Version:** v0 (setup)        **By:** Claude Code

- Moved the uv project from `satchel/` to the repository root, so the layout matches ARCHITECTURE.md §10 and the root `.venv`.
- Added `.gitignore` and removed a committed `.pyc` file from version control.
- Set `requires-python` to `>=3.12`, filled in the project description and licence metadata.
- Added ruff, pytest and mypy as dev dependencies, with configuration in `pyproject.toml`, and created `uv.lock`.
- Created empty packages for the v0 modules: `core`, `providers`, `interface`, `config`, `tracing`, `storage`.
- Replaced the `uv init` stub with a thin `argparse` CLI (`satchel --version`, and a `satchel chat` stub that reports it is not implemented).
- Added `tests/test_cli.py` and `tests/test_architecture.py`. The second one fails if anything under `core/` imports `satchel.providers` or `satchel.interface`.
- Added a GitHub Actions workflow that runs ruff, mypy and pytest on Python 3.12 and 3.14.
- Checked name availability: the PyPI name `satchel` is taken by an unrelated placeholder project.
- Added a "Standing rules" section to `CLAUDE.md` and rewrote its layout and commands sections.

**Decisions:** S-11 (mypy), S-12 (argparse, proposed), S-13 (Python 3.12 floor) added; O-01 updated with the name-check result; O-09 (where ports live) opened; P-01 status updated.
**Docs updated:** `CLAUDE.md`, `DECISIONS.md`, `ARCHITECTURE.md` (§10, §11), `ROADMAP.md` (pre-v0 checklist), this file.
**Follow-ups:**
- The CI workflow has not run yet; it runs on the first push.
- Python 3.12 is not installed locally, so 3.12 compatibility is checked only in CI.
- O-09 needs a decision before the `Provider` port is written.
- A fallback PyPI distribution name is needed before publishing (O-01).
- `README.md` is still empty.

## 2026-11-16 — uv project created; CLAUDE.md written

**Version:** pre-v0        **By:** both

- Nayan created the Python project with `uv init` (commit `a913627`).
- Claude Code wrote the first `CLAUDE.md` from the design docs.

**Decisions:** none.
**Docs updated:** `CLAUDE.md`.
**Follow-ups:** none.

## 2026-11-12 — Repository created; design docs committed

**Version:** pre-v0        **By:** Nayan

- Created the GitHub repository with the MIT licence (commit `c320448`).
- Committed the four design documents written on 2026-11-11: `VISION.md`, `ARCHITECTURE.md`, `DECISIONS.md`, `ROADMAP.md` (commit `a3d2da6`).

**Decisions:** the initial decision log (P, A, S, K, T, X and O series).
**Docs updated:** all four created.
**Follow-ups:** none.
