# Satchel — Architecture

> Status: initial design, written 2026-11-11. Interfaces shown here are starting sketches, not final signatures. Expect this document to change as each version is built.
> Related docs: [VISION.md](VISION.md), [ROADMAP.md](ROADMAP.md), [DECISIONS.md](DECISIONS.md)

## 1. Goals for the design

- **High cohesion, low coupling.** Each module has one job and talks to the others through small interfaces.
- **Replaceable edges.** The interface, the model provider, the embedder, the vector store and the document parser can each be swapped without touching the core.
- **Testable core.** The core can run in tests with a fake provider and a dry-run executor, with no network and no side effects.
- **Observable.** Every step of a turn is traced, because evaluation depends on it.

## 2. Style: ports and adapters

The core defines *ports* (Python `Protocol` classes). *Adapters* implement them. Dependencies point inward: adapters and interfaces import the core, and the core never imports an adapter.

```
        ┌─────────────────────────────────────────────┐
        │                 Interfaces                  │
        │   terminal UI (now) · web / API (later)     │
        └──────────────────────┬──────────────────────┘
                 user input    │    events
                               ▼
        ┌─────────────────────────────────────────────┐
        │                 Core engine                 │
        │  conversation state · agent loop · prompts  │
        │  permission flow · tracing hooks            │
        └───┬──────────┬──────────┬──────────┬────────┘
            │          │          │          │        ports
            ▼          ▼          ▼          ▼
        ┌────────┐ ┌─────────┐ ┌────────┐ ┌──────────┐
        │  LLM   │ │Knowledge│ │ Tools  │ │ Storage  │
        │provider│ │  base   │ │        │ │ & traces │
        └───┬────┘ └───┬─────┘ └───┬────┘ └────┬─────┘
            │          │           │           │      adapters
        Anthropic   embedder    shell       SQLite
        OpenAI-     vector      file ops    JSONL
        compatible  store       recipes
                    parsers
```

## 3. Modules

| Module | Responsibility | Port | First appears |
|---|---|---|---|
| `core` | Conversation state, the turn loop, prompt assembly, emitting events | — | v0 |
| `providers` | Turn our message format into a provider's API call and back | `Provider` | v0 |
| `interface` | Show events to the user, collect input and approvals | consumes `Event` | v0 |
| `config` | Load and validate settings | — | v0 |
| `tracing` | Record every step of a turn | `Tracer` | v0 |
| `storage` | Persist sessions and metadata | `SessionStore` | v0 |
| `kb` | Ingest, chunk, embed, index, retrieve; manage several knowledge bases | `DocumentParser`, `Embedder`, `VectorStore` | v1 |
| `eval` | Run test sets and compute metrics | — | v1.5 |
| `tools` | Tool registry, schemas, validation, execution | `Tool` | v2 |
| `permissions` | Decide whether an action runs, asks, or is refused | `PermissionPolicy` | v2 |

## 4. The boundary between core and interface

The interface never calls the model or a tool. It sends user input to the core and receives a stream of events. Any front end that can consume this stream can replace the terminal UI.

Events (initial set):

| Event | Meaning |
|---|---|
| `TextDelta` | A piece of streamed answer text |
| `SourcesFound` | Retrieval finished; carries the cited chunks |
| `ToolCallRequested` | The model wants to call a tool with these arguments |
| `PermissionRequired` | The core is waiting for approve / deny / always-allow |
| `ToolStarted`, `ToolFinished` | Execution progress and result summary |
| `TerminalHandoff` | An interactive command needs the real terminal |
| `TurnCompleted` | The turn is done; carries token usage |
| `ErrorRaised` | Something failed; carries a user-facing message |

The interface answers `PermissionRequired` with a `PermissionDecision`. Events are plain data (Pydantic models), so they can later be serialised and sent over a socket without redesign.

## 5. One internal message format

Providers disagree on wire formats. Claude uses content blocks with `tool_use` and `tool_result`; OpenAI-compatible APIs use `tool_calls` and a `tool` role. The core uses one neutral format, and each adapter translates in both directions.

```python
class Message(BaseModel):
    role: Literal["user", "assistant"]
    blocks: list[TextBlock | ToolCallBlock | ToolResultBlock]

class Provider(Protocol):
    name: str
    capabilities: Capabilities   # tool calling, streaming, context window

    def stream(
        self,
        system: str,
        messages: list[Message],
        tools: list[ToolSpec] | None = None,
    ) -> AsyncIterator[ProviderEvent]: ...
```

