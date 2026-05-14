# 🚨 IMMEDIATE FIX REQUIRED - Quick Action Summary

## Your Current Situation

- ✅ AWX Controller: Linux (running Ansible)
- ✅ Target Host: **ServerHost-01** (Windows at `your-target-ip`)
- ✅ Project Location: `C:\Users\<your-username>\Documents\GitHub\Agentic_AI_Development_Framework`
- ✅ Virtual Environment: `.venv` exists in project directory
- ❌ Current Issue: AWX trying to use Linux commands on Windows target

---

## 🎯 **3 Required Actions in AWX**

### **Action 1: Update Inventory Host Variables** ⚡ CRITICAL

**Navigate to**: AWX UI → Resources → Inventories → [Your Inventory] → Hosts → `ServerHost-01`

**Click "Edit"** and set these host variables (YAML format):

```yaml
ansible_connection: psrp
ansible_psrp_protocol: http
ansible_psrp_auth: basic
ansible_port: 5985
ansible_python_interpreter: auto_silent  # ← This fixes the Python discovery error
ansible_psrp_cert_validation: ignore
```

Click **Save**.

---

### **Action 2: Update Job Template Playbook Path** ⚡ CRITICAL

**Navigate to**: AWX UI → Resources → Templates → [Your Job Template]

**Click "Edit"** and change:

- **Playbook**: From `AI-Agent-Trigger-Playbook.yml` to:
  ```
  projects/04_github_issue_reporter/awx/playbook_windows.yml
  ```

**IMPORTANT**: This playbook now reads configuration from `.env` files on the Windows target instead of AWX credentials. Ensure both `.env` files exist:
- Root: `C:\Users\<your-username>\Documents\GitHub\Agentic_AI_Development_Framework\.env`
- Project: `C:\Users\<your-username>\Documents\GitHub\Agentic_AI_Development_Framework\projects\04_github_issue_reporter\.env`

Click **Save**.

---

### **Action 3: Attach Windows Machine Credential** ⚡ REQUIRED

**Note**: With the updated playbook, you **no longer need** Ollama/GitHub/Langfuse credentials in AWX - they're read from `.env` files. You only need the Windows authentication credential.

**First, create the credential**:

1. **Navigate to**: AWX UI → Resources → Credentials → Add
2. **Configure**:
   - **Name**: `Windows - ServerHost-01`
   - **Credential Type**: `Machine`
   - **Username**: `Administrator` (or your Windows username)
   - **Password**: `[your_windows_password]`
3. Click **Save**

**Then, attach it to job template**:

1. **Navigate to**: AWX UI → Resources → Templates → [Your Job Template] → Edit
2. **Credentials section**: Click **+** and add `Windows - ServerHost-01`
3. **Remove any Ollama/GitHub/Langfuse credentials** (not needed anymore)
4. Click **Save**

---

## ✅ **Verify Windows Prerequisites** (On ServerHost-01)

Before running the AWX job, ensure WinRM is enabled on ServerHost-01:

**Run this PowerShell script as Administrator on ServerHost-01**:

```powershell
# Enable WinRM
Enable-PSRemoting -Force

# Configure for basic auth
Set-Item WSMan:\localhost\Service\Auth\Basic -Value $true

# Allow unencrypted (for HTTP on port 5985)
Set-Item WSMan:\localhost\Service\AllowUnencrypted -Value $true

# Add AWX server to trusted hosts (replace with your AWX server IP)
$awxServerIP = "your-awx-server-ip"  # ← Replace with actual AWX server IP
Set-Item WSMan:\localhost\Client\TrustedHosts -Value $awxServerIP -Force

# Verify WinRM is listening
Get-WSManInstance -ResourceURI winrm/config/listener -Enumerate

# Test locally
Test-WSMan -ComputerName localhost
```

---

## 🧪 **Test the Fix**

After completing the 3 actions:

1. **Navigate to**: AWX UI → Templates → [Your Job Template]
2. **Click**: Launch
3. **Fill survey**:
   - **Execution Mode**: `report`
   - **Log Level**: `DEBUG`
