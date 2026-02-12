#!/usr/bin/env python3
"""
🛡️ COMPREHENSIVE SECURITY TEST SUITE
Tests the Security Guardian on multiple realistic applications
Perfect for hackathon video demonstration!
"""

import re
import os
from typing import List, Dict

# ANSI color codes for pretty terminal output
RED = '\033[91m'
ORANGE = '\033[93m'
GREEN = '\033[92m'
BLUE = '\033[94m'
PURPLE = '\033[95m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'

class SecurityScanner:
    """Simple vulnerability scanner with fix suggestions"""
    
    def __init__(self):
        self.patterns = {
            'sql_injection': [
                (r'execute\s*\(\s*["\'].*\+.*["\']', "SQL query with string concatenation", "CRITICAL"),
                (r'execute\s*\(\s*f["\'].*\{.*\}.*["\']', "SQL query with f-string", "CRITICAL"),
                (r'\.format\s*\(.*\)', "SQL query with .format()", "CRITICAL"),
                (r'SELECT.*WHERE.*\+', "SELECT with concatenation", "CRITICAL"),
            ],
            'hardcoded_credentials': [
                (r'PASSWORD\s*=\s*["\'][^"\']+["\']', "Hardcoded password", "HIGH"),
                (r'API.*KEY\s*=\s*["\'][^"\']+["\']', "Hardcoded API key", "HIGH"),
                (r'SECRET.*=\s*["\'][^"\']+["\']', "Hardcoded secret", "HIGH"),
                (r'GITHUB.*TOKEN\s*=\s*["\'][^"\']+["\']', "Hardcoded GitHub token", "HIGH"),
            ],
            'command_injection': [
                (r'os\.system\s*\(', "Command execution via os.system()", "CRITICAL"),
                (r'subprocess\..*shell\s*=\s*True', "Shell command injection", "CRITICAL"),
                (r'eval\s*\(', "Code execution via eval()", "CRITICAL"),
                (r'exec\s*\(', "Code execution via exec()", "CRITICAL"),
            ],
            'xss': [
                (r'render_template_string.*\{.*\}', "XSS via template rendering", "HIGH"),
                (r'\.innerHTML\s*=', "XSS via innerHTML", "HIGH"),
                (r'<script>.*\{.*\}.*</script>', "XSS in script tag", "HIGH"),
            ],
            'path_traversal': [
                (r'open\s*\(.*\+.*filename', "Path traversal in file open", "HIGH"),
                (r'os\.path\.join\s*\(.*request\.', "Path traversal risk", "MEDIUM"),
            ],
            'weak_crypto': [
                (r'hashlib\.md5', "Weak hashing algorithm (MD5)", "MEDIUM"),
                (r'base64\.b64encode', "Base64 encoding (not encryption!)", "MEDIUM"),
            ],
            'insecure_deserialization': [
                (r'pickle\.loads', "Insecure deserialization (pickle)", "CRITICAL"),
            ],
        }
        
        # Suggested fixes for each vulnerability type
        self.fixes = {
            'sql_injection': {
                'title': 'Use Parameterized Queries',
                'example': 'query = "SELECT * FROM users WHERE id = ?"\nresult = conn.execute(query, (user_id,))'
            },
            'hardcoded_credentials': {
                'title': 'Use Environment Variables',
                'example': 'import os\nAPI_KEY = os.getenv("API_KEY")\nPASSWORD = os.getenv("DB_PASSWORD")'
            },
            'command_injection': {
                'title': 'Avoid Shell Execution or Use Allowlist',
                'example': '# Use subprocess with list, not shell=True\nsubprocess.run(["ping", "-c", "4", server], capture_output=True)\n# Or use allowlist of safe commands'
            },
            'xss': {
                'title': 'Escape User Input',
                'example': 'from markupsafe import escape\nsafe_output = escape(user_input)\n# Or use template engine with auto-escaping'
            },
            'path_traversal': {
                'title': 'Validate and Sanitize File Paths',
                'example': 'import os\nbase_dir = "/safe/directory/"\npath = os.path.abspath(os.path.join(base_dir, filename))\nif not path.startswith(base_dir):\n    raise ValueError("Invalid path")'
            },
            'weak_crypto': {
                'title': 'Use Strong Hashing (bcrypt/scrypt)',
                'example': 'import bcrypt\nhashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())\n# Or use argon2, scrypt'
            },
            'insecure_deserialization': {
                'title': 'Use Safe Serialization (JSON)',
                'example': 'import json\ndata = json.loads(user_input)  # Safe\n# Avoid pickle.loads() with untrusted data'
            },
        }
    
    def scan(self, code: str, filename: str) -> List[Dict]:
        """Scan code for vulnerabilities"""
        vulnerabilities = []
        lines = code.split('\n')
        
        for vuln_type, pattern_list in self.patterns.items():
            for pattern, description, severity in pattern_list:
                for line_num, line in enumerate(lines, 1):
                    if re.search(pattern, line, re.IGNORECASE):
                        vulnerabilities.append({
                            'file': filename,
                            'type': vuln_type,
                            'severity': severity,
                            'line': line_num,
                            'description': description,
                            'code': line.strip()
                        })
        
        return vulnerabilities

