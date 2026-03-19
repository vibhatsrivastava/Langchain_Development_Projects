# Prerequisites

Ensure the following are in place before running any project in this repo.

---

## 1. Python

**Version:** Python 3.10 or higher

```bash
python --version    # should print 3.10+
```

Download from [https://www.python.org/downloads/](https://www.python.org/downloads/).

---

## 2. Ollama Access

Choose one of the following:

### Option A — Remote Hosted Server (Default)

- Request the **server URL** and **API key** from your admin.
- Verify access:

  ```bash
  curl -H "Authorization: Bearer your_api_key_here" https://your-ollama-server.example.com/api/tags
  ```

  A successful response returns a JSON object listing available models.

### Option B — Local Ollama Installation

- Download and install from [https://ollama.com/download](https://ollama.com/download)
- Verify installation:

  ```bash
  ollama --version
  curl http://localhost:11434/api/tags    # should return a JSON response
  ```

---

## 3. RAM / Hardware (Local Ollama Only)

Running large models locally requires sufficient memory:

| Model Size | Minimum RAM | Recommended RAM |
|-----------|------------|----------------|
| 1B–3B | 4 GB | 8 GB |
| 7B–8B | 8 GB | 16 GB |
| 13B–14B | 12 GB | 16 GB |
| 20B+ | 16 GB | 24 GB+ |

**GPU Acceleration (Optional):**
- NVIDIA GPU: Ollama auto-detects CUDA. Install the [CUDA Toolkit](https://developer.nvidia.com/cuda-downloads).
- Apple Silicon (M1/M2/M3): GPU acceleration is enabled by default via Metal.
- Inference will fall back to CPU if no GPU is detected.

---

## 4. Git

```bash
git --version
```

Download from [https://git-scm.com/](https://git-scm.com/) if not installed.

---

## 5. pip / Virtual Environment

Using a virtual environment per project is **strongly recommended**. It isolates each project's dependencies so packages installed for one project cannot conflict with those of another, and keeps your global Python installation clean.

### Verify pip is available

```bash
pip --version
```

### Create a virtual environment

Run the following from the **repo root** (or from inside a specific project folder if you prefer a project-scoped env):

```bash
python -m venv venv
```

This creates a `venv/` directory that holds an isolated Python interpreter and package tree.

> The `venv/` directory is listed in `.gitignore` and will never be committed.

### Activate the virtual environment

You must activate the environment **before** installing packages or running any script.

**Windows (PowerShell):**
```powershell
venv\Scripts\Activate.ps1
```

**Windows (Command Prompt / cmd.exe):**
```cmd
venv\Scripts\activate.bat
```

**macOS / Linux:**
```bash
source venv/bin/activate
```

Once activated, your shell prompt will be prefixed with `(venv)`, confirming the environment is active.

### Deactivate when done

```bash
deactivate
```
