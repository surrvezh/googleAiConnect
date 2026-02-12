# 🏗️ Shift-Left Security Guardian - Architecture

## System Architecture Diagram

The architecture diagram was generated during project setup and shows:

### High-Level Flow:
```
GitHub PR Event
      ↓ (webhook)
Cloud Function (Webhook Handler)
      ↓ (invokes)
LangGraph Agent (Vertex AI)
      ↓
[Decision Loop]
      ↓
┌─────────────┬──────────────┬─────────────┐
│             │              │             │
│  GitHub API │  Security    │   Code      │
│  Client     │  Scanner     │ Generator   │
│             │              │             │
└─────────────┴──────────────┴─────────────┘
      │             │              │
      └─────────────┴──────────────┘
                    ↓
            Post PR Review
                    ↓
      ┌─────────────┴──────────────┐
      │                            │
   BigQuery                   Cloud Storage
(Decision Logs)               (Artifacts)
```

## Agent Decision Flow (LangGraph State Machine)

The core innovation is the **autonomous decision-making** in the LangGraph agent:

```
┌─────────────────────────────────────────────────┐
│        Security Guardian Agent (Vertex AI)      │
│                                                 │
│   1. Fetch PR Data                              │
│         ↓                                       │
│   2. Assess Risk ◆ (DECISION POINT)             │
│         ↓                                       │
│    ┌────┴────┐                                  │
│    │         │                                  │
│  Low Risk  High Risk                            │
│    │         │                                  │
│    ↓         ↓                                  │
│  Quick     Deep                                 │
│  Scan    Analysis                               │
│    │         │                                  │
│    └────┬────┘                                  │
│         ↓                                       │
│   3. Generate Fixes (LLM-powered)               │
│         ↓                                       │
│   4. Validate Fixes                             │
│         ↓                                       │
│   5. Post Review (GitHub)                       │
│                                                 │
│   Powered by: Gemini 2.0 Flash                  │
└─────────────────────────────────────────────────┘
```

## Key Decision Points (Agentic Behavior)

### Decision 1: Risk Assessment
**Input**: PR metadata, file changes, diff content
**Agent Reasoning**: 
- Analyzes changed files (database operations? auth? file I/O?)
- Counts lines changed
- Uses LLM to assess complexity
**Output**: CRITICAL / HIGH / MEDIUM / LOW risk

### Decision 2: Analysis Strategy Selection
**Input**: Risk level from Decision 1
**Agent Logic**:
```python
if risk_level in ["critical", "high"]:
    strategy = "deep_analysis"  # AST parsing + LLM
elif risk_level == "medium":
    strategy = "deep_analysis"  # Be thorough
else:
    strategy = "quick_scan"     # Pattern matching sufficient
```

### Decision 3: Tool Selection
**Quick Scan Path**:
- Regex pattern matching
- Fast (< 5 seconds)
- Good for credentials, simple patterns

**Deep Analysis Path**:
- AST parsing (Python code structure)
- LLM reasoning on suspicious sections
- Context-aware (understands data flow)
- Thorough (10-20 seconds)

### Decision 4: Fix Generation
**Agent Reasoning**:
- "What ORM is this project using?" → SQL fix pattern
- "Is there a secrets manager available?" → Credentials fix
- "What template engine?" → XSS fix

### Decision 5: Self-Validation
- Syntax check generated code
- Verify fix addresses vulnerability
- Only post validated suggestions

## Data Flow

### 1. GitHub Webhook → Cloud Function
```json
{
  "action": "opened",
  "pull_request": {
    "url": "https://github.com/user/repo/pull/123",
    "changed_files": 3,
    "additions": 150
  }
}
```

### 2. Cloud Function → Agent
```python
agent.analyze_pr(pr_url="...")
```

### 3. Agent → Tools
```python
# GitHub API
diff = github_client.get_pr_diff(pr_url)

# Security Scanner
vulns = scanner.deep_analysis(diff, llm=gemini)

# Code Generator
fixes = generator.generate_fix(vuln, context=diff)
```

