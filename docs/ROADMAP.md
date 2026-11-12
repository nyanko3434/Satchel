# Satchel — Roadmap

> Status: initial plan, written 2026-11-11. Durations are rough estimates at about 15 hours a week; there is no deadline.
> Related docs: [VISION.md](VISION.md), [ARCHITECTURE.md](ARCHITECTURE.md), [DECISIONS.md](DECISIONS.md)

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
- Project setup: uv, ruff, pytest, CI, MIT licence, package layout.
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

- [ ] Check that the name `satchel` is free on PyPI and GitHub; choose a fallback package name if not.
- [ ] Create the repository and copy these documents into `docs/`.
- [ ] Write a `CLAUDE.md` for Claude Code that points to these documents and states the "who writes what" split.
- [ ] Get API keys for Claude and Groq.
