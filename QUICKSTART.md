# Quick Start Guide

Get Security Guardian running in **15 minutes**!

## Prerequisites

- ✅ Google Cloud account with billing enabled
- ✅ GitHub account and repository
- ✅ Python 3.11+
- ✅ gcloud CLI installed

## Step 1: Clone & Setup (2 min)

```bash
cd /Users/i756689/google_ai_hackathon

# Copy environment template
cp .env.example .env

# Edit .env with your settings
# Required: GCP_PROJECT_ID, GITHUB_TOKEN
```

## Step 2: Setup GCP (5 min)

```bash
cd deployment

# Make scripts executable
chmod +x setup_gcp.sh deploy_agent.sh

# Run setup (replace YOUR_PROJECT_ID)
./setup_gcp.sh YOUR_PROJECT_ID

# This will:
# - Enable required APIs
# - Create BigQuery datasets
# - Setup Cloud Storage
# - Generate .env file
```

## Step 3: Create GitHub Token (2 min)

1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes:
   - `repo` (full control)
   - `admin:repo_hook` (webhooks)
4. Copy token
5. Add to `.env`: `GITHUB_TOKEN=ghp_your_token_here`

## Step 4: Deploy Agent (5 min)

```bash
# Still in deployment directory
./deploy_agent.sh

# This will:
# - Deploy Cloud Function
# - Setup secrets
# - Output webhook URL
```

**Save the webhook URL** - you'll need it next!

## Step 5: Configure GitHub Webhook (2 min)

1. Go to your GitHub repo
2. Settings → Webhooks → Add webhook
3. Configure:
   - **Payload URL**: [Your function URL from step 4]
   - **Content type**: application/json
   - **Secret**: [Your GITHUB_WEBHOOK_SECRET from .env]
   - **Events**: "Pull requests" only
4. Click "Add webhook"

## Step 6: Test! (1 min)

```bash
# Create test branch
git checkout -b test/security-check

# Add vulnerable code
echo 'password = "hardcoded123"' > test.py
git add test.py
git commit -m "Test security guardian"
git push origin test/security-check

# Create PR on GitHub
```

Watch the magic happen! 🎉

The Security Guardian will:
1. Analyze your PR
2. Find the hardcoded password
3. Post a review with fixes
4. Show reasoning in BigQuery

---

## Troubleshooting

### "Cloud Function deployment failed"
- Check GCP billing is enabled
- Verify APIs are enabled: `gcloud services list`

### "Webhook returns 401"
- Verify GITHUB_WEBHOOK_SECRET matches in .env and GitHub
- Check Secret Manager has the secret

### "Agent doesn't post review"
- Check GITHUB_TOKEN has correct permissions
- Verify token is set in Secret Manager
- Check Cloud Function logs: `gcloud functions logs read security-guardian-webhook`

### "Want to test locally without GCP?"
```bash
cd demo
python test_agent.py
```

---

## Next Steps

✅ **For Development**:
- Add more vulnerability patterns in `agent/tools/security_scanner.py`
- Customize prompts in `agent/prompts.py`
- Add language support (currently Python-focused)

✅ **For Demo**:
- Use `demo/vulnerable_samples/vulnerable_app.py` for impressive demo
- Check `demo/test_pr_guide.md` for demo scenarios
- Review `PITCH_DECK.md` for presentation tips

✅ **For Production**:
- Add authentication to webhook endpoint
- Setup monitoring alerts in Cloud Monitoring
- Configure auto-scaling for Cloud Functions
- Add rate limiting

---

## Support & Resources

- **Documentation**: See README.md
- **Architecture**: See PITCH_DECK.md + architecture diagram
- **Demo Guide**: demo/test_pr_guide.md
- **Local Testing**: demo/test_agent.py

**Happy security hunting! 🛡️🚀**