### 4. Agent → BigQuery (Logging)
```json
{
  "timestamp": "2024-02-12T11:30:00Z",
  "pr_url": "...",
  "risk_level": "critical",
  "analysis_strategy": "deep_analysis",
  "vulnerabilities_found": 9,
  "reasoning_trace": [
    "Assessed risk: CRITICAL (auth + db operations)",
    "Chose strategy: deep_analysis",
    "Found SQL injection in login endpoint",
    "Generated parameterized query fix",
    "Validated fix: PASSED"
  ]
}
```

### 5. Agent → GitHub (Review)
```markdown
# 🛡️ Security Guardian Analysis Report

**Found 9 potential security issue(s)**

## 🔍 Vulnerabilities Detected

### 1. 🔴 SQL Injection (CRITICAL)
**Line 23**: String concatenation in SQL query

**Vulnerable code:**
```python
query = "SELECT * FROM users WHERE username='" + username + "'"
```

**Suggested fix:**
```suggestion
query = "SELECT * FROM users WHERE username = ?"
user = conn.execute(query, (username,))
```

[... more suggestions ...]

## 🧠 Agent Reasoning Trace
[Expandable section with decision logs]
```

## Component Details

### LangGraph Agent (`agent/graph.py`)
- **State Machine**: Explicit graph of decisions
- **Observable**: Every state transition logged
- **Configurable**: Easy to add new decision points

### Tools (`agent/tools/`)

**1. SecurityScanner**
- Methods: `quick_scan()`, `deep_analysis()`
- Detection: Regex patterns + AST parsing + LLM
- Vulnerabilities: SQL injection, credentials, XSS, etc.

**2. GitHubClient**
- Methods: `get_pr_data()`, `get_pr_diff()`, `post_review()`
- Features: Copilot-style suggestions, inline comments

**3. CodeGenerator**
- Method: `generate_fix()`
- Uses: Gemini 2.0 for context-aware fixes
- Validation: Syntax checking before posting

### GCP Infrastructure

**Cloud Function**:
- Trigger: GitHub webhook
- Runtime: Python 3.11
- Timeout: 540s (9 minutes)
- Memory: 512MB

**Vertex AI**:
- Model: Gemini 2.0 Flash
- Purpose: Security analysis + fix generation
- Location: us-central1

**BigQuery**:
- Dataset: `security_guardian_logs`
- Tables: `webhook_events`, `agent_decisions`
- Purpose: Metrics, reasoning traces

**Secret Manager**:
- Secrets: GitHub token, webhook secret
- Access: Cloud Function only

## Scalability

- **Stateless**: Each PR analysis is independent
- **Parallel**: Multiple PRs processed simultaneously
- **Auto-scaling**: Cloud Functions scale automatically
- **Cost-effective**: Pay per PR analyzed (~$0.12/PR)

## Security Considerations

- ✅ Code never leaves GCP
- ✅ Encrypted at rest (Secret Manager)
- ✅ Webhook signature verification (HMAC)
- ✅ No code storage (only diffs in memory)
- ✅ Audit logs in BigQuery

## Future Architecture Enhancements

1. **Cloud Run** instead of Cloud Functions (longer timeout)
2. **Pub/Sub** for async processing
3. **Cloud Tasks** for retry logic
4. **Firestore** for state persistence
5. **Vertex AI Experiments** for A/B testing prompts

---

## Visual Diagrams

**NOTE**: The actual visual architecture diagram was generated as an image during project setup. 
Check the artifacts/images section in your IDE, or scroll up in the conversation to see the generated diagrams.

To save the diagrams to your project:
1. Right-click on the image in the artifacts panel
2. Save to `/Users/i756689/google_ai_hackathon/docs/architecture_diagram.png`
3. Reference in presentations

---

**For the full visual diagram, see the generated images above in this conversation.**
