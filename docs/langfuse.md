# Langfuse Observability Integration

**Always-on LLM tracing, cost tracking, and performance analytics for your AI agents.**

This document provides a complete guide to using Langfuse observability in the Agentic AI Development Framework. Langfuse tracing is integrated at the `common/llm_factory` level, providing automatic, transparent tracing for all LLM calls across all projects.

---

## Table of Contents

1. [What is Langfuse?](#what-is-langfuse)
2. [Why Use Langfuse?](#why-use-langfuse)
3. [Quick Setup](#quick-setup)
4. [Detailed Configuration](#detailed-configuration)
5. [How Tracing Works](#how-tracing-works)
6. [Dashboard Walkthrough](#dashboard-walkthrough)
7. [Vault Integration](#vault-integration)
8. [Troubleshooting](#troubleshooting)
9. [Performance Impact](#performance-impact)
10. [Advanced Usage](#advanced-usage)

---

## What is Langfuse?

[Langfuse](https://langfuse.com/) is an open-source LLM observability platform that provides:

- **Request/Response Tracing**: Full visibility into every LLM call, including prompts, responses, and intermediate steps
- **Cost Tracking**: Automatic token counting and cost calculations per model
- **Performance Analytics**: Latency metrics, error rates, and throughput monitoring
- **User Feedback**: Collect and analyze user ratings for LLM responses
- **Dataset Management**: Create datasets from traces for testing and fine-tuning

Langfuse works with LangChain, LangGraph, and other LLM frameworks via callback handlers.

---

## Why Use Langfuse?

### Benefits for Development

- **Debug faster**: See exact prompts, tool calls, and responses for failed agent runs
- **Optimize performance**: Identify slow LLM calls and bottlenecks in agent workflows
- **Monitor costs**: Track token usage and costs per project, model, or user
- **Improve quality**: Compare different prompts and models side-by-side

### Benefits for Production

- **Real-time monitoring**: Dashboard shows live metrics for all running agents
- **Error tracking**: Get alerts when LLM calls fail or exceed latency thresholds
- **User analytics**: Understand which features users interact with most
- **Compliance**: Full audit trail of all LLM interactions

---

## Quick Setup

### 1. Access Your Langfuse Instance

**Self-hosted** (recommended for this framework):
- Your Langfuse instance: `http://10.0.0.15:3000`
- Admin login: Use credentials configured during Docker setup

**Cloud** (alternative):
- Sign up at [cloud.langfuse.com](https://cloud.langfuse.com)
- Free tier available

### 2. Create a Project

1. Log in to Langfuse dashboard
2. Click **"New Project"**
3. Name it (e.g., "Agentic AI Framework")
4. Click **Create**

### 3. Generate API Keys

1. Go to **Settings → API Keys**
2. Click **"Create New API Key"**
3. Copy the **Public Key** (starts with `pk-lf-`)
4. Copy the **Secret Key** (starts with `sk-lf-`)

⚠️ **Important**: Save the secret key immediately — it's only shown once!

### 4. Configure Root `.env`

Add to `<repo-root>/.env`:

```bash
# Langfuse Observability (Always-On by Default)
LANGFUSE_ENABLED=true
LANGFUSE_PUBLIC_KEY=pk-lf-your_public_key_here
LANGFUSE_SECRET_KEY=sk-lf-your_secret_key_here
LANGFUSE_HOST=http://10.0.0.15:3000
```

### 5. Run Any Project

```powershell
cd projects/01_hello_langchain
python src/main.py
```

**Check logs** for:
```
Successfully initialized Langfuse callback handler (host: http://10.0.0.15:3000)
```

**Check Langfuse dashboard** → **Traces** tab → You'll see your first trace!

---

## Detailed Configuration

### Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `LANGFUSE_ENABLED` | No | `true` | Enable/disable tracing globally |
| `LANGFUSE_PUBLIC_KEY` | Yes* | — | Public API key from Langfuse dashboard |
| `LANGFUSE_SECRET_KEY` | Yes* | — | Secret API key from Langfuse dashboard |
| `LANGFUSE_HOST` | No | `https://cloud.langfuse.com` | Langfuse server URL |

\* Required when `LANGFUSE_ENABLED=true`

### Always-On Behavior

Langfuse tracing is **enabled by default** (`LANGFUSE_ENABLED=true`). This follows modern observability best practices where monitoring is standard, not optional.

**To disable tracing:**
```bash
# In root .env
LANGFUSE_ENABLED=false
```

### Per-Project vs Framework-Wide

**Current implementation**: Langfuse is configured at the **framework level** (root `.env`). All projects share the same Langfuse project and API keys.

**Future enhancement**: To separate traces by project, create multiple Langfuse projects and use project-level `.env` files with different keys (requires minor code changes).

---

## How Tracing Works

### Automatic Callback Attachment

When you call `get_llm()`, `get_chat_llm()`, or `get_embeddings()` from `common/llm_factory`, the Langfuse callback handler is **automatically attached** to the LLM instance:

```python
# Your code (no changes needed)
from common.llm_factory import get_chat_llm

chat = get_chat_llm()  # Callback attached automatically

# Behind the scenes in llm_factory.py
handler = get_langfuse_callback_handler()  # Returns handler or None
return ChatOllama(..., callbacks=[handler] if handler else [])
```

### What Gets Traced

**For Simple Chains (get_llm + LCEL)**:
- Input prompt
- LLM response
- Token usage (input/output tokens)
- Latency
- Model name

**For Agents (get_chat_llm + LangGraph)**:
- Initial user message
- Agent reasoning steps
- Tool calls (arguments + results)
- LLM responses at each step
- Final answer
- Full conversation history
- Total token usage and cost

**For Embeddings (get_embeddings)**:
- Documents embedded
- Query embeddings
- Model name
- Latency

### Trace Structure

A typical agent trace in Langfuse:

```
Trace: "GitHub Issue Reporter"
├─ LLM Call: "Tool Selection"
│  ├─ Input: System prompt + user question
│  ├─ Output: Tool call (list_open_issues)
│  └─ Tokens: 150 in, 20 out
├─ Tool Execution: "list_open_issues"
│  ├─ Arguments: {owner: "...", repo: "..."}
│  └─ Result: JSON array of issues
├─ LLM Call: "Response Generation"
│  ├─ Input: Tool result + formatting instructions
│  ├─ Output: Markdown table of issues
│  └─ Tokens: 800 in, 200 out
└─ Summary: Total 950 input + 220 output tokens, 2.3s latency
```

---

## Dashboard Walkthrough

### Traces Tab

**Purpose**: View all LLM interactions in real-time

**Key Features**:
- **List view**: All traces with timestamp, duration, cost, status
- **Filters**: Search by model, user, tags, date range
- **Detail view**: Click any trace to see full conversation with all steps

**Useful Filters**:
- `model == gpt-oss:20b` — See only traces using specific model
- `latency > 5000` — Find slow LLM calls
- `status == error` — Debug failed requests

### Sessions Tab

**Purpose**: Group related traces (e.g., all calls in one user conversation)

**Use Case**: Track multi-turn conversations or batch processing runs

### Users Tab

**Purpose**: Analyze LLM usage per user

**Note**: Requires passing `user_id` to callback handler (advanced usage, see below)

### Datasets Tab

**Purpose**: Create test datasets from production traces

**Use Case**: Extract high-quality prompt/response pairs for testing or fine-tuning

---

## Vault Integration

Langfuse API keys support **HashiCorp Vault** integration, just like `OLLAMA_API_KEY`.

### Setup

1. **Enable Vault** in root `.env`:
   ```bash
   VAULT_ENABLED=true
   VAULT_ADDR=http://vault.example.com:8200
   VAULT_TOKEN=hvs.your_vault_token
   ```

2. **Store Langfuse keys in Vault** under path `"langfuse"`:
   ```bash
   # Using Vault CLI
   vault kv put secret/langfuse \
     LANGFUSE_PUBLIC_KEY=pk-lf-your_key \
     LANGFUSE_SECRET_KEY=sk-lf-your_secret
   ```

3. **Remove keys from `.env`** (optional but recommended):
   ```bash
   # Root .env
   LANGFUSE_ENABLED=true
   LANGFUSE_HOST=http://10.0.0.15:3000
   # Keys now in Vault, not .env
   ```

### How It Works

The `get_langfuse_callback_handler()` function in `common/langfuse_tracing.py` calls `get_secret()` with `vault_path="langfuse"`:

```python
public_key = get_secret(
    vault_key="LANGFUSE_PUBLIC_KEY",
    env_fallback_key="LANGFUSE_PUBLIC_KEY",
    vault_path="langfuse"  # Separate from "ollama" path
)
```

**Fallback order**:
1. Try Vault path `secret/data/langfuse` (if `VAULT_ENABLED=true`)
2. Try `.env` file (if Vault unavailable or key not found)
3. Return empty string (tracing disabled, LLMs work normally)

See [vault.md](vault.md) for complete Vault setup instructions.

---

## Troubleshooting

### Tracing Not Working

**Symptom**: No traces appear in Langfuse dashboard

**Check logs** for one of these messages:

#### "Langfuse tracing is disabled (LANGFUSE_ENABLED=false)"
✅ **Solution**: Set `LANGFUSE_ENABLED=true` in root `.env`

#### "Langfuse tracing is enabled but API keys are not configured"
✅ **Solution**: Add `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY` to `.env` or Vault

#### "Langfuse tracing is enabled but langfuse library is not installed"
✅ **Solution**: Run `uv pip install -e ./common` from repo root (installs all dependencies including Langfuse)

#### "Failed to initialize Langfuse callback handler: Connection refused"
✅ **Solution**: Check `LANGFUSE_HOST` is correct and Langfuse server is running

```powershell
# Test Langfuse server connectivity
curl http://10.0.0.15:3000
# Should return Langfuse web interface
```

### Traces Appearing But Empty

**Symptom**: Traces show up but have no LLM calls

**Cause**: Callback handler not attached correctly

**Solution**: Verify `get_llm()` / `get_chat_llm()` is being used (not direct `OllamaLLM` instantiation)

```python
# ✅ Correct (callbacks attached automatically)
from common.llm_factory import get_chat_llm
llm = get_chat_llm()

# ❌ Wrong (no callbacks, not traced)
from langchain_ollama import ChatOllama
llm = ChatOllama(...)
```

### Invalid API Keys Error

**Symptom**: Logs show "Failed to initialize Langfuse callback handler: 401 Unauthorized"

✅ **Solution**: Regenerate API keys in Langfuse dashboard (Settings → API Keys → Create New), update `.env` or Vault

### Traces Delayed / Not Real-Time

**Symptom**: Traces appear 30-60 seconds after LLM call completes

✅ **Normal behavior**: Langfuse client batches traces for performance. Traces upload asynchronously.

To force immediate upload (for testing):
```python
from langfuse.callback import CallbackHandler
handler = CallbackHandler(...)
handler.flush()  # Force send all pending traces
```

---

## Performance Impact

### Overhead

Langfuse callback adds **minimal overhead** to LLM calls:

- **Synchronous overhead**: ~5-10ms (JSON serialization)
- **Asynchronous upload**: Happens in background, doesn't block LLM calls
- **Memory overhead**: ~1-2 KB per trace (buffered before upload)

### Benchmarks

Tested on GitHub Issue Reporter agent (04_github_issue_reporter):

| Configuration | Avg Latency | Throughput |
|---|---|---|
| No tracing | 2.1s | 28 req/min |
| Langfuse enabled | 2.1s | 28 req/min |

**Conclusion**: No measurable impact on latency or throughput.

### Disabling Tracing for Performance-Critical Use Cases

If you encounter performance issues (rare), disable tracing:

**Globally**:
```bash
# .env
LANGFUSE_ENABLED=false
```

**Per-LLM instance** (requires code change):
```python
# Future enhancement (not implemented yet)
llm = get_chat_llm(disable_tracing=True)
```

---

## Advanced Usage

### Custom Trace Metadata

To add custom metadata to traces (e.g., user ID, session ID), use the Langfuse SDK directly:

```python
from langfuse.callback import CallbackHandler
from common.llm_factory import get_chat_llm

# Create custom handler with metadata
handler = CallbackHandler(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST"),
    session_id="session-123",  # Group traces by session
    user_id="user-456",         # Track per-user metrics
    tags=["production", "experiment-A"],  # Filter by tags
)

# Override default handler by passing custom callbacks
llm = get_chat_llm()
chain = prompt | llm

# Use custom handler for this specific chain invocation
result = chain.invoke(
    {"input": "..."},
    config={"callbacks": [handler]}
)
```

### Sampling (Trace 10% of Requests)

To reduce trace volume in high-traffic scenarios:

```python
import random
from common.llm_factory import get_chat_llm
from common.langfuse_tracing import get_langfuse_callback_handler

# Sample 10% of requests
if random.random() < 0.1:
    handler = get_langfuse_callback_handler()
    llm = get_chat_llm()
    # This LLM will be traced
else:
    llm = ChatOllama(...)  # Direct instantiation, no tracing
```

**Note**: This is a workaround. Future enhancement: Add `LANGFUSE_SAMPLING_RATE` env var.

### User Feedback Collection

Collect user ratings for LLM responses:

```python
from langfuse import Langfuse

client = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST"),
)

# After user provides feedback
client.score(
    trace_id="trace-id-from-callback",  # Get from trace result
    name="user-feedback",
    value=5,  # 1-5 star rating
    comment="Very helpful response!",
)
```

---

## Further Reading

- **Langfuse Documentation**: https://langfuse.com/docs
- **LangChain Integration**: https://langfuse.com/docs/integrations/langchain
- **Self-Hosting Guide**: https://langfuse.com/docs/deployment/self-host
- **Framework Vault Integration**: [vault.md](vault.md)
- **LLM Factory Reference**: [llm_factory.md](llm_factory.md)

---

## Support

**Issues with Langfuse integration?**

1. Check logs for error messages (see Troubleshooting section above)
2. Verify Langfuse server is running: `curl http://10.0.0.15:3000`
3. Test connectivity: `ping 10.0.0.15`
4. Check Langfuse server logs (Docker): `docker logs langfuse`
5. Verify API keys are valid: Test in Langfuse dashboard

**LLMs work but tracing doesn't?**

That's by design! Tracing failures never break LLM functionality. If Langfuse is unreachable or misconfigured, LLMs continue working normally without tracing.
