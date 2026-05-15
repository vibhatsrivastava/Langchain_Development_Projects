# Playbook Update: .env File Integration

## Summary of Changes

The `playbook_windows.yml` has been updated to **read all configuration from `.env` files** on the Windows target host instead of requiring AWX credentials. This simplifies AWX setup and keeps sensitive configuration on the target machine.

---

## ✅ **What Changed**

### **Before** (AWX Credentials Approach):
- Required creating 3 custom credential types in AWX
- Required creating 3 credential instances with values
- Required attaching credentials to job template
- Configuration duplicated between `.env` files and AWX

### **After** (`.env` File Approach):
- Only requires Windows Machine credential (for authentication)
- Reads all config from `.env` files on target host
- Single source of truth for configuration
- Simpler AWX setup

---

## 🔄 **How It Works**

The playbook now performs these steps:

1. **Load root `.env`** → Reads `C:\Users\<your-username>\Documents\GitHub\Agentic_AI_Development_Framework\.env`
   - Contains: OLLAMA_*, LANGFUSE_*, LOG_LEVEL

2. **Load project `.env`** → Reads `C:\Users\<your-username>\Documents\GitHub\Agentic_AI_Development_Framework\projects\04_github_issue_reporter\.env`
   - Contains: GITHUB_TOKEN, GITHUB_REPO_OWNER, GITHUB_REPO_NAME

3. **Merge with AWX survey values** → Adds runtime parameters:
   - MODE, ISSUE_NUMBER, DRY_RUN, MAX_ISSUES, LOG_LEVEL (override), AWX_JOB_ID

4. **Pass all environment variables** → To Python agent via `environment: "{{ agent_env }}"`

---

## 📋 **Configuration Sources**

| Variable | Source | Example Value |
|----------|--------|---------------|
| `OLLAMA_BASE_URL` | Root `.env` | `http://10.0.0.15:11434` |
| `OLLAMA_API_KEY` | Root `.env` | `your_api_key_here` |
| `OLLAMA_MODEL` | Root `.env` | `gpt-oss:20b` |
| `OLLAMA_EMBEDDING_MODEL` | Root `.env` | `nomic-embed-text` |
| `LANGFUSE_ENABLED` | Root `.env` | `true` |
| `LANGFUSE_PUBLIC_KEY` | Root `.env` | `pk-lf-...` |
| `LANGFUSE_SECRET_KEY` | Root `.env` | `sk-lf-...` |
| `LANGFUSE_HOST` | Root `.env` | `http://10.0.0.15:3000` |
| `GITHUB_TOKEN` | Project `.env` | `github_pat_...` |
| `GITHUB_REPO_OWNER` | Project `.env` | `your_github_username` |
| `GITHUB_REPO_NAME` | Project `.env` | `your_target_repo` |
| `MODE` | AWX Survey | `report` / `issue` / `auto-analyze` |
| `ISSUE_NUMBER` | AWX Survey | `42` |
| `DRY_RUN` | AWX Survey | `true` / `false` |
| `MAX_ISSUES` | AWX Survey | `100` |
| `LOG_LEVEL` | AWX Survey (overrides `.env`) | `INFO` / `DEBUG` |
| `AWX_JOB_ID` | AWX System | `200` |

---

## 🎯 **Benefits**

1. **Simpler AWX Setup**:
   - No need to create custom credential types
   - No need to maintain secrets in AWX vault
   - Only one credential needed (Windows authentication)

