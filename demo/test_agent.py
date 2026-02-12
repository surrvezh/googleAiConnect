"""
Local Test Script - Test the Security Guardian Agent without GitHub

This allows you to test the agent locally before deploying to GCP.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.graph import SecurityGuardianAgent
from agent.tools.security_scanner import SecurityScanner
from agent.tools.code_generator import CodeGenerator
from langchain_google_vertexai import ChatVertexAI


def test_security_scanner():
    """Test the security scanner on vulnerable code"""
    print("="*60)
    print("🔍 Testing Security Scanner")
    print("="*60)
    
    # Load vulnerable code
    with open('vulnerable_samples/vulnerable_app.py', 'r') as f:
        code = f.read()
    
    scanner = SecurityScanner()
    
    # Quick scan
    print("\n⚡ Running Quick Scan...")
    quick_vulns = scanner.quick_scan(code)
    print(f"Found {len(quick_vulns)} vulnerabilities\n")
    
    for vuln in quick_vulns:
        print(f"  🚨 {vuln['type']} ({vuln['severity']})")
        print(f"     Line {vuln['line']}: {vuln['description']}")
        print(f"     Code: {vuln['code_snippet'][:80]}...\n")
    
    return quick_vulns


def test_code_generator(vulnerabilities):
    """Test the code generator"""
    print("\n" + "="*60)
    print("🔧 Testing Code Generator")
    print("="*60)
    
    # You need to set up GCP credentials for this
    project_id = os.getenv('GCP_PROJECT_ID')
    
    if not project_id:
        print("\n⚠️  GCP_PROJECT_ID not set - skipping LLM-based tests")
        print("To test with Gemini, set GCP_PROJECT_ID in .env\n")
        return
    
    try:
        llm = ChatVertexAI(
            model_name="gemini-2.0-flash-001",
            project=project_id,
            location="us-central1",
        )
        
        generator = CodeGenerator(llm)
        
        # Generate fix for first vulnerability
        if vulnerabilities:
            vuln = vulnerabilities[0]
            print(f"\n💡 Generating fix for: {vuln['type']}\n")
            
            fix = generator.generate_fix(
                vulnerability=vuln,
                original_code=vuln['code_snippet'],
                context="Flask application with database operations"
            )
            
            print("Original Code:")
            print(f"  {vuln['code_snippet']}\n")
            
            print("Suggested Fix:")
            print(f"  {fix['fixed_code'][:200]}...\n")
            
            print(f"Explanation: {fix['explanation'][:150]}...\n")
            
            # Validate
            is_valid = generator.validate_fix(fix)
            print(f"✓ Fix validation: {'PASSED' if is_valid else 'FAILED'}\n")
            
    except Exception as e:
        print(f"❌ Error testing code generator: {e}\n")


def test_full_agent():
    """Test the full agent (requires GCP setup)"""
    print("\n" + "="*60)
    print("🤖 Testing Full Agent")
    print("="*60)
    
    project_id = os.getenv('GCP_PROJECT_ID')
    
    if not project_id:
        print("\n⚠️  GCP_PROJECT_ID not set - skipping full agent test")
        print("To test the full agent:")
        print("1. Set up GCP project")
        print("2. Run deployment/setup_gcp.sh")
        print("3. Set GCP_PROJECT_ID in .env\n")
        return
    
    try:
        agent = SecurityGuardianAgent(
            project_id=project_id,
            location="us-central1"
        )
        
        # Mock PR URL (will use mock data since no real GitHub repo)
        mock_pr_url = "https://github.com/test/repo/pull/1"
        
        print(f"\n🔍 Analyzing mock PR: {mock_pr_url}\n")
        
        result = agent.analyze_pr(mock_pr_url)
        
        print("\n" + "="*60)
        print("📊 Results Summary")
        print("="*60)
        print(f"Risk Level: {result['risk_level']}")
        print(f"Analysis Strategy: {result['analysis_strategy']}")
        print(f"Vulnerabilities Found: {result['vulnerabilities_found']}")
        print(f"Fixes Generated: {result['fixes_generated']}\n")
        
        print("🧠 Reasoning Trace:")
        for step in result['reasoning_trace']:
            print(f"  {step}")
        
    except Exception as e:
        print(f"❌ Error testing agent: {e}\n")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n" + "🛡️  " * 20)
    print("=" * 60)
    print("   SHIFT-LEFT SECURITY GUARDIAN - LOCAL TEST")
    print("=" * 60)
    print("🛡️  " * 20 + "\n")
    
    # Change to demo directory
    os.chdir(os.path.dirname(__file__))
    
    # Test 1: Security Scanner (no GCP needed)
    vulnerabilities = test_security_scanner()
    
    # Test 2: Code Generator (needs GCP)
    test_code_generator(vulnerabilities)
    
    # Test 3: Full Agent (needs GCP)
    test_full_agent()
    
    print("\n" + "="*60)
    print("✅ Testing Complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Deploy to GCP: cd ../deployment && ./deploy_agent.sh")
    print("2. Set up GitHub webhook")
    print("3. Create test PR and watch the agent work! 🚀\n")
