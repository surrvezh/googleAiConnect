# 🧪 Testing Guide - Shift-Left Security Guardian

Complete testing procedure from local to production deployment.

---

## 📋 Testing Roadmap

```
Phase 1: Local Testing (No GCP needed) ✅ 5 minutes
   ↓
Phase 2: Install Dependencies ✅ 3 minutes
   ↓
Phase 3: GCP Setup & Deployment ✅ 15 minutes
   ↓
Phase 4: Live GitHub Testing ✅ 5 minutes
   ↓
Phase 5: Verify Everything Works ✅ 2 minutes
```

---

## PHASE 1: Local Testing (Quick Validation)

### Test the Security Scanner (No GCP needed)

This tests the core vulnerability detection WITHOUT needing Google Cloud.

```bash
cd /Users/i756689/google_ai_hackathon

# Create a simple test script
cat > test_scanner_local.py << 'EOF'
import sys
sys.path.insert(0, '.')

from agent.tools.security_scanner import SecurityScanner

# Test code with vulnerabilities
test_code = '''
import sqlite3

# Hardcoded credentials
password = "super_secret_123"
API_KEY = "sk-1234567890abcdef"

def login(username, password):
    # SQL Injection
    query = "SELECT * FROM users WHERE username='" + username + "'"
    db.execute(query)
'''

print("🔍 Testing Security Scanner...")
print("="*60)

scanner = SecurityScanner()
vulnerabilities = scanner.quick_scan(test_code)

print(f"\n✅ Found {len(vulnerabilities)} vulnerabilities:\n")

for i, vuln in enumerate(vulnerabilities, 1):
    print(f"{i}. {vuln['type'].upper()} (Severity: {vuln['severity']})")
    print(f"   Line {vuln['line']}: {vuln['description']}")
    print(f"   Code: {vuln['code_snippet']}\n")

print("="*60)
print("✅ Security Scanner Test Complete!")
EOF

# Run the test
python test_scanner_local.py
```

**Expected Output:**
- Should find 3 vulnerabilities: 2 hardcoded credentials + 1 SQL injection
- Confirms the scanner logic works!

---

## PHASE 2: Install Dependencies

### Option A: Using Virtual Environment (Recommended)

```bash
cd /Users/i756689/google_ai_hackathon

# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Verify installation
python -c "import langgraph; print('✅ LangGraph installed:', langgraph.__version__)"
```

### Option B: System-wide Installation

```bash
cd /Users/i756689/google_ai_hackathon
pip install -r requirements.txt
```

---

## PHASE 3: GCP Setup (Production Deployment)

### Prerequisites Checklist

