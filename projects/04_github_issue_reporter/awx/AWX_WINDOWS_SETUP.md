# AWX Configuration Guide for Windows Remote Execution

## Quick Fix for Your Current Setup

Your AWX job is failing because it's trying to run Linux commands on a Windows target. Here's how to fix it:

---

## ✅ **Step 1: Update AWX Inventory Host Variables**

**Navigate to**: AWX UI → Resources → Inventories → [Your Inventory] → Hosts → `ServerHost-01`

**Set these host variables** (YAML format):

```yaml
# Connection settings for Windows via psrp/WinRM
ansible_connection: psrp
ansible_psrp_protocol: http  # Change to 'https' if using SSL
ansible_psrp_auth: basic     # Or 'ntlm', 'negotiate', 'kerberos'
ansible_port: 5985           # Or 5986 for HTTPS
ansible_psrp_cert_validation: ignore  # Optional: if using self-signed certs

# CRITICAL: Disable Python interpreter discovery on Windows target
ansible_python_interpreter: auto_silent

# Windows credentials (or use a Machine credential attached to job template)
ansible_user: Administrator
ansible_password: !vault |
  $ANSIBLE_VAULT;1.1;AES256
  [encrypted_password]

# Optional: Connection timeout settings
ansible_psrp_connection_timeout: 30
ansible_psrp_read_timeout: 60
```

**Alternative**: Instead of storing password in host vars, attach a **Machine Credential** to the job template with Windows credentials.

---

## ✅ **Step 2: Update AWX Job Template**

**Navigate to**: AWX UI → Resources → Templates → [Your Job Template]

### **Update These Fields**:

1. **Playbook**: Change to:
   ```
   projects/04_github_issue_reporter/awx/playbook_windows.yml
   ```
   *(This playbook reads configuration from `.env` files on the Windows target)*

2. **Credentials**: Attach **only** this credential:
   - ✅ **Machine Credential** (for Windows authentication) - **REQUIRED**
   
   **Note**: ~~You no longer need~~ Ollama/GitHub/Langfuse credentials in AWX. The playbook now reads all configuration from `.env` files on ServerHost-01:
   - Root `.env`: `C:\Users\<your-username>\Documents\GitHub\Agentic_AI_Development_Framework\.env`
   - Project `.env`: `C:\Users\<your-username>\Documents\GitHub\Agentic_AI_Development_Framework\projects\04_github_issue_reporter\.env`

3. **Options**:
   - ✅ **Enable Privilege Escalation**: OFF (not needed for Windows)
   - ✅ **Enable Concurrent Jobs**: Your choice

4. **Extra Variables** (if your project path is different):
   ```yaml
   # Only add these if your paths differ from defaults
   project_dir: "C:/Users/<your-username>/Documents/GitHub/Agentic_AI_Development_Framework/projects/04_github_issue_reporter"
   repo_root: "C:/Users/<your-username>/Documents/GitHub/Agentic_AI_Development_Framework"
   ```

---

## ✅ **Step 2.5: Ensure .env Files Exist on Windows Target** ✨ NEW

The playbook now loads configuration from `.env` files on the Windows target. **Verify these files exist**:

**On ServerHost-01**, check:

```powershell
# Root .env file (common variables)
Test-Path "C:\Users\<your-username>\Documents\GitHub\Agentic_AI_Development_Framework\.env"
# Should return: True

# Project .env file (GitHub-specific variables)
Test-Path "C:\Users\<your-username>\Documents\GitHub\Agentic_AI_Development_Framework\projects\04_github_issue_reporter\.env"
# Should return: True
```

**Required variables in root `.env`**:
```bash
OLLAMA_BASE_URL=http://10.0.0.15:11434
OLLAMA_API_KEY=your_key_here
OLLAMA_MODEL=gpt-oss:20b
LANGFUSE_ENABLED=true
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_HOST=http://10.0.0.15:3000
LOG_LEVEL=INFO
```

**Required variables in project `.env`**:
```bash
GITHUB_TOKEN=github_pat_...
GITHUB_REPO_OWNER=your_github_username
GITHUB_REPO_NAME=your_target_repo
```

If files are missing, copy from `.env.example` templates and configure with your values.

