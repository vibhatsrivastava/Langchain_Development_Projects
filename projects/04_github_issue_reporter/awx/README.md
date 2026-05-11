# AWX Setup Guide for 04_github_issue_reporter

This guide walks through setting up Ansible AWX to schedule and trigger the **GitHub Issue Reporter & Solution Recommender** agent.

---

## Prerequisites

- Ansible AWX instance (version 21.0+) with admin or project management access
- This repository accessible to AWX (Git, manual upload, or network share)
- Network connectivity from AWX execution nodes to:
  - Ollama server (for LLM inference)
  - GitHub API (api.github.com)
  - Langfuse server (optional, for observability)
- GitHub Personal Access Token with `repo` scope (for write operations)

---

## Setup Steps

### 1. Import Custom Credential Types

AWX requires custom credential types to inject secrets securely. Import the definitions from `awx/credentials.yml`:

1. Navigate to **Settings → Credential Types** in AWX UI
2. Click **Add** to create new credential type
3. Copy YAML from `awx/credentials.yml` for each credential type:
   - **Ollama API Credentials** (required)
   - **Langfuse Observability Credentials** (optional)
   - **GitHub API Credentials** (required)
4. Paste YAML into AWX form (Name, Description, Inputs, Injectors)
5. Save each credential type

**Tip**: Use AWX CLI/API for bulk import:
```bash
awx credential_types create --name "Ollama API Credentials" --inputs @awx/credentials.yml ...
```

---

### 2. Create Credentials

Create credential instances using the imported types:

1. Navigate to **Resources → Credentials** in AWX UI
2. Click **Add** for each required credential:
   
   **Ollama API Credentials**:
   - Name: `Ollama Server - Production`
   - Credential Type: `Ollama API Credentials`
   - Ollama Base URL: `http://your-ollama-server:11434`
   - Ollama API Key: `your_bearer_token` (leave empty for local/unauthenticated)
   - Default Model: `gpt-oss:20b`
   
   **GitHub API Credentials**:
   - Name: `GitHub - Issue Reporter Token`
   - Credential Type: `GitHub API Credentials`
   - GitHub Personal Access Token: `ghp_your_token_here` (with `repo` scope)
   - Repository Owner: `your_github_username` (or organization)
   - Repository Name: `your_repository_name`
   
   **Langfuse Observability Credentials** (optional):
   - Name: `Langfuse - Production`
   - Credential Type: `Langfuse Observability Credentials`
   - Enable Tracing: `true`
   - Langfuse Public Key: `pk-lf-...`
   - Langfuse Secret Key: `sk-lf-...`
   - Langfuse Host: `http://your-langfuse-server:3000`

---

### 3. Create Project

A project in AWX points to the source code repository:

1. Navigate to **Resources → Projects**
2. Click **Add**
3. Configure:
   - **Name**: `Agentic AI Agents`
   - **Organization**: Your organization
   - **SCM Type**: `Git` (or `Manual` if using network share)
   - **SCM URL**: `https://github.com/your-org/Agentic_AI_Development_Framework.git`
   - **SCM Branch**: `main` (or your working branch)
   - **SCM Update Options**: ✓ Update Revision on Launch
4. Save and wait for project sync to complete

---

### 4. Create Job Template

A job template combines the playbook, credentials, and survey:

1. Navigate to **Resources → Templates → Job Templates**
2. Click **Add → Job Template**
3. Configure:
   - **Name**: `GitHub Issue Reporter - Run Agent`
   - **Job Type**: `Run`
   - **Inventory**: Select an inventory with `localhost`
   - **Project**: `Agentic AI Agents`
   - **Playbook**: `projects/04_github_issue_reporter/awx/playbook.yml`
   - **Credentials**:
     - Add `Ollama API Credentials` credential
     - Add `GitHub API Credentials` credential
     - Add `Langfuse Observability Credentials` credential (optional)
   - **Verbosity**: `1 (Verbose)` or higher for debugging
   - **Options**: ✓ Enable Concurrent Jobs (if desired)
4. Save the template

---

### 5. Attach Survey Specification

Surveys allow operators to provide runtime parameters via UI forms:

1. Open the job template created in Step 4
2. Click the **Survey** tab
3. Click **Add**
4. Copy the entire content of `awx/survey.json`
5. Paste into the JSON editor
6. Click **Save**
7. Toggle **Survey Enabled** to ON

**Survey Fields**:
- **Execution Mode**: Choose `report`, `issue`, or `auto-analyze`
- **Issue Number**: Specify issue number (required for `issue` mode)
- **Dry Run**: Preview without posting comments (`auto-analyze` mode only)
- **Max Issues**: Limit number of issues processed (default: 100)
- **Log Level**: Set logging verbosity (DEBUG, INFO, WARNING, ERROR)

