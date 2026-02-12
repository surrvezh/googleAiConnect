# Test PR Creation Guide

This guide shows how to create test PRs to demonstrate the Security Guardian agent.

## 🎯 Demo Scenario 1: SQL Injection Fix

### Step 1: Create a branch with vulnerable code
```bash
git checkout -b feature/add-search-endpoint

# Add this code to app.py:
@app.route('/search')
def search():
    query_term = request.args.get('q')
    sql = f"SELECT * FROM users WHERE name LIKE '%{query_term}%'"
    results = db.execute(sql)
    return {"results": results}
```

### Step 2: Create PR
The Security Guardian will:
1. ✅ Detect HIGH RISK (database operations)
2. 🔍 Choose DEEP ANALYSIS strategy
3. 🚨 Find SQL injection vulnerability
4. 💡 Suggest parameterized query fix:
   ```python
   sql = "SELECT * FROM users WHERE name LIKE ?"
   results = db.execute(sql, (f'%{query_term}%',))
   ```
5. 💬 Post Copilot-style review with clickable suggestion

---

## 🎯 Demo Scenario 2: Hardcoded Credentials

### Step 1: Create a branch
```bash
git checkout -b feature/add-api-integration

# Add this code to config.py:
API_KEY = "sk-1234567890abcdef"
DATABASE_PASSWORD = "super_secret_pass"
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCY"
```

### Step 2: Create PR
The Security Guardian will:
1. ✅ Detect MEDIUM RISK (config changes)
2. ⚡ Choose QUICK SCAN (pattern matching is enough)
3. 🚨 Find 3 hardcoded credentials
4. 💡 Suggest environment variables:
   ```python
   import os
   API_KEY = os.getenv('API_KEY')
   DATABASE_PASSWORD = os.getenv('DB_PASSWORD')
   ```
5. 📊 Show reasoning trace: "Pattern detected → Environment vars recommended"

---

## 🎯 Demo Scenario 3: Full Vulnerable App (Best for Judges!)

### Step 1: Use the provided vulnerable_app.py
```bash
git checkout -b feature/user-authentication
cp demo/vulnerable_samples/vulnerable_app.py app.py
git add app.py
git commit -m "Add user authentication endpoints"
```

### Step 2: Create PR
The Security Guardian will:
1. ✅ Detect CRITICAL RISK (auth + database operations)
2. 🔬 Choose DEEP ANALYSIS (LLM + AST parsing)
3. 🚨 Find 9 different vulnerabilities:
   - 4x SQL Injection (different patterns)
   - 3x Hardcoded credentials
   - 1x Path traversal
   - 1x XSS vulnerability
4. 💡 Generate comprehensive fixes for each
5. 📈 Show detailed reasoning trace demonstrating autonomous decision-making

---

## 📊 Expected Agent Reasoning Trace (for judges)

When the agent analyzes the full vulnerable app, it will log:

```
[2024-02-12T11:30:00] Fetching PR data from: https://github.com/user/repo/pull/1
Retrieved 450 characters of diff content, 1 files changed

[2024-02-12T11:30:02] Analyzing PR risk factors...
Risk Assessment: CRITICAL
Chosen Strategy: deep_analysis
LLM Reasoning: Multiple database operations detected with user input.
               Authentication logic present. High potential for SQLi.
               Hardcoded strings that appear to be credentials.
               Recommendation: Deep analysis with AST + LLM.

[2024-02-12T11:30:05] Running deep analysis (AST + LLM reasoning)...
Deep analysis: 3 pattern-based + 6 LLM-detected
Total vulnerabilities: 9

[2024-02-12T11:30:08] Generating secure code fixes...
Generated 9 secure code alternatives
  ✓ Fix validated: sql_injection_fix
  ✓ Fix validated: hardcoded_credentials_fix
  ✓ Fix validated: path_traversal_fix
  ...

[2024-02-12T11:30:12] Posting review to GitHub PR...
✓ Review posted successfully to GitHub
```

---

## 🎬 Live Demo Tips

1. **Show the agent "thinking"**: Pull up BigQuery and show the reasoning trace
2. **Highlight autonomous decisions**: Point to "Chosen Strategy: deep_analysis"
3. **Show Copilot-style UX**: Click "Apply suggestion" in GitHub
4. **Compare to traditional tools**: Run Bandit on same code - agent finds MORE issues
5. **Show speed**: From PR creation to fix suggestions in <30 seconds

---

## 🧪 Quick Local Test (Without GitHub)

```bash
# Install dependencies
pip install -r requirements.txt

# Test the agent locally
python test_agent.py

# This will:
# 1. Load vulnerable_app.py
# 2. Run the agent
# 3. Print findings to console
# (No GitHub required!)
```

---

## 💡 Talking Points for Judges

**"This isn't just automation - it's true agent behavior"**

Point to:
1. ✅ **Autonomous Risk Assessment**: Agent DECIDES analysis strategy
2. ✅ **Tool Selection**: Chooses regex vs AST vs LLM based on complexity
3. ✅ **Contextual Reasoning**: "Found SQL injection → checking ORM → generating parameterized query"
4. ✅ **Self-Validation**: Validates fixes before posting
5. ✅ **Transparent Reasoning**: Full trace shows every decision

**"It's production-ready on GCP"**
- Deployed on Cloud Functions/Run
- Integrated with Vertex AI
- Logged to BigQuery for analytics
- GitHub webhook integration

**"It's developer-friendly"**
- Copilot-style suggestions
- One-click fix application
- Educational explanations
- No false positive spam
