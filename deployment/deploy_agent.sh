#!/bin/bash

###############################################################################
# Deploy Security Guardian Agent to Cloud Functions
#
# This deploys the webhook handler and agent to GCP Cloud Functions
###############################################################################

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🚀 Deploying Security Guardian Agent${NC}\n"

# Load environment variables
if [ ! -f "../.env" ]; then
    echo -e "${RED}Error: .env file not found${NC}"
    echo "Run ./setup_gcp.sh first"
    exit 1
fi

source ../.env

if [ -z "$GCP_PROJECT_ID" ]; then
    echo -e "${RED}Error: GCP_PROJECT_ID not set in .env${NC}"
    exit 1
fi

echo -e "${YELLOW}Project:${NC} $GCP_PROJECT_ID"
echo -e "${YELLOW}Region:${NC} $GCP_LOCATION\n"

# Set project
gcloud config set project $GCP_PROJECT_ID

# Create secrets in Secret Manager
echo -e "${GREEN}🔐 Setting up secrets...${NC}"

# GitHub token
if [ "$GITHUB_TOKEN" != "your_github_token_here" ]; then
    echo -n "$GITHUB_TOKEN" | gcloud secrets create github-token \
        --data-file=- --replication-policy=automatic || \
        echo -e "${YELLOW}Secret github-token already exists${NC}"
fi

# Webhook secret
if [ "$GITHUB_WEBHOOK_SECRET" != "your_webhook_secret_here" ]; then
    echo -n "$GITHUB_WEBHOOK_SECRET" | gcloud secrets create github-webhook-secret \
        --data-file=- --replication-policy=automatic || \
        echo -e "${YELLOW}Secret github-webhook-secret already exists${NC}"
fi

# Copy agent code to cloud_function directory
echo -e "\n${GREEN}📦 Preparing deployment package...${NC}"
cp -r ../agent ../cloud_function/

# Deploy Cloud Function
echo -e "\n${GREEN}☁️  Deploying Cloud Function...${NC}"

gcloud functions deploy security-guardian-webhook \
    --gen2 \
    --runtime python311 \
    --region $GCP_LOCATION \
    --source ../cloud_function \
    --entry-point webhook_handler \
    --trigger-http \
    --allow-unauthenticated \
    --timeout 540s \
    --memory 512MB \
    --set-env-vars \
GCP_PROJECT_ID=$GCP_PROJECT_ID,\
GCP_LOCATION=$GCP_LOCATION,\
VERTEX_AI_MODEL=$VERTEX_AI_MODEL,\
BIGQUERY_DATASET=$BIGQUERY_DATASET,\
ENABLE_REASONING_LOGS=$ENABLE_REASONING_LOGS \
    --set-secrets \
GITHUB_TOKEN=github-token:latest,\
GITHUB_WEBHOOK_SECRET=github-webhook-secret:latest

# Get the function URL
FUNCTION_URL=$(gcloud functions describe security-guardian-webhook \
    --region $GCP_LOCATION \
    --gen2 \
    --format='value(serviceConfig.uri)')

# Cleanup
rm -rf ../cloud_function/agent

echo -e "\n${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo -e "${YELLOW}Webhook URL:${NC}"
echo -e "${GREEN}$FUNCTION_URL${NC}\n"

echo -e "${YELLOW}Next steps:${NC}"
echo -e "1. Copy the webhook URL above"
echo -e "2. In your GitHub repo, go to: Settings → Webhooks → Add webhook"
echo -e "3. Paste the URL and set:"
echo -e "   - Content type: ${GREEN}application/json${NC}"
echo -e "   - Secret: ${GREEN}your webhook secret from .env${NC}"
echo -e "   - Events: ${GREEN}Pull requests${NC}"
echo -e "4. Create a test PR and watch the agent work! 🤖\n"
