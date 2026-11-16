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

## 2026-11-16 — Docs brought up to date; README written

**Version:** v0        **By:** Claude Code

- Went through every doc against the state of the repository and corrected what had fallen behind.
- Added a "v0 progress" table to the roadmap: ten steps with owner, status and what each one needs first, plus the questions still to settle in v0.
- Wrote `README.md`, which had been empty: what Satchel is, its current state, how to set up for development, and where the docs are.
- First piece of work done on a branch (`v0/docs-sync`) under P-08.

**Decisions:** none.
**Docs updated:** `README.md`, `ROADMAP.md` (v0 progress), `ARCHITECTURE.md` (status line, §10), `CLAUDE.md` (pointer to the progress table), this file.
**Follow-ups:** the questions listed under "v0 progress" in the roadmap.

## 2026-11-16 — Branch workflow adopted

**Version:** v0        **By:** Nayan (decision), Claude Code (recording it)

- From here on, each piece of work is done on its own branch and reaches `main` through a pull request once CI passes. Everything up to and including config loading was committed directly to `main`.

**Decisions:** P-08 added.
**Docs updated:** `DECISIONS.md`, `CLAUDE.md` (standing rule 7), this file.
**Follow-ups:** optionally protect `main` on GitHub so the rule is enforced there too.

## 2026-11-16 — Config loading

**Version:** v0        **By:** Claude Code

- Added the `config` package: `Paths` (XDG locations, computed without creating anything on disk), `Settings` and `ProviderSettings` (Pydantic models), `load_settings()` and `read_api_key()`.
- Providers are named entries in `config.toml`, each with a `type`, a `model`, and optionally `base_url` and `api_key_env`; top-level `provider` selects the active one.
- API keys are never stored in the settings. Only the name of the environment variable is, and the key is read when needed.
- Config problems are reported as a single message naming the file and the field.
- Added `satchel config`, which shows the loaded settings and file locations and reports each key variable only as set or not set, and a global `--config PATH` option.
- Added pydantic as the first runtime dependency and enabled its mypy plugin.
- Added tests for paths, loading, key lookup and the new command, plus a test that `config` imports nothing else from Satchel. 57 tests in total.

**Decisions:** none new. pydantic is covered by S-01, TOML by S-09. XDG lookup is written by hand instead of adding `platformdirs` (A-07, P-04).
**Docs updated:** `ARCHITECTURE.md` (§9: config schema and loader rules), `CLAUDE.md` (state, commands, config notes, commit rule), this file.
**Follow-ups:**
- Building a provider object from the settings comes with `satchel chat`, once the `Provider` port and adapters exist.
- `recipes.toml` loading is v2.
- Everything up to this entry has been pushed to `main`. The result of the CI runs has not been checked from the development machine.

## 2026-11-16 — Ports live in the core

**Version:** v0        **By:** Nayan (decision), Claude Code (recording it)

- Settled where the port `Protocol` classes live: in `core`, with adapter packages holding only implementations.
- Extended the boundary test so `core` may not import `satchel.storage` or `satchel.tracing` either, in addition to `satchel.providers` and `satchel.interface`.
- Confirmed TOML as the format for config and recipes.

**Decisions:** A-08 added; O-09 resolved by A-08; S-09 moved from Proposed to Decided.
**Docs updated:** `DECISIONS.md`, `ARCHITECTURE.md` (§2, §3, §10), this file.
**Follow-ups:** where the knowledge base's own ports live is decided when v1 starts.

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
