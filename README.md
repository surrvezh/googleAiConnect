# 🛡️ Shift-Left Security Guardian

**Autonomous AI Agent for GitHub PR Security Review**

Built for Google AI Hackathon using Vertex AI Agent Builder & LangGraph

## 🎯 What Makes This Agentic?

This is NOT simple automation - it's a **true autonomous agent** that:

1. **DECIDES**: "Is this PR high-risk? Should I do deep analysis or quick scan?"
2. **PLANS**: "I'll first scan for common vulnerabilities, then deep-dive on suspicious sections"
3. **USES TOOLS**: Autonomously chooses between regex, AST parsing, or LLM analysis
4. **REASONS**: "Found SQL injection - let me check the ORM and generate parameterized queries"
5. **VALIDATES**: "Does my fix compile? Let me verify before suggesting"

## 🏗️ Architecture

```
GitHub PR → Webhook → Cloud Function → LangGraph Agent (Vertex AI)
                                            ↓
                                    [Decision Loop]
                                            ↓
                        ┌───────────────────┴───────────────────┐
                        ↓                   ↓                   ↓
                 GitHub API Tool    Security Scanner    Code Generator
                        ↓                   ↓                   ↓
                    Fetch Diff          Find Vulns        Generate Fixes
                        └───────────────────┬───────────────────┘
                                            ↓
                                    Post PR Comments
                                    (Copilot-style suggestions)
                                            ↓
                                    BigQuery Logging
```

## 🔧 Tech Stack

- **Agent Framework**: LangGraph (state machine with reasoning traces)
- **LLM**: Gemini 2.0 Flash via Vertex AI
- **Tools**: GitHub API, AST parsers, regex scanners
- **Deployment**: Cloud Run (agent) + Cloud Functions (webhook)
- **Storage**: BigQuery (logs), Cloud Storage (artifacts)
- **Language**: Python 3.11+

## 📦 Project Structure

```
shift-left-security-guardian/
├── agent/                          # LangGraph agent core
│   ├── graph.py                    # Agent state machine
│   ├── tools/                      # Tool implementations
│   │   ├── security_scanner.py     # Vulnerability detection
│   │   ├── github_client.py        # GitHub API wrapper
│   │   └── code_generator.py       # Fix suggestions
│   └── prompts.py                  # Agent system prompts
├── cloud_function/                 # GCP webhook handler
│   ├── main.py                     # Cloud Function entry
│   └── requirements.txt
├── deployment/                     # GCP deployment configs
│   ├── deploy_agent.sh
│   └── setup_gcp.sh
├── demo/                           # Demo materials
│   └── vulnerable_samples/         # Test PRs
└── requirements.txt                # Python dependencies
```

## 🚀 Quick Start

### 1. Setup GCP
```bash
cd deployment
./setup_gcp.sh YOUR_PROJECT_ID
```

### 2. Deploy Agent
```bash
./deploy_agent.sh
```

### 3. Configure GitHub Webhook
Point your GitHub webhook to the Cloud Function URL (output from deployment)

### 4. Test with Sample PR
```bash
cd demo
# Follow test_pr_guide.md
```

## 🎥 Demo Flow

1. Create PR with vulnerable code (SQL injection, hardcoded keys)
2. Agent autonomously analyzes → **Shows reasoning trace**
3. Posts Copilot-style inline suggestions
4. Developer can review & apply fixes with one click

## 🏆 Hackathon Highlights

- ✅ **Observable Reasoning**: Every agent decision logged to BigQuery
- ✅ **Interactive Suggestions**: GitHub review comments with code diffs
- ✅ **Production Ready**: Deployed on GCP with proper auth & monitoring
- ✅ **True Autonomy**: Agent adapts strategy based on code complexity

## 📊 Metrics Tracked

- Time per analysis
- Vulnerabilities detected (by type)
- Agent decision paths (which tools were chosen)
- Fix acceptance rate

## 🔐 Security Vulnerabilities Detected

**Phase 1 (Core)**:
- SQL Injection
- Hardcoded credentials (API keys, passwords)

**Phase 2 (Bonus)**:
- XSS vulnerabilities
- Path traversal
- Insecure deserialization