4. **Click**: Next → Launch
5. **Watch for these successful tasks**:
   - ✅ `Verify project virtual environment exists` → **ok**
   - ✅ `Verify Python executable exists in venv` → **ok**
   - ✅ `Execute GitHub Issue Reporter agent` → **changed**
   - ✅ `Parse agent output as JSON` → **ok**
   - ✅ `Display agent execution result` → **ok** (shows JSON with status: success)

---

## 📋 **Expected Successful Output**

```
TASK [Verify project virtual environment exists] *******************************
ok: [ServerHost-01]

TASK [Execute GitHub Issue Reporter agent via AWX wrapper (Windows PowerShell)] 
changed: [ServerHost-01]

TASK [Display agent execution result] ******************************************
ok: [ServerHost-01] => {
    "msg": "Status: success\nResult: **Open Issues Report**..."
}

PLAY RECAP *********************************************************************
ServerHost-01              : ok=5    changed=1    unreachable=0    failed=0
```

---

## 🆘 **If Still Failing**

### **Test WinRM Connectivity First**

**From AWX execution node** (SSH into AWX server), run:

```bash
# Install test tools
pip install pypsrp

# Test Python WinRM connection
python3 << EOF
from pypsrp.client import Client
client = Client("your-target-ip", username="Administrator", password="your_password", ssl=False)
output, streams, had_errors = client.execute_cmd("hostname")
print(output)
EOF
```

If this fails, WinRM is not properly configured on ServerHost-01.

---

## 📚 **Full Documentation**

- **Detailed Windows Setup**: [AWX_WINDOWS_SETUP.md](AWX_WINDOWS_SETUP.md)
- **General AWX Setup**: [README.md](README.md)
- **Troubleshooting**: [PSRP_FIX_GUIDE.md](PSRP_FIX_GUIDE.md)

---

## ✅ **Checklist Before Re-Running**

- [ ] Inventory host `ServerHost-01` has `ansible_python_interpreter: auto_silent` set
- [ ] Job template playbook changed to `playbook_windows.yml`
- [ ] Machine credential created with Windows admin credentials
- [ ] Machine credential attached to job template
- [ ] **Root `.env` file exists**: `C:\Users\<your-username>\Documents\GitHub\Agentic_AI_Development_Framework\.env` ✨ NEW
- [ ] **Project `.env` file exists**: `C:\Users\<your-username>\Documents\GitHub\Agentic_AI_Development_Framework\projects\04_github_issue_reporter\.env` ✨ NEW
- [ ] `.env` files contain all required values (OLLAMA_*, GITHUB_*, LANGFUSE_*) ✨ NEW
- [ ] WinRM enabled on ServerHost-01 (run PowerShell script above)
- [ ] Firewall allows port 5985 on ServerHost-01
- [ ] AWX server can ping ServerHost-01: `ping your-target-ip`
- [ ] Virtual environment exists: `C:\Users\<your-username>\Documents\GitHub\Agentic_AI_Development_Framework\projects\04_github_issue_reporter\.venv`
- [ ] Python executable exists: `C:\Users\<your-username>\Documents\GitHub\Agentic_AI_Development_Framework\projects\04_github_issue_reporter\.venv\Scripts\python.exe`

---

## 🎯 **Summary**

**Problem**: AWX (Linux) trying to execute Linux commands on Windows target
**Root Cause**: Wrong playbook + missing `ansible_python_interpreter: auto_silent` setting
**Solution**: Use Windows-specific playbook + disable Python interpreter discovery
**Time to Fix**: ~5 minutes (after WinRM is enabled)

**Files Created**:
1. ✅ `playbook_windows.yml` - Windows-compatible playbook
2. ✅ `AWX_WINDOWS_SETUP.md` - Detailed Windows setup guide
3. ✅ `QUICK_FIX.md` - This file (action summary)
4. ✅ Updated `README.md` - Added Windows scenario

**Next Step**: Complete the 3 actions above, then re-run your AWX job template.
