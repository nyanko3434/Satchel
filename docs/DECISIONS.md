# Satchel — Decision Log

> Started 2026-11-11. Add a new entry whenever a decision is made or changed; do not rewrite history, supersede it.
> Related docs: [VISION.md](VISION.md), [ARCHITECTURE.md](ARCHITECTURE.md), [ROADMAP.md](ROADMAP.md), [PROJECT_LOG.md](PROJECT_LOG.md)

Status values: **Decided** (agreed), **Proposed** (recommended, not yet confirmed), **Open** (needs a decision).

## Project

| ID | Decision | Why | Status |
|---|---|---|---|
| P-01 | The project is named **Satchel**. | It carries your knowledge and your tools. | Decided (availability checked 2026-11-16; the PyPI name is taken, see O-01) |
| P-02 | It is a learning and portfolio project that other people can install and use. | Sets the quality bar: real packaging, docs and tests. | Decided |
| P-03 | Open source under the **MIT** licence. | Permissive and simple. | Decided |
| P-04 | **Linux only** at first; other platforms later. | Keeps v0–v2 focused. Nothing distribution-specific is hard-coded. | Decided |
| P-05 | Build in versions: v0 skeleton, v1 RAG, v1.5 RAG evaluation, v2 agent, v3 extensions. | Each version works alone and teaches one topic. | Decided |
| P-06 | Nayan writes the core by hand; Claude Code writes supporting parts. | The core is where the learning is. | Decided |
| P-07 | About 15 hours a week, no deadline. | — | Decided |

## Architecture

| ID | Decision | Why | Status |
|---|---|---|---|
| A-01 | **Ports and adapters.** The core depends only on interfaces. | Low coupling; every edge is replaceable and testable. | Decided |
| A-02 | The interface is separate from the core and consumes a stream of **events**. | A different front end can be added without touching the core. | Decided |
| A-03 | **No agent or RAG framework** (LangChain, LlamaIndex and similar). Libraries only for commodity parts. | Frameworks hide what the project exists to teach. | Decided |
| A-04 | One **provider-neutral message format** in the core; adapters translate. | Providers use different wire formats for tool calls. | Proposed |
| A-05 | **Async** core (`asyncio`). | Fits streaming, the terminal UI and provider SDKs. | Proposed |
| A-06 | Trace every step of every turn from v0. | Evaluation and debugging depend on it. | Decided |
| A-07 | Few dependencies, each justified, pinned with a lockfile. | Smaller attack surface (a widely used LLM library had malicious releases on PyPI in March 2026) and easier maintenance. | Decided |

## Stack

| ID | Decision | Why | Status |
|---|---|---|---|
| S-01 | **Python 3.12+**, uv, ruff, pytest, Pydantic. | Richest ecosystem for RAG and evaluation; Pydantic generates tool schemas. | Decided |
| S-02 | Providers through the official `anthropic` and `openai` SDKs behind our own `Provider` port. Not LiteLLM. | Writing the adapters is a learning goal. | Decided |
| S-03 | Start with **Claude and Groq**. | They cover the two main tool-calling formats. Groq's API is OpenAI-compatible, so that adapter extends to other compatible servers. | Decided |
| S-04 | Terminal UI: **Rich + prompt_toolkit** REPL first, **Textual** later. | A thin first UI proves the event boundary before investing in a full TUI. | Proposed |
| S-05 | **Local embeddings** through sentence-transformers, small baseline model first. | Free, private, no extra API key. Claude offers no embeddings API. | Proposed |
| S-06 | Vector search: **hand-written NumPy** cosine search in v1, **LanceDB** later behind the same port. | A small knowledge base needs no index, and writing the search teaches retrieval. | Proposed |
| S-07 | PDF parsing with **pypdf** first. pymupdf4llm only as an optional add-on. | pypdf is BSD-licensed. PyMuPDF and pymupdf4llm are AGPL, which complicates an MIT release. | Proposed |
| S-08 | Sessions and metadata in **SQLite**; traces as **JSON Lines**. | No server to run; easy to inspect. | Proposed |
| S-09 | **TOML** for config and recipes. | Parser is in the standard library; one format for everything. | Proposed |
| S-10 | Evaluation metrics written by hand first; compare with DeepEval later. | Writing them is a learning goal. | Decided |
| S-11 | Type checking with **mypy** in strict mode, as a dev dependency and in CI. | Pure Python, mature, and has an official Pydantic plugin, which matters with Pydantic models at every boundary. pyright pulls in a Node.js runtime; ty is younger and has no Pydantic plugin. | Decided (2026-11-16) |
| S-12 | Command-line parsing with the standard library's **`argparse`**; no CLI framework. | No dependency (A-07). Revisit if `satchel kb ...` outgrows it. | Proposed (2026-11-16) |
| S-13 | The supported floor is **Python 3.12** (`requires-python = ">=3.12"`); development uses 3.14 and CI tests both. | Confirms S-01 after `uv init` had defaulted the project to 3.14 only. A lower floor lets more people install it and is safer for the ML dependencies coming in v1. | Decided (2026-11-16) |

