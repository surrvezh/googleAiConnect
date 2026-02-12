"""
Security Scanner Tool

Implements multiple scanning strategies:
1. Quick Scan: Regex-based pattern matching (fast)
2. Deep Analysis: AST parsing + LLM reasoning (thorough)

The agent autonomously chooses which strategy to use!
"""

import re
from typing import List, Dict, Optional
import ast
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage
from agent.prompts import get_vulnerability_analysis_prompt


class SecurityScanner:
    """
    Multi-strategy security vulnerability scanner.
    Showcases agent's ability to choose appropriate tools!
    """
    
    def __init__(self):
        # Vulnerability detection patterns
        self.patterns = {
            "sql_injection": [
                (r'execute\s*\(\s*["\'].*%s.*["\']', "SQL query with string formatting"),
                (r'execute\s*\(\s*f["\'].*\{.*\}.*["\']', "SQL query with f-string"),
                (r'\.raw\s*\(\s*["\'].*\+.*["\']', "Raw SQL with concatenation"),
                (r'db\.execute\s*\(\s*.*\+.*\)', "Database execute with string concatenation"),
            ],
            "hardcoded_credentials": [
                (r'password\s*=\s*["\'][^"\']+["\']', "Hardcoded password"),
                (r'api_key\s*=\s*["\'][^"\']+["\']', "Hardcoded API key"),
                (r'secret\s*=\s*["\'][^"\']+["\']', "Hardcoded secret"),
                (r'token\s*=\s*["\'][A-Za-z0-9\-_]{20,}["\']', "Hardcoded token"),
                (r'AWS_SECRET_ACCESS_KEY\s*=\s*["\'][^"\']+["\']', "AWS credentials"),
            ],
            "xss": [
                (r'innerHTML\s*=\s*.*user', "Potential XSS via innerHTML"),
                (r'eval\s*\(', "eval() usage (XSS/injection risk)"),
                (r'dangerouslySetInnerHTML', "React dangerouslySetInnerHTML"),
            ],
            "path_traversal": [
                (r'open\s*\(\s*.*\+.*user', "File operation with user input"),
                (r'os\.path\.join\s*\(.*request\.', "Path join with user input"),
            ],
        }
    
    def quick_scan(self, code: str) -> List[Dict]:
        """
        Quick regex-based pattern matching.
        Fast but may have false positives.
        """
        vulnerabilities = []
        lines = code.split('\n')
        
        for vuln_type, patterns in self.patterns.items():
            for pattern, description in patterns:
                for line_num, line in enumerate(lines, 1):
                    if re.search(pattern, line, re.IGNORECASE):
                        vulnerabilities.append({
                            "type": vuln_type,
                            "severity": self._get_severity(vuln_type),
                            "line": line_num,
                            "code_snippet": line.strip(),
                            "description": description,
                            "detection_method": "pattern_matching",
                        })
        
        # Deduplicate
        return self._deduplicate(vulnerabilities)
    
    def deep_analysis(self, code: str, llm: BaseChatModel) -> List[Dict]:
        """
        Deep analysis using AST parsing + LLM reasoning.
        More accurate but slower.
        """
        vulnerabilities = []
        
        # Try to parse as Python (expand to other languages later)
        try:
            tree = ast.parse(code)
            suspicious_sections = self._find_suspicious_nodes(tree, code)
            
            # For each suspicious section, use LLM for detailed analysis
            for section in suspicious_sections:
                vuln = self._analyze_with_llm(section, code, llm)
                if vuln:
                    vulnerabilities.append(vuln)
                    
        except SyntaxError:
            # Not valid Python, fall back to LLM analysis on chunks
            chunks = self._chunk_code(code, max_lines=50)
            for chunk in chunks[:3]:  # Analyze first 3 chunks to save tokens
                vuln = self._analyze_with_llm(chunk, code, llm)
                if vuln:
                    vulnerabilities.append(vuln)
        
        return vulnerabilities
    
    def _find_suspicious_nodes(self, tree: ast.AST, code: str) -> List[str]:
        """
        Use AST to find potentially vulnerable code sections.
        """
        suspicious = []
        
        for node in ast.walk(tree):
            # Look for database operations
            if isinstance(node, ast.Call):
                if hasattr(node.func, 'attr'):
                    method_name = node.func.attr
                    if method_name in ['execute', 'raw', 'query', 'eval']:
                        # Extract the code snippet
                        snippet = ast.get_source_segment(code, node)
                        if snippet:
                            suspicious.append(snippet)
            
            # Look for string formatting with sensitive operations
            if isinstance(node, ast.JoinedStr):  # f-strings
                snippet = ast.get_source_segment(code, node)
                if snippet and any(kw in snippet.lower() for kw in ['select', 'insert', 'update', 'delete']):
                    suspicious.append(snippet)
        
        return suspicious[:10]  # Limit to 10 most suspicious
    
    def _analyze_with_llm(
        self,
        code_snippet: str,
        full_context: str,
        llm: BaseChatModel
    ) -> Optional[Dict]:
        """
        Use LLM to analyze a code snippet for vulnerabilities.
        This is where the agent's REASONING shines!
        """
        prompt = get_vulnerability_analysis_prompt(code_snippet, full_context)
        response = llm.invoke([HumanMessage(content=prompt)])
        
        # Parse LLM response
        analysis = response.content
        
        # If no vulnerabilities found, return None
        if "no security issues" in analysis.lower() or "no vulnerabilities" in analysis.lower():
            return None
        
        # Extract vulnerability details from LLM response
        vuln_type = "unknown"
        if "sql injection" in analysis.lower():
            vuln_type = "sql_injection"
        elif "credential" in analysis.lower() or "password" in analysis.lower():
            vuln_type = "hardcoded_credentials"
        elif "xss" in analysis.lower():
            vuln_type = "xss"
        elif "path traversal" in analysis.lower():
            vuln_type = "path_traversal"
        
        # Extract severity
        severity = "medium"
        if "critical" in analysis.lower():
            severity = "critical"
        elif "high" in analysis.lower():
            severity = "high"
        elif "low" in analysis.lower():
            severity = "low"
        
        return {
            "type": vuln_type,
            "severity": severity,
            "code_snippet": code_snippet,
            "description": analysis[:300],  # First 300 chars
            "full_analysis": analysis,
            "detection_method": "llm_analysis",
        }
    
    def _chunk_code(self, code: str, max_lines: int = 50) -> List[str]:
        """Split code into analyzable chunks"""
        lines = code.split('\n')
        chunks = []
        
        for i in range(0, len(lines), max_lines):
            chunk = '\n'.join(lines[i:i + max_lines])
            chunks.append(chunk)
        
        return chunks
    
    def _get_severity(self, vuln_type: str) -> str:
        """Map vulnerability type to severity"""
        severity_map = {
            "sql_injection": "critical",
            "hardcoded_credentials": "high",
            "xss": "high",
            "path_traversal": "high",
        }
        return severity_map.get(vuln_type, "medium")
    
    def _deduplicate(self, vulnerabilities: List[Dict]) -> List[Dict]:
        """Remove duplicate vulnerabilities"""
        seen = set()
        unique = []
        
        for vuln in vulnerabilities:
            # Use type + code snippet as unique key
            key = (vuln['type'], vuln.get('code_snippet', '')[:50])
            if key not in seen:
                seen.add(key)
                unique.append(vuln)
        
        return unique