`Capabilities` matters because models differ. A small local model may not support tool calling reliably, and the core needs to know that instead of failing in confusing ways.

Planned adapters: Anthropic (Claude) and OpenAI-compatible (Groq first; the same adapter should later cover OpenAI, Ollama and other compatible servers by changing the base URL).

## 6. Knowledge base

### Pipeline

```
ingest:    file or pasted text → parse → chunk → embed → store
retrieve:  question → embed → search → top-k chunks (with scores and sources)
```

### Ports

```python
class DocumentParser(Protocol):
    def supports(self, path: Path) -> bool: ...
    def parse(self, path: Path) -> ParsedDocument: ...      # text + metadata

class Embedder(Protocol):
    model_id: str
    dimensions: int
    def embed(self, texts: list[str]) -> list[list[float]]: ...

class VectorStore(Protocol):
    def add(self, chunks: list[Chunk], vectors: list[list[float]]) -> None: ...
    def search(self, vector: list[float], k: int) -> list[ScoredChunk]: ...
    def delete(self, document_id: str) -> None: ...
```

### Choices

- **Embeddings:** a local model through sentence-transformers, starting with a small baseline. The final model is chosen with the evaluation harness. Claude has no embeddings API, so embeddings are independent of the chat provider.
- **Vector search:** in v1, a brute-force cosine search written by hand with NumPy. Later, LanceDB behind the same `VectorStore` port, which also brings keyword-plus-vector hybrid search.
- **Parsing:** plain text and Markdown first, then PDF through pypdf (BSD licence). pymupdf4llm gives better Markdown but is AGPL, so it stays an optional add-on. Docling is a later option for complex layouts.

### On disk

Each knowledge base is a self-contained folder, which makes switching, backing up and deleting simple.

```
~/.local/share/satchel/kbs/<name>/
├── kb.toml      # embedding model, chunk settings, created date
├── sources/     # original files and saved snippets (the source of truth)
└── index/       # chunks and vectors (derived; can always be rebuilt)
```

`kb.toml` records which embedding model built the index. If the configured model differs, Satchel asks for a re-index instead of returning wrong results.

### Commands

```
satchel kb create <name>      satchel kb add <file>...      satchel kb remove <doc>
satchel kb list               satchel kb add --text "..."   satchel kb show [<doc>]
satchel kb use <name>         satchel kb reindex
```

The same operations are available inside a chat as `/kb ...` commands. Both call the same `kb` module.

### Strict mode

Strict mode applies to knowledge answers only, not to actions. It is a combination of four things, and none of them is a hard guarantee alone:

1. A system prompt that restricts answers to the retrieved passages.
2. A retrieval-score threshold: if nothing relevant is found, refuse before calling the model.
3. Required citations in the answer.
4. An explicit refusal path ("that is not in the knowledge base").

How well this works is measured in the evaluation harness (faithfulness and correct-refusal rate).

## 7. Tools and the agent loop (v2)

### The loop

```
1. Build the request: system prompt + environment block + tool specs + conversation
2. Call the provider
3. If the reply contains no tool calls → stream the answer, end the turn
4. For each tool call:
     a. validate arguments against the tool's schema
     b. ask the permission policy: allow / ask the user / deny
     c. execute (or record the denial)
     d. append the result as a tool-result block
5. Go to 2, up to a maximum number of steps
```

The model never executes anything. It only produces a tool name and arguments; Satchel's code validates, asks and executes. Failures (invalid arguments, non-zero exit codes, denials) go back to the model as tool results so it can correct itself or explain.

The **environment block** tells the model what it could not otherwise know: distribution, package manager, shell, working directory, desktop session. It is detected at runtime, never hard-coded.

### Anatomy of a tool

```python
class Tool(Protocol):
    name: str
    description: str                 # when to use it, when not to
    parameters: type[BaseModel]      # Pydantic model → JSON Schema for the provider
    risk: RiskTier                   # default tier; may be raised per call

    async def run(self, args: BaseModel, ctx: ToolContext) -> ToolResult: ...
```

### Core tools

| Tool | Purpose | Default tier |
|---|---|---|
| `search_knowledge_base` | Retrieve passages from the active knowledge base | read-only |
| `read_file` | Read a file | read-only |
| `edit_file` | Replace an exact string in a file; the file must have been read first; a diff is shown | change |
| `write_file` | Create or overwrite a file | change |
| `run_command` | Run a shell command | change, or privileged by rule |

File tools are separate from `run_command` because they are easier to validate, scope and show as diffs than `sed` or `echo >` through a shell.