---

## ✅ **Step 3: Create Windows Machine Credential**

**Navigate to**: AWX UI → Resources → Credentials → Add

**Configure**:
- **Name**: `Windows - ServerHost-01 Admin`
- **Credential Type**: `Machine`
- **Username**: `Administrator` (or your Windows user)
- **Password**: `[your_windows_password]`
- **Privilege Escalation Method**: Leave blank (not needed for Windows)

**Attach this credential** to your job template (in addition to Ollama/GitHub credentials).

---

## ✅ **Step 4: Verify Windows Remote Management (WinRM)**

Before running the AWX job, ensure WinRM is enabled on ServerHost-01:

### **On ServerHost-01 (Windows target), run PowerShell as Administrator**:

```powershell
# Enable WinRM
Enable-PSRemoting -Force

# Configure WinRM for basic auth (if using basic)
Set-Item WSMan:\localhost\Service\Auth\Basic -Value $true

# Allow unencrypted traffic (only for HTTP, not recommended for production)
Set-Item WSMan:\localhost\Service\AllowUnencrypted -Value $true

# Add AWX server to trusted hosts (replace with your AWX server IP)
Set-Item WSMan:\localhost\Client\TrustedHosts -Value "your-awx-server-ip" -Force

# Verify WinRM listener is running
Get-WSManInstance -ResourceURI winrm/config/listener -Enumerate

# Test from AWX server (run this from AWX execution node)
# Test-WSMan -ComputerName your-target-ip -Port 5985
```

### **For Production: Use HTTPS with Certificate**

```powershell
# Generate self-signed certificate for WinRM HTTPS
$cert = New-SelfSignedCertificate -DnsName "ServerHost-01" -CertStoreLocation Cert:\LocalMachine\My

# Create HTTPS WinRM listener
New-WSManInstance -ResourceURI winrm/config/Listener -SelectorSet @{Address="*";Transport="HTTPS"} -ValueSet @{Hostname="ServerHost-01";CertificateThumbprint=$cert.Thumbprint}

# Update AWX inventory to use HTTPS (port 5986)
```

---

## ✅ **Step 5: Test AWX Connection**

Before running the full job template, test the connection:

### **Create a test playbook** in AWX:

```yaml
---
- name: Test Windows Connection
  hosts: ServerHost-01
  gather_facts: false
  vars:
    ansible_python_interpreter: auto_silent
  
  tasks:
    - name: Ping Windows host
      ansible.windows.win_ping:
      
    - name: Get Windows version
      ansible.windows.win_shell: |
        $PSVersionTable.PSVersion
        Get-ComputerInfo | Select-Object WindowsVersion, OsArchitecture
      register: win_info
      
    - name: Display Windows info
      ansible.builtin.debug:
        var: win_info.stdout
```

**Create a test job template** with this playbook and run it. If successful, proceed to the main agent job.

---

## ✅ **Step 6: Run Your Agent Job**

1. **Navigate to**: Job Templates → [GitHub Issue Reporter - Run Agent]
2. **Click**: Launch
3. **Fill survey**:
   - **Execution Mode**: `report`
   - **Log Level**: `DEBUG` (for first run)
4. **Click**: Next → Launch
5. **Monitor output** in real-time

---

## 📋 **What Changed in the New Playbook**

| Old Playbook (Linux-focused) | New Playbook (Windows-compatible) |
|------------------------------|-----------------------------------|
| `ansible.builtin.stat` | `ansible.windows.win_stat` |
| `ansible.builtin.command` | `ansible.windows.win_shell` with PowerShell |
| Direct Python execution | Activate venv first, then run Python |
| Linux paths (`/runner/...`) | Windows paths (`C:/Users/...`) |
| No Python interpreter setting | `ansible_python_interpreter: auto_silent` |

---

## 🔍 **Expected Output After Fix**

