# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Satchel is a terminal assistant that answers from user-controlled knowledge bases (RAG) and carries out tasks on the user's machine with approval (tool-calling agent). It is a learning and portfolio project, built in versions: v0 skeleton → v1 RAG → v1.5 RAG evaluation → v2 agent → v3 extensions.

**Current state: early v0.** Tooling, CI, config loading (`src/satchel/config/`) and a thin CLI (`src/satchel/interface/cli.py`) exist. `core`, `providers`, `tracing` and `storage` are still empty packages. Almost everything in `docs/` describes the intended design, not existing code. Check what actually exists before assuming a module is there.

**What is next:** the "v0 progress" table in `docs/ROADMAP.md` lists every v0 step with its owner, status and prerequisites. Read it at the start of a session and update it when a step starts or finishes. The next steps (message format, `Provider` port) are Nayan's.

The design docs are the source of truth and should be read before non-trivial work:

- `docs/VISION.md` — purpose, principles, non-goals
- `docs/ARCHITECTURE.md` — modules, ports, events, on-disk layout
- `docs/ROADMAP.md` — scope and "done when" per version, and who writes each part
- `docs/DECISIONS.md` — decision log with IDs (A-01, S-02, …) and open questions
- `docs/PROJECT_LOG.md` — dated log of work done

## Standing rules

1. **Keep the docs current.** When a change makes any doc (including this file) out of date, update it in the same piece of work.
2. **Log the work.** Add an entry to `docs/PROJECT_LOG.md` for each piece of completed work, newest first, in the format that file describes, and update the "v0 progress" table in `docs/ROADMAP.md`.
3. **No agent or RAG frameworks** (LangChain, LlamaIndex, LiteLLM, and similar). Libraries only for commodity parts (A-03, S-02).
4. **No new dependency without an entry in `docs/DECISIONS.md`**, runtime or dev (A-07). Write the entry first, then add the package.
5. **The core never imports from adapters or the interface.** `tests/test_architecture.py` enforces this; do not weaken that test to make code pass.
6. **Read `docs/ARCHITECTURE.md` before structural changes** (new packages, moved modules, new ports, changed boundaries), and update it if the structure changes.
7. **One branch per piece of work; never push or merge to `main`** (P-08). Branch from an up-to-date `main`, named `<version>/<topic>` (for example `v0/tracing`). Commit in small logical commits. When the work is finished (the four checks pass, docs and project log updated), push the branch to `origin` and stop: Nayan opens the pull request, checks CI and merges. Code, tests, dependencies and design changes always go through a branch. Only trivia (a typo, a one-line doc correction) may be committed straight to `main`, and even then it is not pushed.

## Who writes what (decision P-06)

This is the most important rule in the repo. The project exists so the author learns by building the core.

- **Nayan writes by hand:** the neutral message format, provider adapters (including the tool-calling path), the core turn function and agent loop, chunking, vector search, the retrieval pipeline, grounding prompt and strict-mode logic, tool descriptions and schemas, permission rules, evaluation metrics and the LLM-judge prompt.
- **Claude Code writes:** project scaffolding, the terminal UI/REPL, CLI plumbing, config loading, storage, document parsers, individual tool implementations, diff rendering, terminal handoff, recipe loading, the approval UI, eval runner and dataset loading, tests and boilerplate.

Do not implement a "Nayan writes" part unless explicitly asked to. For those parts, explain, review, or write tests and surrounding plumbing instead. `docs/ROADMAP.md` has the exact split per version.

## Working rules from the design docs

- **Decisions come first.** Record a design decision in `docs/DECISIONS.md` before implementing it. Add or supersede entries; never rewrite history. Entries marked *Proposed* are not yet confirmed, so raise them rather than treating them as settled.
- **Dependencies are pinned** through `uv.lock`, which is committed (A-07).
- **Linux only** for now, with nothing distribution-specific hard-coded (P-04). Environment details are detected at runtime.
- MIT licence constrains dependencies: AGPL libraries such as PyMuPDF/pymupdf4llm can only be optional add-ons (S-07).

## Repository layout

The uv project is at the repo root (`pyproject.toml`, `uv.lock`, `src/satchel/`, `tests/`), with the design docs in `docs/` and the virtualenv in `.venv/`.

Packages under `src/satchel/` that exist so far: `config` (settings, XDG paths, loader) and `interface` (`cli.py`) have code; `core`, `providers`, `tracing` and `storage` are empty apart from a docstring. `kb`, `tools`, `permissions` and `eval` are created in their own versions, not before.

## Commands

Run from the repo root. Package management is uv; the supported floor is Python 3.12 and development uses 3.14 (S-13).

```bash
uv sync                                   # install from the lockfile
uv run satchel --version                  # run the CLI
uv run satchel config                     # show loaded settings and file locations
uv run satchel --config PATH config       # same, for a config file other than the XDG one
uv run pytest                             # all tests
uv run pytest tests/test_cli.py           # one file
uv run pytest tests/test_cli.py::test_chat_is_a_stub_for_now   # one test
uv run pytest -k checker                  # tests matching a keyword
uv run ruff check .                       # lint (add --fix to apply fixes)
uv run ruff format .                      # format (CI runs --check)
uv run mypy                               # strict type check of src/ and tests/
uv add <package>                          # runtime dependency: DECISIONS.md entry first
uv add --dev <package>                    # dev dependency: DECISIONS.md entry first
```

