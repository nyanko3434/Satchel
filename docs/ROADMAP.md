# Satchel — Roadmap

> Status: initial plan, written 2026-11-11; v0 progress last updated 2026-11-16. Durations are rough estimates at about 15 hours a week; there is no deadline.
> Related docs: [VISION.md](VISION.md), [ARCHITECTURE.md](ARCHITECTURE.md), [DECISIONS.md](DECISIONS.md), [PROJECT_LOG.md](PROJECT_LOG.md)

Each version ends with something that works and can be shown. "You write" marks the parts Nayan implements by hand; "Claude Code writes" marks supporting work.

| Version | Theme | Rough duration |
|---|---|---|
| v0 | Skeleton: chat with any provider | 2 weeks |
| v1 | RAG: answers from a knowledge base | 3–4 weeks |
| v1.5 | Evaluation harness for RAG | 2 weeks |
| v2 | Agent: tools, recipes, permissions | 5–6 weeks |
| v3 | Extensions | open |

---

## v0 — Skeleton

**Goal:** a streaming chat in the terminal that works with Claude and Groq, built on the final module boundaries.

**Scope**
- Project setup: uv, ruff, mypy, pytest, CI, MIT licence, package layout.
- Neutral message format and the `Provider` port.
- Anthropic adapter and OpenAI-compatible adapter (Groq), with streaming.
- Core engine: conversation state, one turn in, events out.
- Event protocol between core and interface.
- Minimal terminal UI: a Rich + prompt_toolkit REPL.
- Config loading; API keys from environment variables.
- Tracing to JSON Lines; sessions in SQLite.

**You write:** the message format, both provider adapters, the core turn function.
**Claude Code writes:** project scaffolding, the REPL, config loading, storage, tests.

**Done when**
- `satchel chat` streams answers from either provider, selected in config.
- The core runs in a test with a fake provider and no network.
- A trace file exists for every session.

**You will have learned:** how provider APIs differ, how streaming works, how to draw a boundary between a core and its interface.

### v0 progress

Update this table whenever a step starts or finishes. Each step is done on its own branch (P-08).

| # | Step | Who | Status | Needs first |
|---|---|---|---|---|
| 1 | Project setup: uv, ruff, mypy, pytest, CI, package skeleton, boundary test | Claude Code | Done 2026-11-16 | — |
| 2 | Config loading: XDG paths, `config.toml`, keys from the environment, `satchel config` | Claude Code | Done 2026-11-16 | — |
| 3 | Neutral message format in `core` (`Message` and its blocks) | Nayan | **Next** | Confirm A-04 |
| 4 | `Provider` port, `ProviderEvent`, `Capabilities` in `core` | Nayan | Not started | Step 3; confirm A-05 (async), since it fixes the port's signature |
| 5 | Scripted fake provider for tests | Claude Code | Blocked | Step 4 |
| 6 | Event models and the core turn function | Nayan | Not started | Step 4 |
| 7 | Anthropic adapter, then OpenAI-compatible adapter (Groq), with streaming | Nayan | Not started | Step 4; API keys; adds the `anthropic` and `openai` SDKs (S-02) |
| 8 | Tracing to JSON Lines and sessions in SQLite | Claude Code | Blocked | Steps 3 and 6; confirm S-08 |
| 9 | Rich + prompt_toolkit REPL, `satchel chat`, building a provider from the settings | Claude Code | Blocked | Steps 6 and 7; confirm S-04 before adding either library |
| 10 | End-to-end test: core with the fake provider, no network, one trace file per session | Claude Code | Blocked | Steps 5, 6 and 8 |

Questions to settle along the way:

- **Who writes the event models (step 6)?** The scope above lists the event protocol but assigns it to nobody. They live in `core`.
- **Who writes the `Tracer` and `SessionStore` port definitions (step 8)?** Under A-08 they live in `core`; the implementations in `tracing` and `storage` are Claude Code's.
- **S-12** (`argparse` for the command line) is still marked Proposed although the CLI is built on it. Confirm it or replace it.
- The first CI run on GitHub has not been checked from the development machine. Look at the Actions tab, and consider protecting `main` so pull requests need a passing run.

---

## v1 — RAG

**Goal:** cited answers from switchable knowledge bases, with a strict mode.

**Scope**
- Knowledge-base manager: create, list, use, show, add, remove, reindex.
- Ingestion: `.txt` and `.md` first, then pasted snippets, then PDF (pypdf).
- Chunking: start with a simple fixed-size strategy with overlap.
- `Embedder` port with a local sentence-transformers model.
- `VectorStore` port with a hand-written NumPy cosine search.
- Retrieve-then-generate pipeline with citations.
- Strict mode toggle: prompt, score threshold, refusal path.
- `/kb` and `/strict` commands inside the chat.