```
TASK [Verify project virtual environment exists] *******************************
ok: [ServerHost-01]

TASK [Verify Python executable exists in venv] *********************************
ok: [ServerHost-01]

TASK [Execute GitHub Issue Reporter agent via AWX wrapper (Windows PowerShell)] 
changed: [ServerHost-01]

TASK [Parse agent output as JSON] **********************************************
ok: [ServerHost-01]

TASK [Display agent execution result] ******************************************
ok: [ServerHost-01] => {
    "msg": "Status: success\nResult: **Open Issues Report**\n...\nExecution Time: 15.2s\nAWX Job ID: 200"
}

PLAY RECAP *********************************************************************
ServerHost-01              : ok=5    changed=1    unreachable=0    failed=0
```

---

## 🚨 **Troubleshooting Common Issues**

### **Issue: "WinRM connection failed"**

**Error**: `Failed to connect to the host via winrm`

**Fix**:
1. Verify WinRM is enabled on target: `winrm enumerate winrm/config/listener`
2. Check firewall allows port 5985/5986
3. Verify AWX server can reach target: `Test-NetConnection your-target-ip -Port 5985`
4. Check credentials are correct

---

### **Issue: "Access is denied"**

**Error**: `401 Unauthorized` or `Access is denied`

**Fix**:
1. Verify Windows user has Administrator privileges
2. Check UAC settings on target host
3. Try using domain credentials instead of local account
4. Enable basic auth in WinRM: `Set-Item WSMan:\localhost\Service\Auth\Basic -Value $true`

---

### **Issue: "Virtual environment not found"**

**Error**: `Virtual environment not found at C:/Users/.../04_github_issue_reporter/.venv`

**Fix**:
1. **On ServerHost-01**, verify the venv exists:
   ```powershell
   Test-Path "C:\Users\<your-username>\Documents\GitHub\Agentic_AI_Development_Framework\projects\04_github_issue_reporter\.venv"
   ```
2. If missing, create it:
   ```powershell
   cd "C:\Users\<your-username>\Documents\GitHub\Agentic_AI_Development_Framework\projects\04_github_issue_reporter"
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install uv
   uv pip install -e ../../../common
   uv pip install -r requirements.txt
   ```
3. Update AWX job template extra-vars if path is different

---

### **Issue: "Python module 'common.awx_wrapper' not found"**

**Error**: `ModuleNotFoundError: No module named 'common.awx_wrapper'`

**Fix**:
1. Verify `common` package is installed in the venv:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   python -c "import common; print(common.__file__)"
   ```
2. If not found, install it:
   ```powershell
   cd C:\Users\<your-username>\Documents\GitHub\Agentic_AI_Development_Framework
   .venv\Scripts\Activate.ps1
   pip install -e ./common
   ```
3. Verify `awx_wrapper.py` exists:
   ```powershell
   Test-Path "C:\Users\<your-username>\Documents\GitHub\Agentic_AI_Development_Framework\common\awx_wrapper.py"
   ```

---

### **Issue: "pypsrp version warning"**

**Warning**: `ansible_psrp_transport is unsupported by the current psrp version installed`

**Fix** (on AWX execution node):
```bash
pip install --upgrade pypsrp>=0.8.0
# Then restart AWX services
```

---

## 📝 **Checklist Before Running**

- [ ] WinRM enabled on ServerHost-01
- [ ] Firewall allows port 5985 (HTTP) or 5986 (HTTPS)
- [ ] AWX inventory has correct host variables (with `ansible_python_interpreter: auto_silent`)
- [ ] Machine credential created with Windows admin credentials
- [ ] Job template updated to use `playbook_windows.yml`
- [ ] All credentials attached to job template
- [ ] Virtual environment exists on ServerHost-01
- [ ] `common` package installed in venv
- [ ] Project synced in AWX (if using Git SCM)
- [ ] Survey configured (or ready to fill when launching)

---

## 🎯 **Summary**

**The core issue**: AWX (Linux controller) was trying to use Linux commands/modules on a Windows target, causing Python interpreter discovery to fail.

**The fix**: Use Windows-specific Ansible modules (`ansible.windows.*`) and disable Python interpreter discovery on the Windows target by setting `ansible_python_interpreter: auto_silent`.

**Files created**:
- ✅ `playbook_windows.yml` - Windows-compatible playbook
- ✅ `AWX_WINDOWS_SETUP.md` - This configuration guide

**Next step**: Update your AWX job template to use the new playbook and inventory settings, then re-run the job.