CI (`.github/workflows/ci.yml`) runs ruff check, ruff format --check, mypy and pytest on Python 3.12 and 3.14. All four must pass locally before work is called done. Python 3.12 is not installed on the development machine, so 3.12 compatibility is checked only in CI; avoid syntax and stdlib features newer than 3.12.

ruff skips Markdown files on purpose: the code blocks in the design docs are sketches.

## Architecture (intended)

Ports and adapters. The core defines ports as Python `Protocol` classes; adapters implement them. **Dependencies point inward: adapters and interfaces import the core, and the core never imports an adapter.** The `Protocol` classes are defined inside `core`, and `providers`, `storage` and `tracing` hold only implementations (A-08).

- **Core ↔ interface boundary.** The interface never calls a model or a tool. It sends user input to the core and consumes a stream of events (`TextDelta`, `SourcesFound`, `ToolCallRequested`, `PermissionRequired`, `ToolStarted`/`ToolFinished`, `TerminalHandoff`, `TurnCompleted`, `ErrorRaised`), answering `PermissionRequired` with a `PermissionDecision`. Events are plain Pydantic data so a different front end can replace the terminal UI.
- **One provider-neutral message format.** The core uses a single `Message` type with text, tool-call and tool-result blocks. Each provider adapter (Anthropic; OpenAI-compatible, Groq first) translates both ways, using the official SDKs behind the `Provider` port. Adapters expose `Capabilities` so the core can handle models that lack reliable tool calling.
- **Knowledge base.** `parse → chunk → embed → store` on ingest, `embed → search → top-k` on retrieve, behind the `DocumentParser`, `Embedder` and `VectorStore` ports. Each KB is a self-contained folder: `sources/` is the source of truth and `index/` is derived and rebuildable. `kb.toml` records the embedding model so a mismatch triggers a re-index instead of wrong results. The CLI (`satchel kb ...`) and in-chat `/kb` commands call the same `kb` module.
- **Agent loop (v2).** The model only produces a tool name and arguments. Satchel's code validates against the tool's Pydantic schema, consults the permission policy, executes, and feeds results (including failures and denials) back as tool-result blocks, up to a step limit. Intent routing is done by tool calling, not a separate classifier (T-01).
- **Tracing.** Every step of every turn is traced to JSON Lines from v0, because the evaluation harness replays test sets through the real core and depends on those traces.

Planned cross-cutting choices: async core (`asyncio`), Pydantic models at boundaries, unit tests using fakes for the ports plus a few end-to-end tests with a scripted fake provider and no network.

Runtime data follows XDG: config and recipes in `~/.config/satchel/`, knowledge bases and SQLite sessions in `~/.local/share/satchel/`, traces in `~/.local/state/satchel/traces/`, embedding models in `~/.cache/satchel/`. API keys come from environment variables and are never written to config.

**Config (built).** `config.toml` holds named provider entries, each with a `type` (`anthropic` or `openai_compat`), a `model`, and optionally `base_url` and `api_key_env`; top-level `provider` selects the active one (schema in `ARCHITECTURE.md` §9). Things to preserve when touching it:

- `Settings` never holds a key, only the name of the environment variable. Keys are read on demand with `read_api_key()`.
- The `config` package imports nothing else from `satchel` (enforced by `tests/test_architecture.py`). The CLI is the composition root: it loads settings and passes them inward.
- Functions take `env` and `home` as parameters instead of reading `os.environ` or `Path.home()` themselves; only `cli.main()` supplies the real ones. Tests pass fakes and never touch the real home directory.
- User-facing config problems are raised as `ConfigError` with a complete message; the CLI prints it and exits with code 2.

## Safety invariants

These are non-negotiable design constraints, and any code touching tools, commands or permissions must preserve them:

- Satchel never asks for, sees or stores a password. Interactive commands (for example a sudo prompt) are handed to the real terminal via `TerminalHandoff`; the core receives only the exit code and captured output (X-01).
- Three permission tiers: read-only runs automatically; changes ask first; privileged or destructive actions always ask and are never remembered. There is no approve-everything mode (X-02, X-06).
- Risk tiers are assigned by rules in code, never by the model. Anything unrecognised defaults to asking (X-04).
- File tools are scoped to the working directory unless the user allows more (X-03).
- Knowledge-base content and command output are data, not instructions. Tool calls they provoke still go through the normal permission flow (X-05).
- Commands that run other commands (`setsid`, `systemd-run`, `hyprctl dispatch exec`, `busctl call`, `gdbus call`) are never read-only (X-10).
- Reading the screen, an accessibility tree or the clipboard always asks and is never remembered (X-08). Sending input to the desktop is privileged (X-09).
- Recipe parameter values are shell-escaped before substitution.
- The executor has a dry-run mode; evaluation must never touch the real system (X-07).