### Recipes

A recipe is a user-defined tool described in config. It gives the model knowledge it could not have, such as how *this* machine reloads its status bar.

```toml
[[recipe]]
name = "refresh_waybar"
description = "Reload Waybar after its config changes."
command = "killall -SIGUSR2 waybar"

[[recipe]]
name = "install_package"
description = "Install a package from the Arch repos or the AUR."
command = "yay -S {package}"

[recipe.parameters.package]
type = "string"
description = "Exact package name"
```

Each recipe is registered as a tool with a generated schema. Parameter values are shell-escaped before substitution, so a value can never inject extra commands. Recipes go through the same permission tiers as everything else.

### Permissions

| Tier | Examples | Behaviour |
|---|---|---|
| Read-only | `read_file`, `search_knowledge_base`, a short allowlist of commands such as `ls`, `pwd`, `which` | Runs automatically |
| Change | `edit_file`, `write_file`, most commands | Asks first; "always allow" can be remembered per tool or command pattern |
| Privileged or destructive | anything with `sudo`, `rm -r`, package installs, writes outside the allowed paths | Always asks; never remembered |

The tier for a command is decided by rules in Satchel's code, not by the model. Anything unrecognised defaults to asking.

**Scope.** File tools refuse paths outside the working directory unless the user has allowed more (in config or during the session). A shell command cannot be confined by path checks alone, so for `run_command` the protection is the approval step: every command that is not on the read-only allowlist is shown in full before it runs. Real sandboxing (for example bubblewrap or containers) is a later option.

**Passwords.** Satchel never asks for, sees or stores a password. When a command is interactive (a sudo prompt, a confirmation), the core emits `TerminalHandoff`, the command runs attached to the real terminal, the user types what is needed, and the core receives only the exit code and captured output.

**Untrusted text.** Knowledge-base content and command output are data, not instructions. If a document says "run this command", any resulting tool call still passes through the same permission flow. This is the main defence against prompt injection.

**Dry run.** The executor has a dry-run mode that records what would have run without running it. It is used by the evaluation harness and is available to users.

## 8. Tracing and evaluation

Every turn writes a trace: the request sent to the provider, retrieved chunks with scores, each tool call with arguments, permission decisions, results, timings and token counts. Traces are JSON Lines files, one per session.

The evaluation harness replays test sets through the real core and computes:

| Area | Metrics |
|---|---|
| Retrieval | recall@k, mean reciprocal rank |
| Answers | faithfulness to retrieved passages (LLM-judged), correctness against reference answers, correct-refusal rate in strict mode |
| Tool use | tool-selection accuracy, argument correctness, task success, unnecessary-call rate, correct-refusal rate |

Metrics are written by hand first. A comparison against an existing framework such as DeepEval comes later.

## 9. Configuration and data locations

Following the XDG conventions on Linux:

| What | Where |
|---|---|
| Settings and recipes | `~/.config/satchel/config.toml`, `~/.config/satchel/recipes.toml` |
| Knowledge bases, sessions (SQLite) | `~/.local/share/satchel/` |
| Traces | `~/.local/state/satchel/traces/` |
| Downloaded embedding models | `~/.cache/satchel/` |

API keys are read from environment variables, not written to config files.

## 10. Proposed package layout

```
satchel/
├── pyproject.toml
├── src/satchel/
│   ├── core/          # engine, messages, events, prompts
│   ├── providers/     # base port, anthropic, openai_compat
│   ├── kb/            # parsers, chunking, embedders, stores, manager
│   ├── tools/         # registry, builtin tools, recipes, executor
│   ├── permissions/   # tiers, rules, policy
│   ├── storage/       # sessions
│   ├── tracing/
│   ├── config/
│   ├── eval/          # runner, metrics, datasets
│   └── interface/     # cli entry point, terminal UI
├── tests/
├── evals/             # test sets and saved results
└── docs/              # these documents
```

## 11. Cross-cutting rules

- **Async core.** Streaming, the terminal UI and provider SDKs all fit `asyncio`. (Proposed; confirm in v0.)
- **Typed everywhere.** Pydantic models at boundaries, type checking in CI.
- **Tests.** Unit tests for each module with fakes for the ports; a small set of end-to-end tests with a scripted fake provider.
- **Dependencies.** Few, justified in [DECISIONS.md](DECISIONS.md), and pinned with a lockfile.
- **Tooling.** Python 3.12+, uv, ruff, pytest.
- **Distribution.** Installable with `uv tool install` or `pipx`. MIT licence. Linux first.