---

### 6. Test Execution

Run a manual test to verify the setup:

1. Navigate to the job template
2. Click **Launch**
3. Fill out the survey:
   - **Execution Mode**: `report`
   - **Log Level**: `INFO`
4. Click **Next** → **Launch**
5. Monitor the job output in real-time
6. Verify successful execution:
   - Exit code: 0
   - JSON output with `"status": "success"`
   - Report displayed in job log

**Expected Output**:
```json
{
  "status": "success",
  "result": "**Open Issues Report**\n\n| # | Title | Author | ...",
  "metadata": {
    "agent": "04_github_issue_reporter",
    "execution_time": 12.34,
    "awx_job_id": "12345"
  }
}
```

---

### 7. Schedule Recurring Jobs (Optional)

Automate issue analysis on a schedule:

1. Navigate to **Resources → Schedules**
2. Click **Add**
3. Configure:
   - **Name**: `Daily Issue Auto-Analysis`
   - **Start Date/Time**: Set desired start time
   - **Time Zone**: Select your timezone
   - **Repeat Frequency**: Choose frequency (e.g., `Daily`, `Hourly`)
   - **Run On**: Select days of week (for weekly schedules)
   - **Job Template**: Select `GitHub Issue Reporter - Run Agent`
   - **Survey Values**:
     ```json
     {
       "mode": "auto-analyze",
       "dry_run": "false",
       "max_issues": "50",
       "log_level": "INFO"
     }
     ```
4. Save the schedule

**Common Schedules**:
- **Daily Auto-Analysis**: Run every morning to analyze new issues
- **Hourly Report**: Generate issue report every hour
- **Weekly Bulk Analysis**: Deep analysis of all open issues once per week

---

## Usage Patterns

### Pattern 1: Manual On-Demand Execution

**Use Case**: Operator wants to analyze a specific issue right now.

**Steps**:
1. Navigate to job template → **Launch**
2. Survey:
   - **Execution Mode**: `issue`
   - **Issue Number**: `42`
   - **Log Level**: `INFO`
3. Click **Launch**
4. Agent fetches issue details, generates recommendation, and posts comment to GitHub
5. Check GitHub issue for new AI analysis comment

---

### Pattern 2: Scheduled Auto-Analysis

**Use Case**: Automatically analyze all new issues every day at 9 AM.

**Configuration**:
- **Schedule**: Daily at 9:00 AM (your timezone)
- **Survey**:
  - **Execution Mode**: `auto-analyze`
  - **Dry Run**: `false`
  - **Max Issues**: `100`
  - **Log Level**: `INFO`

**Behavior**:
- Agent fetches issues opened in the last 24 hours
- Analyzes each issue and posts recommendation
- Skips issues that already have bot comments (prevents duplicates)
- Logs summary of processed issues

---

### Pattern 3: Webhook-Triggered Analysis

**Use Case**: Analyze new issues immediately when they're opened.

**Setup**:
1. Create a webhook in AWX job template
2. Configure GitHub webhook:
   - **Payload URL**: `https://awx.example.com/api/v2/job_templates/123/github/`
   - **Content type**: `application/json`
   - **Events**: Select `Issues` (only `opened` action)
3. Add webhook secret to AWX job template

**Behavior**:
- GitHub sends webhook when new issue is opened
- AWX receives webhook and launches job
- Agent analyzes the issue and posts recommendation
- Near real-time response (< 1 minute)

---

### Pattern 4: Dry Run Preview

**Use Case**: Preview auto-analysis results before enabling comment posting.

**Steps**:
1. Launch job template with survey:
   - **Execution Mode**: `auto-analyze`
   - **Dry Run**: `true`
   - **Max Issues**: `10`
   - **Log Level**: `DEBUG`
2. Review job output to see what would be posted
3. Verify recommendations are accurate
4. Re-run with `dry_run: false` to post comments

---

### Pattern 5: API-Triggered Execution

**Use Case**: Integrate with CI/CD pipeline or external system.

**Example**:
```bash
# Trigger via AWX API
curl -X POST https://awx.example.com/api/v2/job_templates/123/launch/ \
  -H "Authorization: Bearer $AWX_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "extra_vars": {
      "mode": "issue",
      "issue_number": "42",
      "log_level": "INFO"
    }
  }'
```

**Use Cases**:
- CI pipeline triggers analysis after merging PR
- External monitoring system detects high issue count and triggers report
- Integration with Slack bot for on-demand analysis

---

## Troubleshooting

### Issue 1: Agent Fails with "GITHUB_TOKEN not found"