2. **Single Source of Truth**:
   - Configuration lives in `.env` files (where it's already needed for local runs)
   - No duplication between `.env` and AWX

3. **Easier Maintenance**:
   - Update `.env` files on target host to change configuration
   - No need to update AWX credentials
   - Consistent behavior between local and AWX execution

4. **Security**:
   - Secrets stay on target host
   - Only Windows authentication credential stored in AWX
   - `.env` files protected by Windows file permissions

---

## 📝 **New Playbook Tasks**

### **Task: Load root .env file**
```yaml
- name: Load root .env file into environment
  ansible.windows.win_shell: |
    # Parse .env file and output as KEY=VALUE
    $rootEnvFile = "{{ repo_root }}\.env"
    if (Test-Path $rootEnvFile) {
      Get-Content $rootEnvFile | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]+)\s*=\s*(.+)\s*$') {
          $name = $matches[1].Trim()
          $value = $matches[2].Trim().Trim("'").Trim('"')
          Write-Output "$name=$value"
        }
      }
    }
  register: root_env_output
```

### **Task: Load project .env file**
```yaml
- name: Load project .env file into environment
  ansible.windows.win_shell: |
    # Parse .env file and output as KEY=VALUE
    $projectEnvFile = "{{ project_dir }}\.env"
    if (Test-Path $projectEnvFile) {
      Get-Content $projectEnvFile | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]+)\s*=\s*(.+)\s*$') {
          $name = $matches[1].Trim()
          $value = $matches[2].Trim().Trim("'").Trim('"')
          Write-Output "$name=$value"
        }
      }
    }
  register: project_env_output
```

### **Task: Parse and merge environment variables**
```yaml
- name: Parse environment variables from .env files
  ansible.builtin.set_fact:
    env_vars: >-
      {{
        (root_env_output.stdout_lines | default([]) + project_env_output.stdout_lines | default([]))
        | select('match', '^[A-Z_]+=.+$')
        | list
      }}

- name: Set agent execution environment variables
  ansible.builtin.set_fact:
    agent_env: >-
      {{
        env_vars | map('regex_replace', '^([^=]+)=(.*)$', '[\1, \2]')
        | map('from_json') | items2dict
        | combine({
          'MODE': mode | default('report'),
          'ISSUE_NUMBER': issue_number | default(''),
          'DRY_RUN': dry_run | default('false'),
          'MAX_ISSUES': max_issues | default('100'),
          'LOG_LEVEL': log_level | default('INFO'),
          'AWX_JOB_ID': tower_job_id | default('')
        })
      }}
```

### **Task: Display loaded configuration (sanitized)**
```yaml
- name: Display loaded environment (sanitized - no secrets)
  ansible.builtin.debug:
    msg: |
      Loaded from .env files:
      - OLLAMA_BASE_URL: {{ agent_env.OLLAMA_BASE_URL | default('not set') }}
      - OLLAMA_MODEL: {{ agent_env.OLLAMA_MODEL | default('not set') }}
      - GITHUB_REPO_OWNER: {{ agent_env.GITHUB_REPO_OWNER | default('not set') }}
      - GITHUB_REPO_NAME: {{ agent_env.GITHUB_REPO_NAME | default('not set') }}
      From AWX survey:
      - MODE: {{ agent_env.MODE }}
      - LOG_LEVEL: {{ agent_env.LOG_LEVEL }}
```

---

## 🔒 **Security Considerations**

1. **Secrets in `.env` files**:
   - Protected by Windows file permissions
   - Only accessible to authorized users
   - Not stored in AWX database

2. **WinRM Connection**:
   - Use HTTPS (port 5986) in production
   - Use certificate-based auth instead of basic auth
   - Restrict WinRM access via firewall

3. **Playbook Output**:
   - Debug task sanitizes output (no GITHUB_TOKEN, API_KEY, or SECRET_KEY shown)
   - Only non-sensitive config displayed

---

## ⚠️ **Important Notes**

1. **`.env` files must exist** on the Windows target before running the playbook
2. **Project `.env` overrides root `.env`** for duplicate keys (hierarchical loading)
3. **AWX survey values override `.env`** for runtime parameters (MODE, LOG_LEVEL, etc.)
4. **Playbook validates** that `.env` files are readable (fails gracefully if missing)

---

## 🧪 **Testing**

After updating to the new playbook, verify:

1. **Run AWX job** with survey:
   - MODE: `report`
   - LOG_LEVEL: `DEBUG`

2. **Check playbook output** for "Display loaded environment" task:
   ```
   TASK [Display loaded environment (sanitized - no secrets)] ********************
   ok: [ServerHost-01] => {
       "msg": "Loaded from .env files:\n- OLLAMA_BASE_URL: http://10.0.0.15:11434\n- OLLAMA_MODEL: gpt-oss:20b\n..."
   }
   ```

3. **Verify agent execution** succeeds with loaded config

---

## 📚 **Updated Documentation**

- ✅ `playbook_windows.yml` - Updated with `.env` loading logic
- ✅ `AWX_WINDOWS_SETUP.md` - Added Step 2.5 for `.env` file verification
- ✅ `QUICK_FIX.md` - Updated credential requirements
- ✅ `ENV_FILE_INTEGRATION.md` - This document (overview and technical details)

---

## 🚀 **Migration Path**

If you already set up AWX with custom credentials:

1. **Keep existing setup** - Old playbook still works
2. **Or migrate to `.env` approach**:
   - Update job template playbook to `playbook_windows.yml`
   - Remove Ollama/GitHub/Langfuse credentials from job template
   - Keep only Machine credential
   - Ensure `.env` files exist on target with all values
   - Test with `MODE=report` first

**Both approaches are supported** - use whichever fits your workflow better.
