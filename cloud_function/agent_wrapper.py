"""
Agent Wrapper for Cloud Function

This wrapper makes it easy to call the agent from the Cloud Function.
"""

import os
import sys

# Add parent directory to path to import agent
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agent.graph import SecurityGuardianAgent


def run_security_analysis(pr_url: str) -> dict:
    """
    Run security analysis on a GitHub PR.
    
    This is the main entry point for the Cloud Function.
    """
    # Get GCP configuration from environment
    project_id = os.getenv('GCP_PROJECT_ID')
    location = os.getenv('GCP_LOCATION', 'us-central1')
    model_name = os.getenv('VERTEX_AI_MODEL', 'gemini-2.0-flash-001')
    
    if not project_id:
        raise ValueError("GCP_PROJECT_ID environment variable not set")
    
    # Initialize agent
    agent = SecurityGuardianAgent(
        project_id=project_id,
        location=location,
        model_name=model_name
    )
    
    # Run analysis
    result = agent.analyze_pr(pr_url)
    
    return result