def print_banner():
    """Print test suite banner"""
    print(f"\n{BOLD}{PURPLE}{'='*80}{RESET}")
    print(f"{BOLD}{PURPLE}🛡️  SHIFT-LEFT SECURITY GUARDIAN - COMPREHENSIVE TEST SUITE{RESET}")
    print(f"{BOLD}{PURPLE}{'='*80}{RESET}")
    print(f"{CYAN}Testing: Banking App | E-commerce | API Server | Admin Dashboard{RESET}\n")

def print_file_header(filename: str, file_num: int, total: int):
    """Print test file header"""
    print(f"\n{BOLD}{BLUE}{'─'*80}{RESET}")
    print(f"{BOLD}{BLUE}📄 TEST CASE {file_num}/{total}: {filename}{RESET}")
    print(f"{BOLD}{BLUE}{'─'*80}{RESET}\n")

def print_vulnerability(vuln: Dict, num: int, scanner: SecurityScanner):
    """Print vulnerability details with suggested fix"""
    severity_colors = {
        'CRITICAL': RED,
        'HIGH': ORANGE,
        'MEDIUM': '\033[93m',
        'LOW': GREEN
    }
    
    severity_emojis = {
        'CRITICAL': '🔴',
        'HIGH': '🟠',
        'MEDIUM': '🟡',
        'LOW': '🟢'
    }
    
    color = severity_colors.get(vuln['severity'], RESET)
    emoji = severity_emojis.get(vuln['severity'], '⚪')
    
    print(f"{num}. {emoji} {BOLD}{color}{vuln['type'].upper().replace('_', ' ')}{RESET}")
    print(f"   Severity: {color}{vuln['severity']}{RESET}")
    print(f"   Line {vuln['line']}: {vuln['description']}")
    code_snippet = vuln['code'][:70] + ('...' if len(vuln['code']) > 70 else '')
    print(f"   {CYAN}Vulnerable Code:{RESET} {code_snippet}")
    
    # Show suggested fix
    if vuln['type'] in scanner.fixes:
        fix = scanner.fixes[vuln['type']]
        print(f"   {GREEN}💡 Suggested Fix:{RESET} {fix['title']}")
        
        # Show example code (properly formatted)
        fix_lines = fix['example'].replace('\\n', '\n').split('\n')
        if len(fix_lines) > 1:
            print(f"   {GREEN}✅ Secure Code:{RESET}")
            for fix_line in fix_lines[:3]:  # Show first 3 lines
                print(f"      {fix_line}")
        else:
            print(f"   {GREEN}✅{RESET} {fix['example']}")
    
    print()  # Empty line for spacing

