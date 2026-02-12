# 🔑 Credentials & Tokens Guide

## What Tokens Do You Need?

### ✅ REQUIRED for Full Deployment

1. **GitHub Personal Access Token** (for GitHub API)
2. **GCP Authentication** (via gcloud CLI)
3. **GitHub Webhook Secret** (for webhook security)

### ❌ NOT REQUIRED for Local Testing

You can test the security scanner locally WITHOUT any tokens!

---

## 📝 Detailed Setup Guide

### 1. GitHub Personal Access Token

**When needed:** To fetch PR data and post review comments

**How to create:**

1. Go to: https://github.com/settings/tokens/new
2. Token name: `security-guardian-agent`
3. Expiration: `90 days` (or `No expiration` for hackathon)
4. Select scopes:
   - ✅ **repo** (Full control of private repositories)
     - ✅ repo:status
     - ✅ repo_deployment
     - ✅ public_repo
     - ✅ repo:invite
     - ✅ security_events
   - ✅ **admin:repo_hook** (Full control of repository hooks)
     - ✅ write:repo_hook
     - ✅ read:repo_hook

5. Click "Generate token"
6. **Copy the token immediately** (you won't see it again!)
7. Save it to your `.env` file:
   ```bash
   GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

**Example token format:**
```
ghp_1a2b3c4d5e6f7g8h9i0jklmnopqrstuvwxyzABC
```

---

### 2. GCP Authentication (Google Cloud)

**When needed:** To use Vertex AI (Gemini), BigQuery, Cloud Functions

**How to set up:**

#### Step 2a: Install gcloud CLI

```bash
# Check if already installed
gcloud --version

# If not installed:
brew install --cask google-cloud-sdk

# Initialize
gcloud init
```

#### Step 2b: Authenticate

```bash
# Login to your Google account
gcloud auth login

# Set application default credentials (for Vertex AI)
gcloud auth application-default login

# Set your project
gcloud config set project YOUR_PROJECT_ID
```

**You DON'T need to manually create a token** - gcloud handles this for you!

#### Step 2c: Enable Required APIs

```bash
# The setup script does this, but you can manually enable:
gcloud services enable \
  cloudfunctions.googleapis.com \
  cloudbuild.googleapis.com \
  aiplatform.googleapis.com \
  bigquery.googleapis.com \
  storage-api.googleapis.com \
  secretmanager.googleapis.com
```

---

### 3. GitHub Webhook Secret

**When needed:** To verify webhook requests are actually from GitHub

**How to create:**

Just create a random string:

```bash
# Generate a random secret
openssl rand -hex 32

# Example output:
# 3f8a9b2c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2
```

Save it to your `.env` file:
```bash
GITHUB_WEBHOOK_SECRET=your_random_secret_here
```

**Use the SAME secret** when configuring the GitHub webhook later!

---

## 📋 Complete .env File Template

Create `/Users/i756689/google_ai_hackathon/.env`:

```bash
# ============================================
# Google Cloud Configuration
# ============================================
GCP_PROJECT_ID=your-gcp-project-id
GCP_LOCATION=us-central1
VERTEX_AI_MODEL=gemini-2.0-flash-001

# ============================================
# GitHub Configuration
# ============================================
# Get from: https://github.com/settings/tokens
GITHUB_TOKEN=ghp_your_github_token_here

# Generate with: openssl rand -hex 32
GITHUB_WEBHOOK_SECRET=your_random_webhook_secret

# ============================================
# BigQuery Configuration
# ============================================
BIGQUERY_DATASET=security_guardian_logs
BIGQUERY_TABLE=agent_decisions

# ============================================
# Cloud Storage
# ============================================
GCS_BUCKET=your-project-id-security-guardian

# ============================================
# Agent Configuration
# ============================================
AGENT_MAX_ITERATIONS=10
AGENT_TEMPERATURE=0.1
ENABLE_REASONING_LOGS=true
```

---

## 🚦 Testing Tiers (What Works Without Tokens)

### Tier 1: **Local Security Scanner** (NO tokens needed)
```bash
cd /Users/i756689/google_ai_hackathon
python test_local.py
```
✅ Tests vulnerability detection patterns
❌ No LLM analysis (no GCP)
❌ No GitHub integration

---

### Tier 2: **With GCP Auth** (Only gcloud needed)
```bash
# After: gcloud auth application-default login
cd demo
python test_agent.py
```
✅ Tests security scanner
✅ Tests LLM-based code generation (Gemini)
❌ No GitHub integration (but uses mock data)

---

### Tier 3: **Full Integration** (All tokens needed)
```bash
# After: Setup GCP + GitHub token
cd deployment
./deploy_agent.sh
```
✅ Full agent deployed
✅ GitHub webhook integration
✅ Real PR analysis
✅ Automated review posting

---

## 🔒 Security Best Practices

### ✅ DO:
- Store tokens in `.env` file (already in .gitignore)
- Use Secret Manager in GCP (deployment script does this)
- Rotate tokens every 90 days
- Use minimum required permissions

### ❌ DON'T:
- Commit tokens to Git
- Share tokens publicly
- Use tokens in code (always use environment variables)
- Give tokens more permissions than needed

---

## 🧪 Quick Test: Do Your Tokens Work?

### Test GitHub Token:
```bash
curl -H "Authorization: token YOUR_GITHUB_TOKEN" \
  https://api.github.com/user

# Should return your GitHub user info
```

### Test GCP Auth:
```bash
gcloud auth application-default print-access-token

# Should print an access token (means auth is working)
```

---

## ❓ FAQ

**Q: I don't have a GCP account. Can I still test locally?**
A: Yes! Use `test_local.py` - it only tests the scanner, no GCP needed.

**Q: What if my GitHub token expires?**
A: Create a new one with the same permissions and update `.env`

**Q: How much will GCP cost?**
A: Very little for hackathon testing:
- Gemini API: ~$0.10 per PR
- Cloud Functions: ~$0.01 per invocation
- BigQuery: Minimal (first 10GB free)
- **Total**: ~$0.12 per PR analyzed

**Q: Can I use a free GCP trial?**
A: Yes! New accounts get $300 in credits.

---

## 🎯 Recommended Flow for Hackathon

**Day 1: Local Testing**
1. Test locally without any tokens
2. See if the scanner logic works

**Day 2: GCP Setup**
1. Create GCP account (get $300 free credits)
2. Run `gcloud auth login`
3. Test with Gemini (no GitHub yet)

**Day 3: Full Integration**
1. Create GitHub token
2. Deploy to Cloud Functions
3. Test with real PRs

---

## 📞 Need Help?

**Can't create GitHub token?**
- Need: Repository admin access
- Alternative: Use personal repo for testing

**GCP authentication failing?**
- Run: `gcloud auth application-default login`
- Check: `gcloud config list`

**Webhook secret unsure?**
- Just use any random string for testing
- Example: `my_super_secret_webhook_key_123`

---

**Next Step:** Let me know if you want to:
1. Test locally first (no tokens)
2. Set up GCP authentication
3. Create GitHub token