Before starting, ensure you have:
- [ ] Google Cloud account with billing enabled
- [ ] `gcloud` CLI installed ([Install guide](https://cloud.google.com/sdk/docs/install))
- [ ] GitHub account
- [ ] GCP Project ID ready

### Step 3.1: Authenticate with GCP

```bash
# Login to Google Cloud
gcloud auth login

# Set application default credentials
gcloud auth application-default login

# Verify authentication
gcloud auth list
```

### Step 3.2: Run GCP Setup Script

```bash
cd /Users/i756689/google_ai_hackathon/deployment

# Make scripts executable (if not already)
chmod +x setup_gcp.sh deploy_agent.sh

# Run setup (replace YOUR_PROJECT_ID)
./setup_gcp.sh YOUR_PROJECT_ID

# Example:
# ./setup_gcp.sh my-hackathon-project-2024
```

**What this does:**
1. ✅ Enables required Google Cloud APIs
2. ✅ Creates BigQuery dataset and tables
3. ✅ Creates Cloud Storage bucket
4. ✅ Generates `.env` file for you

### Step 3.3: Configure GitHub Token

```bash
# Open the .env file
cd /Users/i756689/google_ai_hackathon
open .env

# Or edit manually:
nano .env
```

**Add your GitHub token:**

1. Go to: https://github.com/settings/tokens/new
2. Select scopes:
   - ✅ `repo` (full control of repositories)
   - ✅ `admin:repo_hook` (manage webhooks)
3. Generate token
4. Copy token to `.env`:
   ```
   GITHUB_TOKEN=ghp_YOUR_TOKEN_HERE
   GITHUB_WEBHOOK_SECRET=your_random_secret_123
   ```

### Step 3.4: Deploy to Cloud Functions

```bash
cd /Users/i756689/google_ai_hackathon/deployment

# Deploy the agent
./deploy_agent.sh
```

**What this does:**
1. ✅ Uploads code to Cloud Functions
2. ✅ Configures environment variables
3. ✅ Sets up Secret Manager
4. ✅ Returns webhook URL

**Save the webhook URL** - you'll need it next!

---

## PHASE 4: GitHub Integration Testing

### Step 4.1: Create Test Repository

```bash
# Create a new test repository on GitHub
# Or use an existing one

# Clone it locally (if new)
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
```

### Step 4.2: Configure GitHub Webhook

1. Go to your GitHub repo: `https://github.com/YOUR_USERNAME/YOUR_REPO`
2. Click **Settings** → **Webhooks** → **Add webhook**
3. Configure:
   - **Payload URL**: `[Your Cloud Function URL from Step 3.4]`
   - **Content type**: `application/json`
   - **Secret**: `[Your GITHUB_WEBHOOK_SECRET from .env]`
   - **Events**: Select "Let me select individual events"
     - ✅ Check **Pull requests** only
   - **Active**: ✅ Checked
4. Click **Add webhook**

### Step 4.3: Test with Vulnerable Code

**Test 1: Simple Hardcoded Password**

```bash
# Create a test branch
git checkout -b test/security-check-1

# Add vulnerable code
cat > test_app.py << 'EOF'
# Simple test - hardcoded password
password = "hardcoded_password_123"
api_key = "sk-1234567890abcdef"
EOF

git add test_app.py
git commit -m "Test: Add config with credentials"
git push origin test/security-check-1
```

**Now create a Pull Request on GitHub:**
1. Go to your repo on GitHub
2. Click "Compare & pull request"
3. Create the PR

**Expected Result:**
- ⏱️ Within 10-30 seconds, the agent should post a comment
- 🔍 Should detect 2 hardcoded credentials
- 💡 Should suggest using environment variables

---

**Test 2: SQL Injection**

```bash
# Create another test branch
git checkout main
git checkout -b test/sql-injection

# Add SQL injection vulnerability
cat > database.py << 'EOF'
import sqlite3

def get_user(username):
    conn = sqlite3.connect('users.db')
    # SQL Injection vulnerability!
    query = f"SELECT * FROM users WHERE name = '{username}'"
    result = conn.execute(query)
    return result.fetchone()
EOF

git add database.py
git commit -m "Add user lookup function"
git push origin test/sql-injection
```

**Create PR → Expected Result:**
- 🔍 Should detect SQL injection (HIGH severity)
- 💡 Should suggest parameterized query
- 🧠 Should show "deep_analysis" strategy in reasoning

---

**Test 3: Full Vulnerable App (Best Demo)**

```bash
# Create demo branch
git checkout main
git checkout -b demo/full-security-test

# Copy the comprehensive vulnerable app
cp /Users/i756689/google_ai_hackathon/demo/vulnerable_samples/vulnerable_app.py app.py

git add app.py
git commit -m "Add authentication and user management system"
git push origin demo/full-security-test
```

**Create PR → Expected Result:**
- 🚨 Should detect 9 vulnerabilities
- 📊 Risk level: CRITICAL
- 🔬 Strategy: deep_analysis
- 💬 Comprehensive review with all fixes

---

## PHASE 5: Verify Everything Works

### Check Cloud Function Logs

```bash
# View recent logs
gcloud functions logs read security-guardian-webhook \
  --region=us-central1 \
  --limit=50

# Watch logs in real-time (during PR creation)
gcloud functions logs read security-guardian-webhook \
  --region=us-central1 \
  --limit=50 \
  --format="table(severity,log,execution_id)"
```

### Check BigQuery Logs

```bash
# Query agent decisions
bq query --use_legacy_sql=false '
SELECT 
  timestamp,
  pr_url,
  risk_level,
  analysis_strategy,
  vulnerabilities_found,
  fixes_generated
FROM `YOUR_PROJECT_ID.security_guardian_logs.agent_decisions`
ORDER BY timestamp DESC
LIMIT 10
'
```

Or use BigQuery Console: https://console.cloud.google.com/bigquery

### Verify GitHub Review

1. Go to your PR on GitHub
2. Check the **Conversation** tab
3. You should see:
   - ✅ Comment from the Security Guardian
   - ✅ Vulnerabilities listed with severity
   - ✅ Inline code suggestions
   - ✅ Reasoning trace (expandable section)

---

## 🐛 Troubleshooting

### Issue: "Command not found: gcloud"
**Solution:**
```bash
# Install gcloud CLI
brew install --cask google-cloud-sdk
# Or download from: https://cloud.google.com/sdk/docs/install
```

### Issue: "Permission denied" on deployment
**Solution:**
```bash
# Grant your user the required roles
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="user:YOUR_EMAIL@gmail.com" \
  --role="roles/cloudfunctions.admin"
```

### Issue: Cloud Function returns 500 error
**Solution:**
```bash
# Check logs for errors
gcloud functions logs read security-guardian-webhook --limit=100

# Common fixes:
# 1. Verify GITHUB_TOKEN is set in Secret Manager
# 2. Check environment variables in Cloud Function
# 3. Ensure all dependencies are in requirements.txt
```

### Issue: Agent doesn't post review
**Solution:**
```bash
# Verify GitHub token permissions
# Token needs: repo, admin:repo_hook

# Check if token is in Secret Manager
gcloud secrets versions access latest --secret=github-token

# Re-deploy if needed
cd deployment
./deploy_agent.sh
```

### Issue: Webhook signature verification fails
**Solution:**
```bash
# Ensure webhook secret matches between:
# 1. .env file
# 2. Secret Manager
# 3. GitHub webhook settings

# Update secret:
echo -n "your_webhook_secret" | gcloud secrets versions add github-webhook-secret --data-file=-
```

---

## 📊 Success Metrics

Your project is working correctly if:

✅ **Local test** finds vulnerabilities in test code  
✅ **Cloud Function** deploys without errors  
✅ **GitHub webhook** shows "Recent Deliveries" with 200 status  
✅ **PR comment** appears within 30 seconds of PR creation  
✅ **BigQuery** has entries in `agent_decisions` table  
✅ **Inline suggestions** are clickable/applicable in GitHub  

---

## 🎯 Next Steps After Testing

Once everything works:

1. **Practice Demo Flow**
   - Use `demo/test_pr_guide.md` for scenarios
   - Time yourself (should be <2 minutes for full demo)

2. **Prepare Presentation**
   - Review `PITCH_DECK.md`
   - Practice explaining autonomous decisions
   - Prepare to show BigQuery reasoning trace

3. **Create Backup PRs**
   - Have 2-3 test PRs ready
   - In case of internet issues during demo

4. **Document Issues Found**
   - Track detection rate
   - Note any false positives
   - Collect metrics for presentation

---

## 📞 Quick Reference Commands

```bash
# Deploy
cd deployment && ./deploy_agent.sh

# View logs
gcloud functions logs read security-guardian-webhook --limit=50

# Test locally
cd demo && python test_agent.py

# Query BigQuery
bq query --use_legacy_sql=false 'SELECT * FROM security_guardian_logs.agent_decisions LIMIT 10'

# Redeploy after changes
cd deployment && ./deploy_agent.sh
```

---

**Ready to start testing? Let's begin with Phase 1! 🚀**
