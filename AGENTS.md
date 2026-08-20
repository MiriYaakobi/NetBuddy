# NetBuddy - Agent Context (AGENTS.md)

## Build & Run
- Package Manager / Runner: `uv`
- Run Agent Tests: `uv run eval.py`
- Launch Web UI: `uv run streamlit run app.py`

## Project Structure
- `app.py`: Cyberpunk-lilac Streamlit chat interface with optimized short-term memory (`[-4:]`).
- `agent.py`: ReAct agent loop, Groq LLM integration, tool execution, and security guardrails.
- `course_notes.txt`: Local semantic knowledge base powered by ChromaDB RAG.
- `eval.py`: Automated evaluation suite verifying core networking tasks and security.

## Conventions
- Language: Python 3.13 managed via `uv`.
- Code Style: Clean, modular code with professional English comments and docstrings.
- Security & Secrets: Never commit `.env`. Always reference `.env.example` for environment configuration.
