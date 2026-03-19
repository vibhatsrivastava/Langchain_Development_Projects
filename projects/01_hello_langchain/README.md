# 01 — Hello LangChain

Minimal working example demonstrating a basic LangChain LCEL chain using an Ollama-hosted LLM.

---

## What This Project Covers

- Loading a model via the shared `common/llm_factory` utility
- Defining a `PromptTemplate`
- Building a simple **LCEL chain**: `prompt | llm | StrOutputParser()`
- Running a single Q&A inference call

---

## How to Run

**1. Ensure the root `.env` is configured:**

```bash
# From the repo root
cp .env.example .env
# Fill in OLLAMA_BASE_URL and OLLAMA_API_KEY
```

**2. Create a virtual environment (from the repo root):**

This isolates the project's dependencies from your global Python installation and other projects.

```bash
python -m venv venv
```

**3. Activate the virtual environment:**

You must activate the environment before installing packages or running the application.

_Windows (PowerShell):_
```powershell
venv\Scripts\Activate.ps1
```

_Windows (Command Prompt):_
```cmd
venv\Scripts\activate.bat
```

_macOS / Linux:_
```bash
source venv/bin/activate
```

Your prompt will show `(venv)` when the environment is active.

**4. Install dependencies:**

```bash
pip install -r requirements-base.txt
pip install -r projects/01_hello_langchain/requirements.txt
```

**5. Run:**

```bash
cd projects/01_hello_langchain
python src/main.py
```

**6. Deactivate when done:**

```bash
deactivate
```

---

## Sample Output

```
2026-03-20 10:00:00 | INFO | __main__ | Initialising LLM...
2026-03-20 10:00:00 | INFO | __main__ | Question: What is LangChain and why is it useful for building AI agents?

--- Response ---
LangChain is an open-source framework that simplifies building applications powered by large language
models (LLMs). It provides abstractions for chaining prompts, tools, memory, and retrieval steps,
making it easy to compose complex agentic workflows without managing low-level API calls directly.
----------------
```

---

## Notes / References

- [LangChain LCEL Docs](https://python.langchain.com/docs/concepts/lcel/)
- [OllamaLLM Integration](https://python.langchain.com/docs/integrations/llms/ollama/)
- To use a different model, set `OLLAMA_MODEL` in your `.env` — see [docs/models.md](../../docs/models.md)
