# Quick Fix Guide: psrp Connection Error

## Problem Summary

Your AWX job is failing with this error:
```
[WARNING]: ansible_psrp_transport is unsupported by the current psrp version installed
fatal: [ServerHost-01]: FAILED! => {"msg": "cannot run the interpreter '/usr/bin/python' on the psrp connection plugin"}
```

**Root Cause**: Ansible is trying to discover a Python interpreter on the Windows target host (`ServerHost-01`) during psrp connection, but Windows doesn't have Python at the Linux path `/usr/bin/python`.

---

## Immediate Fix Options

### Option 1: Update AWX Inventory Host Variables (Recommended)

Update the inventory host `ServerHost-01` in AWX to disable Python interpreter discovery:

1. **Navigate to AWX UI**: Resources → Inventories → [Your Inventory] → Hosts → `ServerHost-01`
2. **Edit Host Variables** (YAML format):
   ```yaml
   ansible_connection: psrp
   ansible_psrp_protocol: http  # or https if using SSL
   ansible_psrp_auth: basic  # or ntlm, negotiate, kerberos
   ansible_python_interpreter: auto_silent  # ← This disables Python discovery
   ansible_psrp_cert_validation: ignore  # optional, if using self-signed certs
   ```
3. **Save** and re-run the job template

**Why this works**: `ansible_python_interpreter: auto_silent` tells Ansible not to discover Python on the target host, which is unnecessary for Windows psrp connections.

---

### Option 2: Use localhost with Local Connection (Alternative)

If AWX and the agent run on the same Windows server, use localhost instead:

1. **Navigate to AWX UI**: Resources → Templates → [Your Job Template] → Inventory
2. **Change to use a localhost-only inventory**:
   - Create new inventory: `Localhost Only`
   - Add host: `localhost`
   - Set host variables:
     ```yaml
     ansible_connection: local
     ansible_python_interpreter: auto_silent
     ```
3. **Update Job Template** to use this inventory
4. **Re-run the job**

**Why this works**: `ansible_connection: local` bypasses network connections entirely and runs commands locally.

---

### Option 3: Upgrade pypsrp Library (If Version Issue)

The warning `ansible_psrp_transport is unsupported` suggests an outdated `pypsrp` library:

1. **SSH into AWX execution node** (or update execution environment container)
2. **Upgrade pypsrp**:
   ```bash
   pip install --upgrade pypsrp
   ```
3. **Verify version** (should be 0.8.0+):
   ```bash
   python -c "import pypsrp; print(pypsrp.__version__)"
   ```
4. **Restart AWX services** (if needed)
5. **Re-run the job**

---

## Verification Steps

After applying the fix, verify the job runs successfully:

1. **Check playbook sync**: Ensure AWX project synced the latest `playbook.yml` (which now includes `ansible_python_interpreter: auto_silent` in play vars)
2. **Test connection**:
   ```bash
   # From AWX execution node, test psrp connection
   ansible ServerHost-01 -i /path/to/inventory -m win_ping \
     -e ansible_connection=psrp \
     -e ansible_python_interpreter=auto_silent
   ```
   Expected output: `ServerHost-01 | SUCCESS => { "ping": "pong" }`
3. **Launch job template** from AWX UI
4. **Monitor job output** - should no longer see Python interpreter discovery errors

---

## Updated Playbook Changes

The `playbook.yml` has been updated to support both localhost and remote Windows hosts:

**Before**:
```yaml
- name: Execute 04_github_issue_reporter AI Agent
  hosts: localhost
  gather_facts: false
  
  vars:
    project_dir: "{{ playbook_dir }}/.."
    # ... rest of vars
```

**After**:
```yaml
- name: Execute 04_github_issue_reporter AI Agent
  hosts: all  # ← Changed to support inventory flexibility
  gather_facts: false
  
  # Disable Python interpreter discovery for Windows/psrp connections
  vars:
    ansible_python_interpreter: auto_silent  # ← Added this
    project_dir: "{{ playbook_dir }}/.."
    # ... rest of vars
```

---

## Best Practice Configuration

For production AWX deployments with Windows execution nodes:

**Inventory Structure**:
```yaml
# Inventory: Windows Agents
all:
  children:
    windows_hosts:
      hosts:
        ServerHost-01:
          ansible_host: 10.0.0.101
          ansible_connection: psrp
          ansible_psrp_protocol: https
          ansible_psrp_auth: negotiate
          ansible_psrp_cert_validation: ignore
          ansible_python_interpreter: auto_silent
```

**Job Template Settings**:
- **Inventory**: Windows Agents (with host variables above)
- **Project**: Agentic AI Agents (synced to latest commit)
- **Playbook**: `projects/04_github_issue_reporter/awx/playbook.yml`
- **Credentials**: Ollama API, GitHub API, Windows Credential (for psrp auth)
- **Verbosity**: 1 (Verbose) for debugging

---

## Troubleshooting Commands

If still encountering issues, run these diagnostics:

```powershell
# 1. Check AWX project sync status
awx projects list --name "Agentic AI Agents" --format yaml

# 2. Verify playbook.yml exists and is up-to-date
ls /var/lib/awx/projects/<project_id>/projects/04_github_issue_reporter/awx/playbook.yml

# 3. Test psrp connectivity manually
ansible-playbook -i inventory playbook.yml --check -vvv

# 4. Check pypsrp version on execution node
pip show pypsrp | grep Version

# 5. Verify Python interpreter setting
ansible ServerHost-01 -i inventory -m setup -a "filter=ansible_python_interpreter"
```

---

## Next Steps

1. ✅ Apply **Option 1** (update inventory host variables) - **recommended first step**
2. ✅ Re-run AWX job template and verify success
3. ✅ If still failing, apply **Option 3** (upgrade pypsrp)
4. ✅ Update `README.md` documentation with your final working configuration
5. ✅ Commit changes to repository

**Documentation Updated**:
- `playbook.yml` - Now supports remote Windows hosts
- `README.md` - Added troubleshooting section for psrp errors
- This guide - Quick reference for fixing the immediate issue

---

**Support**: See full troubleshooting guide in [README.md](README.md#troubleshooting)