**Cause**: GitHub API credential not attached to job template or token is invalid.

**Solution**:
1. Verify credential is created: **Resources → Credentials → GitHub API Credentials**
2. Check credential is attached to job template: **Templates → Edit → Credentials**
3. Verify token has `repo` scope: https://github.com/settings/tokens
4. Test token manually:
   ```bash
   curl -H "Authorization: Bearer $GITHUB_TOKEN" https://api.github.com/user
   ```

---

### Issue 2: Playbook Fails with "Virtual environment not found"

**Cause**: Project `.venv` not created or AWX SCM path incorrect.

**Solution**:
1. Ensure project sync completed successfully
2. Check AWX project path: `/var/lib/awx/projects/<project_name>`
3. Verify `.venv` exists in project directory:
   ```bash
   ls /var/lib/awx/projects/Agentic_AI_Agents/projects/04_github_issue_reporter/.venv
   ```
4. If missing, run setup on AWX execution node:
   ```bash
   cd /var/lib/awx/projects/Agentic_AI_Agents/projects/04_github_issue_reporter
   uv venv .venv
   uv pip install -e ../../../common
   uv pip install -r requirements.txt
   ```

---

### Issue 3: Agent Execution Times Out

**Cause**: Large number of issues or slow LLM inference.

**Solution**:
1. Increase job template timeout: **Templates → Edit → Job Timeout** (e.g., 600 seconds)
2. Reduce `max_issues` in survey (e.g., 10 instead of 100)
3. Use faster LLM model (e.g., `llama3.1:8b` instead of `gpt-oss:20b`)
4. Check Ollama server performance and network latency

---

### Issue 4: Bot Posts Duplicate Comments

**Cause**: Survey `issue_number` set incorrectly or bot marker not detected.

**Solution**:
1. Agent checks for bot marker (`<!-- AI-ANALYSIS-BOT -->`) before posting
2. Verify existing comments contain the marker:
   ```bash
   curl -H "Authorization: Bearer $GITHUB_TOKEN" \
     https://api.github.com/repos/owner/repo/issues/42/comments
   ```
3. If marker is missing, agent will post new comment
4. Use `dry_run: true` to preview before posting

---

### Issue 5: Langfuse Tracing Not Working

**Cause**: Langfuse credentials not attached or server unreachable.

**Solution**:
1. Verify Langfuse credential is attached (optional)
2. Check Langfuse server is reachable from AWX execution nodes:
   ```bash
   curl http://your-langfuse-server:3000/health
   ```
3. Verify API keys are correct (check Langfuse dashboard)
4. Set `langfuse_enabled: false` if not using observability

---

## Advanced Configuration

### Custom AWX Execution Environments

If AWX uses containerized execution environments, ensure the container has:
- Python 3.11+
- `uv` package manager
- Network access to Ollama and GitHub

**Dockerfile Example**:
```dockerfile
FROM quay.io/ansible/awx-ee:latest
USER root
RUN pip install uv
USER 1000
```

---

### Multi-Repository Support

To support multiple repositories, create separate job templates:
1. Duplicate job template
2. Attach different GitHub credential (with different `GITHUB_REPO_OWNER` and `GITHUB_REPO_NAME`)
3. Name template accordingly (e.g., `GitHub Issue Reporter - Repo A`)

Or use a dynamic inventory with repository configuration as host variables.

---

### Integration with Jira/ServiceNow

Export agent results to external ticketing systems:
1. Add custom tool in `main.py` to create Jira ticket
2. Modify playbook to parse agent output and call Jira API
3. Use AWX workflow to chain jobs (analyze issue → create Jira ticket)

---

## Security Best Practices

1. **Use Vault for Secrets**: Store credentials in HashiCorp Vault or AWX encrypted storage
2. **Limit Token Scope**: GitHub token should have minimum required permissions (`public_repo` for public repos)
3. **Rotate Tokens Regularly**: Update GitHub token every 90 days
4. **Audit Job Logs**: Review AWX job logs for sensitive data exposure
5. **Enable RBAC**: Restrict job template execution to authorized users only
6. **Network Segmentation**: Isolate AWX execution nodes in secure network zone

---

## Support & Feedback

For issues or questions:
- **Documentation**: See repository `docs/` directory
- **GitHub Issues**: Report bugs or feature requests
- **Contributing**: See `docs/contributing.md` for AWX integration patterns

---

**Next Steps**:
1. Complete AWX setup (Steps 1-6)
2. Run test execution (Step 6)
3. Configure schedule or webhook (Step 7)
4. Monitor job execution and review GitHub comments
5. Adjust survey parameters and LLM model as needed
