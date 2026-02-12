"""
Cloud Function: GitHub Webhook Handler

Receives webhook events from GitHub and triggers the Security Guardian agent.
"""

import os
import json
import hashlib
import hmac
from flask import Request, jsonify
import functions_framework
from google.cloud import bigquery
from datetime import datetime

# Import our agent (will be deployed with the function)
import sys
sys.path.append(os.path.dirname(__file__))
from agent_wrapper import run_security_analysis


@functions_framework.http
def webhook_handler(request: Request):
    """
    Cloud Function entry point for GitHub webhooks.
    
    Triggered when:
    - Pull request opened
    - Pull request synchronized (new commits)
    """
    
    # Verify GitHub webhook signature
    if not verify_github_signature(request):
        return jsonify({"error": "Invalid signature"}), 401
    
    # Parse webhook payload
    payload = request.get_json()
    event_type = request.headers.get('X-GitHub-Event')
    
    print(f"📥 Received GitHub event: {event_type}")
    
    # Only process pull request events
    if event_type != 'pull_request':
        return jsonify({"message": "Event ignored (not a PR)"}), 200
    
    action = payload.get('action')
    
    # Only process opened and synchronized PRs
    if action not in ['opened', 'synchronize']:
        return jsonify({"message": f"Action '{action}' ignored"}), 200
    
    # Extract PR information
    pr_data = payload.get('pull_request', {})
    pr_url = pr_data.get('html_url')
    pr_number = pr_data.get('number')
    repo_name = payload.get('repository', {}).get('full_name')
    
    print(f"🔍 Analyzing PR #{pr_number} from {repo_name}")
    
    # Log to BigQuery
    log_webhook_event(payload, event_type, action)
    
    # Trigger the Security Guardian agent
    try:
        result = run_security_analysis(pr_url)
        
        # Log results to BigQuery
        log_analysis_result(pr_url, result)
        
        return jsonify({
            "status": "success",
            "pr_url": pr_url,
            "vulnerabilities_found": result.get('vulnerabilities_found', 0),
            "fixes_generated": result.get('fixes_generated', 0),
        }), 200
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return jsonify({"error": str(e)}), 500


def verify_github_signature(request: Request) -> bool:
    """
    Verify that the webhook request is from GitHub.
    Uses HMAC SHA256 signature verification.
    """
    webhook_secret = os.getenv('GITHUB_WEBHOOK_SECRET')
    
    if not webhook_secret:
        print("⚠️  Warning: GITHUB_WEBHOOK_SECRET not set, skipping verification")
        return True  # For development/testing
    
    signature = request.headers.get('X-Hub-Signature-256', '')
    
    if not signature:
        return False
    
    # Compute expected signature
    body = request.get_data()
    expected_signature = 'sha256=' + hmac.new(
        webhook_secret.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)


def log_webhook_event(payload: dict, event_type: str, action: str):
    """Log webhook event to BigQuery for metrics"""
    try:
        client = bigquery.Client()
        dataset_id = os.getenv('BIGQUERY_DATASET', 'security_guardian_logs')
        table_id = 'webhook_events'
        
        table_ref = client.dataset(dataset_id).table(table_id)
        
        row = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'action': action,
            'pr_number': payload.get('pull_request', {}).get('number'),
            'repo': payload.get('repository', {}).get('full_name'),
            'payload': json.dumps(payload),
        }
        
        errors = client.insert_rows_json(table_ref, [row])
        
        if errors:
            print(f"⚠️  BigQuery logging error: {errors}")
            
    except Exception as e:
        print(f"⚠️  Failed to log to BigQuery: {e}")


def log_analysis_result(pr_url: str, result: dict):
    """Log analysis results to BigQuery"""
    try:
        client = bigquery.Client()
        dataset_id = os.getenv('BIGQUERY_DATASET', 'security_guardian_logs')
        table_id = 'agent_decisions'
        
        table_ref = client.dataset(dataset_id).table(table_id)
        
        row = {
            'timestamp': datetime.utcnow().isoformat(),
            'pr_url': pr_url,
            'risk_level': result.get('risk_level', ''),
            'analysis_strategy': result.get('analysis_strategy', ''),
            'vulnerabilities_found': result.get('vulnerabilities_found', 0),
            'fixes_generated': result.get('fixes_generated', 0),
            'reasoning_trace': json.dumps(result.get('reasoning_trace', [])),
        }
        
        errors = client.insert_rows_json(table_ref, [row])
        
        if errors:
            print(f"⚠️  BigQuery logging error: {errors}")
            
    except Exception as e:
        print(f"⚠️  Failed to log to BigQuery: {e}")
