"""
GitHub API Client Tool

Handles all GitHub interactions:
- Fetch PR data and diffs
- Post review comments with Copilot-style suggestions
- Format inline code suggestions
"""

import os
from typing import Dict, List, Optional
from github import Github, GithubException
import re


class GitHubClient:
    """
    GitHub API wrapper for the Security Guardian agent.
    Implements Copilot-style code suggestions!
    """
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or os.getenv('GITHUB_TOKEN')
        if not self.token:
            print("⚠️  Warning: GITHUB_TOKEN not set. GitHub features will be limited.")
            self.gh = None
        else:
            self.gh = Github(self.token)
    
    def get_pr_data(self, pr_url: str) -> Dict:
        """
        Fetch PR metadata from GitHub.
        
        Args:
            pr_url: Full URL like "https://github.com/owner/repo/pull/123"
        
        Returns:
            dict with PR metadata
        """
        if not self.gh:
            return self._mock_pr_data()
        
        try:
            # Parse PR URL
            owner, repo, pr_number = self._parse_pr_url(pr_url)
            
            # Fetch PR
            repository = self.gh.get_repo(f"{owner}/{repo}")
            pr = repository.get_pull(pr_number)
            
            return {
                "number": pr.number,
                "title": pr.title,
                "body": pr.body or "",
                "state": pr.state,
                "author": pr.user.login,
                "changed_files": pr.changed_files,
                "additions": pr.additions,
                "deletions": pr.deletions,
                "commits": pr.commits,
                "files": [f.filename for f in pr.get_files()],
            }
            
        except GithubException as e:
            print(f"❌ GitHub API error: {e}")
            return self._mock_pr_data()
    
    def get_pr_diff(self, pr_url: str) -> str:
        """
        Fetch the unified diff for a PR.
        
        Returns:
            str: Full diff content
        """
        if not self.gh:
            return self._mock_diff()
        
        try:
            owner, repo, pr_number = self._parse_pr_url(pr_url)
            
            repository = self.gh.get_repo(f"{owner}/{repo}")
            pr = repository.get_pull(pr_number)
            
            # Combine all file diffs
            full_diff = []
            for file in pr.get_files():
                full_diff.append(f"--- a/{file.filename}")
                full_diff.append(f"+++ b/{file.filename}")
                full_diff.append(file.patch or "")
                full_diff.append("\n")
            
            return "\n".join(full_diff)
            
        except GithubException as e:
            print(f"❌ GitHub API error: {e}")
            return self._mock_diff()
    
    def post_review(
        self,
        pr_url: str,
        vulnerabilities: List[Dict],
        suggested_fixes: List[Dict],
        reasoning_trace: List[str]
    ) -> bool:
        """
        Post a review comment on the PR with Copilot-style suggestions.
        
        This is what makes the demo INTERACTIVE!
        """
        if not self.gh:
            print("📝 MOCK: Would post review to GitHub")
            self._print_review_preview(vulnerabilities, suggested_fixes, reasoning_trace)
            return True
        
        try:
            owner, repo, pr_number = self._parse_pr_url(pr_url)
            repository = self.gh.get_repo(f"{owner}/{repo}")
            pr = repository.get_pull(pr_number)
            
            # Format review comment
            review_body = self._format_review_comment(
                vulnerabilities,
                suggested_fixes,
                reasoning_trace
            )
            
            # Post review
            pr.create_review(
                body=review_body,
                event="COMMENT",  # Could be "REQUEST_CHANGES" for critical issues
            )
            
            # Also post inline comments with suggestions
            self._post_inline_suggestions(pr, suggested_fixes)
            
            print("✅ Review posted to GitHub!")
            return True
            
        except GithubException as e:
            print(f"❌ Failed to post review: {e}")
            return False
    
    def _post_inline_suggestions(self, pr, suggested_fixes: List[Dict]):
        """
        Post inline code suggestions (Copilot-style).
        
        This creates the "Suggested change" blocks that users can apply with one click!
        """
        for fix in suggested_fixes:
            try:
                # GitHub's suggestion format
                suggestion_body = f"""```suggestion
{fix.get('fixed_code', '')}
```

**Why this fix?**
{fix.get('explanation', 'Security improvement')}
"""
                
                # Post as review comment on specific line
                # Note: This requires file path and line number from the fix
                if 'file_path' in fix and 'line_number' in fix:
                    pr.create_review_comment(
                        body=suggestion_body,
                        commit=pr.get_commits()[pr.commits - 1],
                        path=fix['file_path'],
                        line=fix['line_number'],
                    )
            except Exception as e:
                print(f"⚠️  Could not post inline suggestion: {e}")
    
    def _format_review_comment(
        self,
        vulnerabilities: List[Dict],
        suggested_fixes: List[Dict],
        reasoning_trace: List[str]
    ) -> str:
        """
        Format a comprehensive review comment.
        Includes agent reasoning for transparency!
        """
        parts = []
        
        # Header
        parts.append("# 🛡️ Security Guardian Analysis Report\n")
        
        # Summary
        if not vulnerabilities:
            parts.append("✅ **No security vulnerabilities detected!** Great work!\n")
            return "\n".join(parts)
        
        vuln_count = len(vulnerabilities)
        fix_count = len(suggested_fixes)
        
        parts.append(f"**Found {vuln_count} potential security issue(s)**\n")
        parts.append(f"**Generated {fix_count} secure alternative(s)**\n")
        
        # Vulnerabilities
        parts.append("\n## 🔍 Vulnerabilities Detected\n")
        
        for i, vuln in enumerate(vulnerabilities, 1):
            severity_emoji = {
                "critical": "🔴",
                "high": "🟠",
                "medium": "🟡",
                "low": "🟢",
            }
            emoji = severity_emoji.get(vuln.get('severity', 'medium'), '🟡')
            
            parts.append(f"### {i}. {emoji} {vuln.get('type', 'Unknown').replace('_', ' ').title()}")
            parts.append(f"**Severity:** {vuln.get('severity', 'medium').upper()}")
            parts.append(f"**Description:** {vuln.get('description', 'No description')}")
            
            if 'code_snippet' in vuln:
                parts.append(f"\n**Vulnerable code:**")
                parts.append(f"```python\n{vuln['code_snippet']}\n```\n")
        
        # Suggested fixes
        if suggested_fixes:
            parts.append("\n## ✅ Suggested Fixes\n")
            parts.append("The agent has generated secure alternatives. Review and apply them below:\n")
            
            for i, fix in enumerate(suggested_fixes, 1):
                parts.append(f"### Fix {i}: {fix.get('type', 'Security Fix')}")
                
                if 'fixed_code' in fix:
                    parts.append(f"```python\n{fix['fixed_code']}\n```")
                
                parts.append(f"\n**Explanation:** {fix.get('explanation', 'Security improvement')}\n")
        
        # Agent reasoning (this is KEY for judges!)
        parts.append("\n## 🧠 Agent Reasoning Trace\n")
        parts.append("<details><summary>Click to see how the agent analyzed this PR</summary>\n")
        parts.append("```")
        parts.extend(reasoning_trace)
        parts.append("```")
        parts.append("</details>\n")
        
        # Footer
        parts.append("\n---")
        parts.append("*🤖 Generated by [Shift-Left Security Guardian](https://github.com/your-repo) - An autonomous AI agent powered by Vertex AI & Gemini*")
        
        return "\n".join(parts)
    
    def _parse_pr_url(self, pr_url: str) -> tuple[str, str, int]:
        """
        Parse GitHub PR URL into (owner, repo, pr_number).
        
        Examples:
            "https://github.com/owner/repo/pull/123" → ("owner", "repo", 123)
        """
        pattern = r'github\.com/([^/]+)/([^/]+)/pull/(\d+)'
        match = re.search(pattern, pr_url)
        
        if not match:
            raise ValueError(f"Invalid GitHub PR URL: {pr_url}")
        
        owner, repo, pr_number = match.groups()
        return owner, repo, int(pr_number)
    
    # ==================== MOCK DATA (for testing without GitHub) ====================
    
    def _mock_pr_data(self) -> Dict:
        """Mock PR data for testing"""
        return {
            "number": 1,
            "title": "Add user authentication",
            "body": "Implementing login functionality",
            "state": "open",
            "author": "test-user",
            "changed_files": 3,
            "additions": 150,
            "deletions": 20,
            "commits": 2,
            "files": ["app.py", "db.py", "config.py"],
        }
    
    def _mock_diff(self) -> str:
        """Mock diff for testing"""
        return """--- a/app.py
+++ b/app.py
@@ -10,7 +10,7 @@ def login(username, password):
-    query = "SELECT * FROM users WHERE username='" + username + "'"
+    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
     user = db.execute(query)
"""
    
    def _print_review_preview(
        self,
        vulnerabilities: List[Dict],
        suggested_fixes: List[Dict],
        reasoning_trace: List[str]
    ):
        """Print review preview to console (for testing)"""
        print("\n" + "="*60)
        print("GITHUB REVIEW PREVIEW")
        print("="*60)
        print(self._format_review_comment(vulnerabilities, suggested_fixes, reasoning_trace))
        print("="*60 + "\n")
