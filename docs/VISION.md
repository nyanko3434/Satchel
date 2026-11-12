# Satchel — Vision

> Status: initial vision, written 2026-11-11. This is a living document; update it when the direction changes.
> Related docs: [ARCHITECTURE.md](ARCHITECTURE.md), [ROADMAP.md](ROADMAP.md), [DECISIONS.md](DECISIONS.md)

## In one sentence

Satchel is a terminal assistant that answers from knowledge bases you control and carries out tasks on your machine, with your approval.

The name: a satchel carries what you need. Here that means your knowledge and your tools.

## Why it exists

Three reasons, in priority order:

1. **Learning.** To understand, by building them, how retrieval-augmented generation works, how an agent decides which tool to call and with which parameters, and how systems like this are evaluated.
2. **Portfolio.** A project with a real architecture, real tests and real evaluation numbers, not a framework demo.
3. **Usefulness.** Something other people can install and use on their own Linux machine.

## What it does

### 1. Answers from a knowledge base

- You keep one or more knowledge bases and switch between them.
- Adding knowledge is easy: text files, Markdown, PDFs, or a pasted snippet of raw text.
- Viewing, adding and removing content is done with simple terminal commands.
- Answers cite the passages they came from.
- **Strict mode** is a toggle. When on, Satchel answers knowledge questions only from the knowledge base and says so when the answer is not there. When off, it may also use the model's general knowledge.

### 2. Carries out tasks

You describe what you want in plain language and Satchel works out what to do:

- "install claude code" → runs the right package-manager command for your system
- "open firefox" → launches the application
- "refresh the waybar" → reloads it
- "change the font size in this config to 12" → edits the file and shows you the diff first

It does this with a small set of general tools (run a command, read a file, edit a file, write a file, search the knowledge base), plus **recipes**: short config entries where you teach it a task it could not know by itself.

### 3. Understands mixed requests

From one prompt, Satchel should be able to tell whether you are:

- asking something its knowledge base can answer,
- asking it to perform a task,
- asking for several things at once, or
- asking for something outside its capabilities, in which case it says so instead of pretending.

### 4. Works with the model you choose

Hosted APIs (Claude and Groq first, then Gemini, OpenAI and others) or a model running locally. Switching is a config change.

## Principles

1. **You stay in control.** Nothing that changes your system runs without your approval. Satchel never sees or stores your password.
2. **Grounded by default.** Knowledge answers show their sources. Strict mode makes "I don't know" an acceptable answer.
3. **The core is ours.** The agent loop, tool calling, retrieval pipeline and provider adapters are written by hand, not imported from an agent framework. Libraries are used only for commodity parts.
4. **Modular.** High cohesion, low coupling. The interface, the model provider, the vector store and the document parser can each be replaced without touching the core.
5. **Measured, not assumed.** Every step is traced, and quality claims come from an evaluation harness.
6. **Small and auditable.** Few dependencies, pinned versions, MIT licence.

## Who it is for

- First: the author, on Arch Linux.
- Then: Linux users who are comfortable in a terminal and want a private, hackable assistant over their own notes and their own machine.
- Later, possibly: other platforms.

## Learning goals

| Topic | Where it is learned |
|---|---|
| RAG: chunking, embeddings, retrieval, grounding | v1 |
| Evaluating RAG: retrieval metrics, faithfulness, refusals | v1.5 |
| Tool calling: schemas, tool selection, parameter filling | v2 |
| Agent loops: multi-step tasks, error recovery, stopping | v2 |
| Safety for agents: permissions, scoping, prompt injection | v2 |
| Evaluating agents: tool accuracy, task success | v2 |
| Software architecture: ports and adapters, clean boundaries | every version |

## Non-goals

- A wrapper around LangChain, LlamaIndex or a similar framework.
- A hosted or multi-user service.
- A web or desktop GUI in the early versions (the architecture leaves room for one).
- Unattended autonomous operation. A person approves actions.
- Windows and macOS support in the first versions.
- Storing or handling credentials.

## What success looks like

- Someone can install Satchel with one command, add their documents, and get cited answers within a few minutes.
- A plain-language request such as "install X" or "edit this file" leads to the correct tool call with correct parameters, shown for approval, and executed correctly.
- The repository contains evaluation results that back up quality claims for both retrieval and tool use.
- A new model provider or a new interface can be added by writing one adapter, with no changes to the core.
- The author can explain every part of the core without looking at the code.

## How the work is split

- **Nayan writes the core himself:** the agent loop, the retrieval pipeline, the provider adapters, the tool-calling path and the evaluation metrics.
- **Claude Code writes the supporting parts:** the terminal interface, command-line plumbing, config loading, document parsers, tests and boilerplate.
- Design decisions are recorded in [DECISIONS.md](DECISIONS.md) before they are implemented.
- Time budget: roughly 15 hours a week, with no fixed deadline.