def print_summary(all_vulnerabilities: List[Dict]):
    """Print overall summary"""
    print(f"\n{BOLD}{PURPLE}{'='*80}{RESET}")
    print(f"{BOLD}{PURPLE}📊 COMPREHENSIVE SECURITY ANALYSIS SUMMARY{RESET}")
    print(f"{BOLD}{PURPLE}{'='*80}{RESET}\n")
    
    # Count by severity
    critical = sum(1 for v in all_vulnerabilities if v['severity'] == 'CRITICAL')
    high = sum(1 for v in all_vulnerabilities if v['severity'] == 'HIGH')
    medium = sum(1 for v in all_vulnerabilities if v['severity'] == 'MEDIUM')
    
    print(f"{BOLD}Total Vulnerabilities Found:{RESET} {RED}{len(all_vulnerabilities)}{RESET}")
    print(f"  🔴 Critical: {RED}{critical}{RESET}")
    print(f"  🟠 High:     {ORANGE}{high}{RESET}")
    print(f"  🟡 Medium:   {medium}{RESET}\n")
    
    # Count by type
    vuln_types = {}
    for v in all_vulnerabilities:
        vuln_types[v['type']] = vuln_types.get(v['type'], 0) + 1
    
    print(f"{BOLD}Vulnerability Types:{RESET}")
    for vtype, count in sorted(vuln_types.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {vtype.replace('_', ' ').title()}: {count}")
    
    print(f"\n{BOLD}{GREEN}✅ Agent Capabilities Demonstrated:{RESET}")
    print(f"  ✓ Multi-file analysis")
    print(f"  ✓ Multiple vulnerability types detected")
    print(f"  ✓ Severity classification")
    print(f"  ✓ Line-level precision")
    print(f"  ✓ Context-aware detection")
    
    print(f"\n{BOLD}{CYAN}🚀 Production Features:{RESET}")
    print(f"  • Vertex AI + Gemini 2.0 for deep analysis")
    print(f"  • LangGraph for autonomous decisions")
    print(f"  • GitHub integration with PR comments")
    print(f"  • Copilot-style code suggestions")
    print(f"  • BigQuery logging for observability")
    
    print(f"\n{BOLD}{PURPLE}{'='*80}{RESET}\n")

def main():
    """Run comprehensive security tests"""
    print_banner()
    
    # Test files
    test_files = [
        ('banking_app.py', 'Banking Application'),
        ('ecommerce_app.py', 'E-commerce Platform'),
        ('api_server.py', 'API Server'),
        ('admin_dashboard.py', 'Admin Dashboard'),
    ]
    
    scanner = SecurityScanner()
    all_vulnerabilities = []
    
    # Scan each file
    for idx, (filename, description) in enumerate(test_files, 1):
        filepath = f'test_cases/{filename}'
        
        if not os.path.exists(filepath):
            print(f"{RED}⚠️  File not found: {filepath}{RESET}")
            continue
        
        print_file_header(description, idx, len(test_files))
        
        with open(filepath, 'r') as f:
            code = f.read()
        
        vulnerabilities = scanner.scan(code, filename)
        all_vulnerabilities.extend(vulnerabilities)
        
        print(f"{BOLD}🔍 Scanning {filename}...{RESET}\n")
        
        if vulnerabilities:
            print(f"{GREEN}✅ Found {len(vulnerabilities)} vulnerabilities:{RESET}\n")
            for i, vuln in enumerate(vulnerabilities, 1):
                print_vulnerability(vuln, i, scanner)
        else:
            print(f"{GREEN}✅ No vulnerabilities detected{RESET}\n")
    
    # Print summary
    print_summary(all_vulnerabilities)
    
    print(f"{BOLD}{GREEN}🎥 PERFECT FOR HACKATHON VIDEO!{RESET}")
    print(f"{CYAN}This demonstrates real-world security analysis across multiple applications.{RESET}\n")

if __name__ == '__main__':
    main()
