"""
System prompts for the Security Guardian agent.
These prompts guide the LLM's reasoning and decision-making.
"""


def get_system_prompt() -> str:
    """Base system prompt for the security agent"""
    return """You are a Security Guardian Agent - an autonomous AI that reviews code for security vulnerabilities.

Your capabilities:
- Detect SQL injection, hardcoded credentials, XSS, path traversal
- Generate secure code alternatives
- Explain security issues in developer-friendly language
- Make autonomous decisions about analysis depth

Your personality:
- Helpful and educational (not just critical)
- Transparent about reasoning
- Prioritize high-severity issues
- Suggest actionable fixes

Remember: You're helping developers build secure software, not just finding problems!"""


def get_decision_prompt(pr_data: dict, diff_content: str) -> str:
    """
    Prompt for risk assessment decision.
    The agent uses this to AUTONOMOUSLY decide analysis strategy.
    """
    changed_files = pr_data.get('changed_files', 0)
    additions = pr_data.get('additions', 0)
    deletions = pr_data.get('deletions', 0)
    title = pr_data.get('title', '')
    
    return f"""Analyze this Pull Request and assess its security risk level.

PR Title: {title}
Files Changed: {changed_files}
Lines Added: {additions}
Lines Deleted: {deletions}

Code Diff (first 2000 chars):
```
{diff_content[:2000]}
```

Based on this information, assess the risk level:
- HIGH RISK: Database operations, authentication, file I/O, external API calls, crypto
- MEDIUM RISK: Business logic changes, data validation, config changes
- LOW RISK: UI changes, documentation, tests, minor refactoring

Provide your assessment in this format:
RISK LEVEL: [High/Medium/Low]
REASONING: [Why you chose this level]
RECOMMENDED ANALYSIS: [Quick scan or deep analysis]
KEY CONCERNS: [Specific areas to focus on]

Be concise but thorough in your reasoning."""


def get_vulnerability_analysis_prompt(code_snippet: str, context: str) -> str:
    """Prompt for deep vulnerability analysis"""
    return f"""Analyze this code snippet for security vulnerabilities.

Code to analyze:
```python
{code_snippet}
```

Surrounding context:
```
{context[:1000]}
```

Check for:
1. SQL Injection (raw SQL queries, string concatenation)
2. Hardcoded Credentials (API keys, passwords, tokens)
3. XSS (unescaped user input in HTML)
4. Path Traversal (file operations with user input)
5. Insecure Deserialization

For each vulnerability found, provide:
- Type: [SQL Injection, Credentials, XSS, etc.]
- Severity: [Critical, High, Medium, Low]
- Line numbers (if identifiable)
- Explanation: Why this is vulnerable
- Impact: What could an attacker do?

If no vulnerabilities found, state: "No security issues detected."
"""


def get_fix_generation_prompt(
    vulnerability: dict,
    original_code: str,
    context: str
) -> str:
    """Prompt for generating secure code fixes"""
    vuln_type = vulnerability.get('type', 'Unknown')
    description = vulnerability.get('description', '')
    
    return f"""Generate a secure fix for this vulnerability.

Vulnerability Type: {vuln_type}
Description: {description}

Original Code:
```python
{original_code}
```

Context:
```
{context[:800]}
```

Generate a SECURE alternative that:
1. Fixes the vulnerability
2. Maintains the same functionality
3. Follows Python best practices
4. Includes comments explaining the fix

Provide:
1. FIXED CODE: [Complete secure version]
2. EXPLANATION: [What changed and why it's secure]
3. ADDITIONAL NOTES: [Any other security considerations]

Keep the fix minimal - only change what's necessary for security."""
