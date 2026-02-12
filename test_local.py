#!/usr/bin/env python3
"""
Quick local test - No GCP needed!
Tests the security scanner with vulnerable code.
"""

import sys
sys.path.insert(0, '.')

from agent.tools.security_scanner import SecurityScanner

# Test code with multiple vulnerabilities
test_code = '''
import sqlite3

# VULNERABILITY 1 & 2: Hardcoded credentials
password = "super_secret_123"
API_KEY = "sk-1234567890abcdef"

def login(username, password):
    # VULNERABILITY 3: SQL Injection
    query = "SELECT * FROM users WHERE username='" + username + "'"
    db.execute(query)
    
def search(term):
    # VULNERABILITY 4: SQL Injection with f-string
    sql = f"SELECT * FROM posts WHERE title LIKE '%{term}%'"
    return db.execute(sql)
'''

print("\n" + "="*70)
print("🛡️  SECURITY GUARDIAN - LOCAL TEST")
print("="*70)
print("\n🔍 Testing Security Scanner on vulnerable code...\n")

scanner = SecurityScanner()
vulnerabilities = scanner.quick_scan(test_code)

print(f"✅ Scanner completed! Found {len(vulnerabilities)} vulnerabilities:\n")
print("-"*70)

for i, vuln in enumerate(vulnerabilities, 1):
    severity_emoji = {
        "critical": "🔴",
        "high": "🟠",
        "medium": "🟡",
        "low": "🟢"
    }
    emoji = severity_emoji.get(vuln['severity'], '⚪')
    
    print(f"\n{i}. {emoji} {vuln['type'].upper().replace('_', ' ')}")
    print(f"   Severity: {vuln['severity'].upper()}")
    print(f"   Line {vuln.get('line', '?')}: {vuln['description']}")
    print(f"   Code: {vuln['code_snippet'][:60]}...")

print("\n" + "="*70)
print("✅ LOCAL TEST COMPLETE!")
print("="*70)
print(f"\n📊 Results: {len(vulnerabilities)} vulnerabilities detected")
print("🎯 Next step: Install dependencies and test with GCP\n")
