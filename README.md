# AI-conf

![Language](https://img.shields.io/badge/language-Python-blue)

> No license file included — all rights reserved by default.

## About

AI-conf is a personal experimentation playground for multi-agent LLM "conversations", mostly built around locally-hosted Ollama models (with optional Groq API calls) chatting with each other in a terminal, one taking on a persona and passing a rolling message history to the next. It contains several independent scripts exploring different multi-agent patterns: a free-form three-persona "roundtable" discussion, two "tag team"/"build team" loops where LLM agents write Python code, run it in a spawned terminal window, wait for the human ("Nymo") to approve or reject it, and auto-archive working scripts under descriptive filenames, and two simple single-model chat testers used to compare a local Ollama model's latency against a Groq-hosted model. `agent_workspace/` holds actual scripts these agent loops previously generated and saved (a time checker, a git status checker, a project-snippet manager, a quadratic-equation solver, and a simple calculator) — i.e. real output artifacts of the tool working, not hand-written library code. This is clearly a personal AI/agents learning project, not a packaged product.

## Table of Contents

- [About](#about)
- [Scripts](#scripts)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Security Note](#security-note)
- [Testing](#testing)
- [Author and License](#author-and-license)

## Scripts

| Script | What it does |
|---|---|
| `roundtable.py` | Three local Ollama personas (Thinker `llama3.2:3b`, Coder `qwen2.5-coder:3b`, JSON Guy `llama3.2:1b`) take turns responding to a rolling conversation history, capped at the last 6 messages, looping indefinitely until Ctrl+C |
| `agent_builder.py` | A structured build loop: Thinker (`llama3.2:3b`) plans once, Coder (`qwen2.5-coder:3b`) writes Python wrapped in ` ```python ` blocks and signals `[RUN_TEST]`, the script extracts and runs that code in a spawned `cmd` window, prompts the human for a pass/fail verdict, feeds failures back to the Coder, and on success has an Archivist (`llama3.2:1b`) invent a filename (`[SAVE_AS: name.py]`) to save the script under in `agent_workspace/` |
| `tag_team.py` | A simpler two-agent variant of the same build loop: a single "Elite Solo Developer" (`llama3.1:8b`, local) writes and tests code directly (no separate planning step), then an Archivist (`llama3.2:1b`) names and archives it |
| `tag_team2.py` | Same as `tag_team.py` but routes the Lead Dev role to Groq's `llama-3.3-70b-versatile` over the cloud API instead of a local Ollama model, keeping the Archivist local |
| `tester_1_local.py` | Minimal interactive chat REPL against a local Ollama model (`llama3.1:8b`), printing response latency each turn |
| `tester_2_groq.py` | Same REPL against Groq's `llama-3.3-70b-versatile`, printing latency, for comparing local vs. cloud inference speed |
| `agent_workspace/*.py` | Standalone utility scripts (`Time_Checker.py`, `git_checker.py`, `project_snippet_manager.py`, `quadratic_equation_runner.py`, `simple_calculator.py`) previously produced and archived by the build-loop scripts above |

## Prerequisites

- Python 3
- [Ollama](https://ollama.com/) installed and running locally, with the models referenced by each script pulled (e.g. `ollama pull llama3.2:3b`, `qwen2.5-coder:3b`, `llama3.2:1b`, `llama3.1:8b`)
- Python packages: `ollama`, `groq` (only needed for `tag_team2.py` and `tester_2_groq.py`)
- Windows (the `extract_and_run_code` helper in `agent_builder.py`/`tag_team.py`/`tag_team2.py` spawns a Windows `cmd.exe` window via `start "AI_Test" /wait cmd /c ...` to run generated code — this will not work as-is on macOS/Linux)
- A Groq API key for the Groq-backed scripts

## Installation

```bash
git clone https://github.com/successjoseph/AI-conf.git
cd AI-conf
pip install -r requirements.txt
```

Pull whichever Ollama models the script you intend to run requires, e.g.:

```bash
ollama pull llama3.2:3b
ollama pull qwen2.5-coder:3b
ollama pull llama3.2:1b
ollama pull llama3.1:8b
```

## Configuration

A local, gitignored `.env` at the repo root supplies `GROQ_API_KEY`, read by `tester_2_groq.py` via `python-dotenv`. `tag_team2.py` still expects its own `GROQ_API_KEY` string literal to be filled in directly (it only ever held the placeholder `"YOUR_GROQ_API_KEY_HERE"`, not a real secret, so it was left as-is).

## Usage

Each script is standalone and run directly with Python; all are interactive terminal loops:

```bash
python roundtable.py          # free-form 3-agent discussion, prompts for a starting topic
python agent_builder.py        # 3-agent build loop (Thinker → Coder → tested → Archivist)
python tag_team.py             # 2-agent build loop, fully local
python tag_team2.py            # 2-agent build loop, Lead Dev on Groq
python tester_1_local.py        # single-model chat REPL against local Ollama
python tester_2_groq.py         # single-model chat REPL against Groq
```

`agent_builder.py`, `tag_team.py`, and `tag_team2.py` will pop open a separate terminal window to execute any code the "Coder"/"Lead Dev" persona produces, then ask you in the original terminal whether it worked; approved code is renamed and kept in `agent_workspace/`.

## Security Note

`tester_2_groq.py` previously hardcoded a real-looking `gsk_...` Groq API key directly in source (and injected it into `os.environ` at import time). It has been moved to a gitignored `.env` and now loads via `python-dotenv` instead — but since the key was already committed to git history, it should still be rotated/revoked in the Groq console. `tag_team2.py` only ever held the placeholder string `"YOUR_GROQ_API_KEY_HERE"`, not a real secret, so it was left unchanged.

## Testing

No automated tests are currently included. Verification of generated code happens interactively (the human answers "did it work?" for each script the agents produce).

## Author and License

**Author:** [successjoseph](https://github.com/successjoseph)

**License:** No license file is present in this repository — all rights reserved by default.
