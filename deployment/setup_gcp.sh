#!/bin/bash

###############################################################################
# Shift-Left Security Guardian - GCP Setup Script
#
# This script sets up the Google Cloud Platform environment:
# - Enables required APIs
# - Creates BigQuery datasets and tables
# - Sets up Cloud Storage bucket
# - Configures IAM permissions
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🛡️  Shift-Left Security Guardian - GCP Setup${NC}\n"

# Check if project ID is provided
if [ -z "$1" ]; then
    echo -e "${RED}Error: GCP Project ID required${NC}"
    echo "Usage: ./setup_gcp.sh YOUR_PROJECT_ID"
    exit 1
fi

PROJECT_ID=$1
REGION=${2:-us-central1}

echo -e "${YELLOW}Project ID:${NC} $PROJECT_ID"
echo -e "${YELLOW}Region:${NC} $REGION\n"

# Set the project
echo -e "${GREEN}📌 Setting GCP project...${NC}"
gcloud config set project $PROJECT_ID

# Enable required APIs
echo -e "\n${GREEN}🔧 Enabling required Google Cloud APIs...${NC}"
gcloud services enable \
    cloudfunctions.googleapis.com \
    cloudbuild.googleapis.com \
    aiplatform.googleapis.com \
    bigquery.googleapis.com \
    storage-api.googleapis.com \
    secretmanager.googleapis.com

echo -e "${GREEN}✓ APIs enabled${NC}"

# Create BigQuery dataset
echo -e "\n${GREEN}📊 Setting up BigQuery...${NC}"
DATASET_ID="security_guardian_logs"

# Check if dataset exists
if bq ls -d $PROJECT_ID:$DATASET_ID &> /dev/null; then
    echo -e "${YELLOW}Dataset $DATASET_ID already exists${NC}"
else
    bq mk --dataset --location=$REGION $PROJECT_ID:$DATASET_ID
    echo -e "${GREEN}✓ Created dataset: $DATASET_ID${NC}"
fi

# Create webhook_events table
echo -e "${GREEN}Creating webhook_events table...${NC}"
bq mk --table \
    --schema timestamp:TIMESTAMP,event_type:STRING,action:STRING,pr_number:INTEGER,repo:STRING,payload:STRING \
    --time_partitioning_field timestamp \
    $PROJECT_ID:$DATASET_ID.webhook_events || echo -e "${YELLOW}Table may already exist${NC}"

# Create agent_decisions table
echo -e "${GREEN}Creating agent_decisions table...${NC}"
bq mk --table \
    --schema timestamp:TIMESTAMP,pr_url:STRING,risk_level:STRING,analysis_strategy:STRING,vulnerabilities_found:INTEGER,fixes_generated:INTEGER,reasoning_trace:STRING \
    --time_partitioning_field timestamp \
    $PROJECT_ID:$DATASET_ID.agent_decisions || echo -e "${YELLOW}Table may already exist${NC}"

echo -e "${GREEN}✓ BigQuery setup complete${NC}"

# Create Cloud Storage bucket for artifacts
echo -e "\n${GREEN}📦 Setting up Cloud Storage...${NC}"
BUCKET_NAME="${PROJECT_ID}-security-guardian"

if gsutil ls -b gs://$BUCKET_NAME &> /dev/null; then
    echo -e "${YELLOW}Bucket $BUCKET_NAME already exists${NC}"
else
    gsutil mb -l $REGION gs://$BUCKET_NAME
    echo -e "${GREEN}✓ Created bucket: gs://$BUCKET_NAME${NC}"
fi

# Create .env file
echo -e "\n${GREEN}📝 Creating environment configuration...${NC}"

if [ -f "../.env" ]; then
    echo -e "${YELLOW}.env file already exists, skipping${NC}"
else
    cat > ../.env <<EOF
# Google Cloud Configuration
GCP_PROJECT_ID=$PROJECT_ID
GCP_LOCATION=$REGION
VERTEX_AI_MODEL=gemini-2.0-flash-001

# GitHub Configuration (UPDATE THESE!)
GITHUB_TOKEN=your_github_token_here
GITHUB_WEBHOOK_SECRET=your_webhook_secret_here

# BigQuery Configuration
BIGQUERY_DATASET=$DATASET_ID
BIGQUERY_TABLE=agent_decisions

# Cloud Storage
GCS_BUCKET=$BUCKET_NAME

# Agent Configuration
AGENT_MAX_ITERATIONS=10
AGENT_TEMPERATURE=0.1
ENABLE_REASONING_LOGS=true
EOF
    echo -e "${GREEN}✓ Created .env file${NC}"
    echo -e "${YELLOW}⚠️  IMPORTANT: Update .env with your GitHub token and webhook secret${NC}"
fi

# Setup complete
echo -e "\n${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ GCP Setup Complete!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"

echo -e "${YELLOW}Next steps:${NC}"
echo -e "1. Update ${GREEN}.env${NC} with your GitHub token"
echo -e "2. Run ${GREEN}./deploy_agent.sh${NC} to deploy the Cloud Function"
echo -e "3. Configure GitHub webhook with the function URL\n"
