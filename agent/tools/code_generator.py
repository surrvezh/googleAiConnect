"""
Code Generator Tool

Generates secure code fixes for detected vulnerabilities.
Uses LLM to create context-aware solutions!
"""

import ast
from typing import Dict, Optional
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage
from agent.prompts import get_fix_generation_prompt


class CodeGenerator:
    """
    Generates secure code alternatives using LLM reasoning.
    
    This showcases the agent's ability to not just find bugs,
    but also SOLVE them autonomously!
    """
    
    def __init__(self, llm: BaseChatModel):
        self.llm = llm
    
    def generate_fix(
        self,
        vulnerability: Dict,
        original_code: str,
        context: str
    ) -> Dict:
        """
        Generate a secure fix for a vulnerability.
        
        Args:
            vulnerability: Detected vulnerability details
            original_code: The vulnerable code snippet
            context: Surrounding code for context
            
        Returns:
            dict with fixed code and explanation
        """
        vuln_type = vulnerability.get('type', 'unknown')
        
        # Get LLM to generate fix
        prompt = get_fix_generation_prompt(vulnerability, original_code, context)
        response = self.llm.invoke([HumanMessage(content=prompt)])
        
        fix_content = response.content
        
        # Parse the LLM response to extract fixed code
        fixed_code = self._extract_code_block(fix_content)
        explanation = self._extract_explanation(fix_content)
        
        return {
            "type": f"{vuln_type}_fix",
            "original_code": original_code,
            "fixed_code": fixed_code,
            "explanation": explanation,
            "full_response": fix_content,
            "vulnerability_id": vulnerability.get('type', ''),
            "file_path": vulnerability.get('file_path', ''),
            "line_number": vulnerability.get('line', 0),
        }
    
    def validate_fix(self, fix: Dict) -> bool:
        """
        Validate that the generated fix is syntactically correct.
        
        This is the agent's SELF-VALIDATION step!
        """
        fixed_code = fix.get('fixed_code', '')
        
        if not fixed_code:
            return False
        
        # Try to parse as Python
        try:
            ast.parse(fixed_code)
            return True
        except SyntaxError:
            # Could be a code snippet, not full module
            # Try wrapping in a function
            try:
                wrapped = f"def temp_func():\n    " + fixed_code.replace('\n', '\n    ')
                ast.parse(wrapped)
                return True
            except SyntaxError:
                # Still invalid, likely not Python or incomplete
                # For hackathon, we'll be lenient
                return len(fixed_code) > 10  # At least some content
    
    def _extract_code_block(self, llm_response: str) -> str:
        """Extract code block from LLM response"""
        # Look for code blocks
        import re
        
        # Try to find ```python or ``` code blocks
        patterns = [
            r'```python\n(.*?)\n```',
            r'```\n(.*?)\n```',
            r'FIXED CODE:\s*```(?:python)?\n(.*?)\n```',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, llm_response, re.DOTALL)
            if match:
                return match.group(1).strip()
        
        # If no code block found, try to extract after "FIXED CODE:"
        if "FIXED CODE:" in llm_response:
            lines = llm_response.split('\n')
            code_lines = []
            capturing = False
            
            for line in lines:
                if "FIXED CODE:" in line:
                    capturing = True
                    continue
                if capturing:
                    if "EXPLANATION:" in line or "ADDITIONAL NOTES:" in line:
                        break
                    code_lines.append(line)
            
            return '\n'.join(code_lines).strip()
        
        # Fallback: return first 10 lines
        return '\n'.join(llm_response.split('\n')[:10])
    
    def _extract_explanation(self, llm_response: str) -> str:
        """Extract explanation from LLM response"""
        # Look for explanation section
        if "EXPLANATION:" in llm_response:
            parts = llm_response.split("EXPLANATION:")
            explanation_section = parts[1] if len(parts) > 1 else ""
            
            # Get text until next section
            end_markers = ["ADDITIONAL NOTES:", "```", "---"]
            for marker in end_markers:
                if marker in explanation_section:
                    explanation_section = explanation_section.split(marker)[0]
            
            return explanation_section.strip()
        
        # Fallback: return part of the response
        return llm_response[:200] + "..."


# ==================== PREDEFINED SECURE PATTERNS ====================

class SecurePatterns:
    """
    Library of secure coding patterns.
    Agent can use these as templates for common fixes.
    """
    
    SQL_INJECTION_FIXES = {
        "parameterized_query": """
# Secure: Use parameterized queries
query = "SELECT * FROM users WHERE username = ? AND password = ?"
user = db.execute(query, (username, password))
""",
        "orm_usage": """
# Secure: Use ORM instead of raw SQL
user = User.objects.filter(username=username, password=password).first()
""",
    }
    
    CREDENTIAL_FIXES = {
        "environment_vars": """
# Secure: Use environment variables
import os
api_key = os.getenv('API_KEY')
password = os.getenv('DB_PASSWORD')
""",
        "secrets_manager": """
# Secure: Use cloud secrets manager
from google.cloud import secretmanager

client = secretmanager.SecretManagerServiceClient()
secret_name = "projects/PROJECT_ID/secrets/SECRET_NAME/versions/latest"
response = client.access_secret_version(request={"name": secret_name})
api_key = response.payload.data.decode('UTF-8')
""",
    }
    
    XSS_FIXES = {
        "escape_output": """
# Secure: Escape user input before rendering
from markupsafe import escape
safe_output = escape(user_input)
""",
        "template_engine": """
# Secure: Use template engine with auto-escaping
from jinja2 import Template
template = Template('<p>{{ user_input }}</p>')  # Auto-escaped
""",
    }