## Knowledge base

| ID | Decision | Why | Status |
|---|---|---|---|
| K-01 | **Several switchable** knowledge bases. | Requested feature. | Decided |
| K-02 | Managed through **terminal commands**, backed by one `kb` module. No web page. | "Portal" means an entry point, not a website. | Decided |
| K-03 | Inputs: text, Markdown, PDF, and **pasted raw text snippets**. Start simple, grow later. | Requested feature. | Decided |
| K-04 | Each knowledge base is a folder: original sources plus a derived, rebuildable index. | Easy to view, back up, switch and delete. | Proposed |
| K-05 | **Strict mode** is a toggle and applies to knowledge answers only, not actions. | Requested feature; scope agreed. | Decided |
| K-06 | Strict mode = prompt + retrieval threshold + citations + refusal path, verified by evaluation. | It cannot be a hard guarantee; it has to be measured. | Decided |

## Agent and tools

| ID | Decision | Why | Status |
|---|---|---|---|
| T-01 | Intent is handled by **tool calling**, not a separate classifier. | One loop covers tasks, knowledge questions, mixed requests and refusals. | Decided |
| T-02 | Five core tools: `run_command`, `read_file`, `edit_file`, `write_file`, `search_knowledge_base`. | General tools cover the target tasks; a small set keeps tool selection accurate. | Decided |
| T-03 | **Recipes** (user-defined tools in config) ship in **v2**, after the core tools. | They are the "user easily creates a task" feature and are thin wrappers over command execution. | Decided |
| T-04 | `edit_file` uses exact string replacement, requires a prior read, and shows a diff. | Predictable, reviewable edits. | Proposed |
| T-05 | Failures go back to the model as tool results; turns have a step limit. | Lets the model self-correct without running forever. | Proposed |
| T-06 | No separate planner until evaluation shows the loop is not enough. | Avoid complexity before there is evidence for it. | Decided |
| T-07 | An environment block (distribution, package manager, shell, working directory) is detected at runtime and given to the model. | The model cannot pick the right command without it. | Decided |

## Safety

| ID | Decision | Why | Status |
|---|---|---|---|
| X-01 | Satchel **never** asks for, sees or stores a password. Interactive commands are handed to the real terminal. | Non-negotiable trust boundary. | Decided |
| X-02 | **Three permission tiers:** read-only runs automatically; changes ask first; privileged or destructive actions always ask and are never remembered. | Balance of safety and convenience. | Decided |
| X-03 | Access is **limited to the working directory** unless the user allows more. | Smallest useful default scope. | Decided |
| X-04 | Risk tiers are assigned by **rules in code**, not by the model; unknown commands default to asking. | The model's own risk estimate cannot be trusted. | Proposed |
| X-05 | Knowledge-base content and command output are treated as **data, not instructions**. | Defence against prompt injection. | Proposed |
| X-06 | No "approve everything" mode by default. | Too easy to cause damage. | Decided |
| X-07 | A **dry-run executor** exists for evaluation and for users. | Evaluating an agent must not touch the real system. | Proposed |

## Open questions

| ID | Question | Needed by |
|---|---|---|
| O-01 | Is `satchel` free on PyPI and GitHub? If not, what is the package name? **Checked 2026-11-16:** the PyPI name `satchel` is taken by an unrelated placeholder project (one release, 1.0, no files, "Planning" status). The GitHub repository exists at `nyanko3434/Satchel`; other unrelated projects share the name, none of them a Python assistant. Still open: the PyPI distribution name (a fallback such as a suffixed name, or a PEP 541 request for the abandoned name). The import name and the `satchel` command can stay as they are. | Before publishing to PyPI (v3); does not block v0, since installing from the Git repository works |
| O-02 | Which embedding model becomes the default? | v1.5, decided by evaluation |
| O-03 | Which chunking strategy and sizes? | v1, revisited in v1.5 |
| O-04 | In v2, is retrieval only a tool, or is "always retrieve" kept as a mode? | v2, decided by evaluation |
| O-05 | How are capability differences between models (especially small local ones) represented and handled? | v2 / v3 |
| O-06 | Which commands are on the read-only allowlist, and which patterns are privileged? | v2 |
| O-07 | Is path-scoping for `run_command` worth real sandboxing? | v3 |
| O-08 | MCP client support: worth adding, and when? | v3 |
| O-09 | Where do the port `Protocol`s live? ARCHITECTURE.md §10 puts the base port in `providers/`, but the `Provider` port refers to the core's `Message`, and the core has to type against the port, so `core` and `providers` would import each other. Options: (a) ports live in `core`, and adapter packages hold only implementations; (b) each package keeps a `base` module that the core is allowed to import. Recommendation: (a). The boundary test in `tests/test_architecture.py` currently assumes (a) by forbidding all of `satchel.providers`. | Before the `Provider` port is written (v0) |
