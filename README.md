# Satchel

A terminal assistant that answers from knowledge bases you control and carries out tasks on your machine, with your approval.

The name: a satchel carries what you need. Here that means your knowledge and your tools.

## Status

Early development, working towards v0. **There is nothing to use yet.** The project setup and config loading are done; the chat itself is not. Progress is tracked in the [roadmap](docs/ROADMAP.md).

| Version | Theme | State |
|---|---|---|
| v0 | Skeleton: streaming chat with Claude or Groq | In progress |
| v1 | Answers from switchable knowledge bases, with citations and a strict mode | Planned |
| v1.5 | Evaluation harness for retrieval and answers | Planned |
| v2 | Agent: tools, recipes and permissions | Planned |
| v3 | Extensions | Open |

## What it is for

Satchel is a learning and portfolio project. The agent loop, tool calling, retrieval pipeline and provider adapters are written by hand, with no agent or RAG framework, and quality claims are meant to come from an evaluation harness. The reasoning is in [VISION.md](docs/VISION.md).

It targets Linux first.

## Development

Requires [uv](https://docs.astral.sh/uv/) and Python 3.12 or newer.

```bash
git clone https://github.com/nyanko3434/Satchel.git
cd Satchel
uv sync

uv run satchel --version
uv run satchel config        # show loaded settings and where Satchel keeps files

uv run pytest                # tests
uv run ruff check .          # lint
uv run ruff format --check . # formatting
uv run mypy                  # type check
```

## Configuration

Settings live in `~/.config/satchel/config.toml`. Providers are named entries, and `provider` selects the active one:

```toml
provider = "groq"

[providers.claude]
type = "anthropic"
model = "<model id>"
api_key_env = "ANTHROPIC_API_KEY"

[providers.groq]
type = "openai_compat"
model = "<model id>"
base_url = "https://api.groq.com/openai/v1"
api_key_env = "GROQ_API_KEY"
```

API keys are never written to the config file. `api_key_env` is the name of the environment variable that holds the key. Nothing uses these settings to call a model yet.

## Documentation

- [VISION.md](docs/VISION.md): what Satchel is and why it exists
- [ARCHITECTURE.md](docs/ARCHITECTURE.md): modules, boundaries and data locations
- [ROADMAP.md](docs/ROADMAP.md): what each version contains, and v0 progress
- [DECISIONS.md](docs/DECISIONS.md): the decision log
- [PROJECT_LOG.md](docs/PROJECT_LOG.md): a dated record of work done

## Licence

[MIT](LICENSE)