**You write:** chunking, the brute-force vector search, the retrieval pipeline, the grounding prompt and strict-mode logic.
**Claude Code writes:** parsers, the `kb` command-line plumbing, on-disk layout, tests.

**Done when**
- A new user can create a knowledge base, add a PDF and a text snippet, and get an answer that cites the right passage.
- With strict mode on, a question the knowledge base cannot answer gets a refusal.
- Switching knowledge bases is one command.

**You will have learned:** embeddings, similarity search, chunking trade-offs, grounding and why retrieval quality decides answer quality.

---

## v1.5 — Evaluation for RAG

**Goal:** numbers instead of impressions.

**Scope**
- A small hand-made test set: questions, reference answers, and the passages that should be retrieved. Include questions the knowledge base cannot answer.
- Eval runner that replays the set through the real pipeline.
- Retrieval metrics: recall@k, mean reciprocal rank.
- Answer metrics: faithfulness (LLM-judged), correctness, correct-refusal rate.
- A results file committed to the repository, so changes can be compared.
- Experiments: chunk size, top-k, embedding model, strict-mode threshold.

**You write:** the metrics and the LLM-judge prompt.
**Claude Code writes:** the runner, result formatting, dataset loading.

**Done when**
- One command produces a results table.
- At least two design choices from v1 (for example chunk size and embedding model) have been revisited using the numbers.

**You will have learned:** how to build a test set, what each metric does and does not tell you, and the limits of LLM-as-judge.

---

## v2 — Agent

**Goal:** Satchel carries out tasks from plain-language requests, safely.

Built in this order, each step usable before the next:

1. **Tool-calling path.** `Tool` port, registry, schema generation from Pydantic, argument validation, tool calls and results in both provider adapters.
2. **The agent loop.** Multi-step turns, errors fed back to the model, a step limit.
3. **Read-only tools.** `search_knowledge_base` and `read_file`. Retrieval becomes a tool; keep the v1 always-retrieve pipeline so the two approaches can be compared in evals.
4. **Permissions.** Three tiers, rule-based classification, working-directory scope, approval prompts in the UI, remembered "always allow".
5. **Changing tools.** `edit_file` (exact replacement, read-first, diff preview), `write_file`.
6. **`run_command`.** Timeouts, output truncation, environment block, terminal handoff for interactive commands, dry-run mode.
7. **Recipes.** User-defined tools from `recipes.toml`, with shell-escaped parameters.
8. **Agent evaluation.** A task set with expected tools and arguments; tool-selection accuracy, argument correctness, task success, unnecessary calls, correct refusals. Runs against the dry-run executor or a container.

**You write:** the tool-calling path in the adapters, the agent loop, the tool descriptions and schemas, the permission rules, the agent metrics.
**Claude Code writes:** the individual tool implementations, diff rendering, terminal handoff, recipe loading, the approval UI, tests.

**Done when**
- "install X", "open Y", "refresh the waybar" (via a recipe) and "change Z in this file" each produce the correct call, an approval prompt, and the correct result.
- A mixed request ("what do my notes say about X, and add that to notes.md") is handled in one turn.
- A request outside its capabilities gets a clear refusal.
- No password ever passes through Satchel.
- The agent eval produces a results table.

**You will have learned:** how tool calling works on the wire, how descriptions and schemas steer tool choice, how agent loops recover from errors, and how to make an agent safe to run on a real machine.

---

## v3 — Extensions

Not committed. Pick based on what v2 teaches.

- Textual-based terminal UI.
- LanceDB vector store and hybrid search; reranking.
- More providers: Gemini, OpenAI, local models through Ollama, with capability flags.
- Better PDF parsing (optional pymupdf4llm or Docling add-ons).
- MCP client support, so existing MCP servers become tools.
- Planning for long multi-step tasks.
- Sandboxed command execution.
- A second interface (local API or web) to prove the boundary.
- Windows and macOS support.
- Publishing to PyPI.

---

## Before starting v0

- [x] Check that the name `satchel` is free on PyPI and GitHub. Done 2026-11-16: the PyPI name is taken (see O-01 in [DECISIONS.md](DECISIONS.md)).
- [ ] Choose a fallback PyPI distribution name. Not needed until publishing (v3).
- [x] Create the repository and copy these documents into `docs/`.
- [x] Write a `CLAUDE.md` for Claude Code that points to these documents and states the "who writes what" split.
- [ ] Get API keys for Claude and Groq.
