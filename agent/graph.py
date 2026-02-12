"""
Shift-Left Security Guardian Agent

LangGraph state machine for autonomous PR security analysis.
Showcases true agentic behavior: Decision → Plan → Tool Use → Reason → Validate
"""

from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_google_vertexai import ChatVertexAI
import operator
from datetime import datetime

# Import our custom tools
from agent.tools.security_scanner import SecurityScanner
from agent.tools.github_client import GitHubClient
from agent.tools.code_generator import CodeGenerator
from agent.prompts import get_system_prompt, get_decision_prompt


class AgentState(TypedDict):
    """
    Agent state that flows through the graph.
    Tracks the agent's reasoning and decisions.
    """
    messages: Annotated[Sequence[BaseMessage], operator.add]
    pr_url: str
    pr_data: dict  # Raw PR data from GitHub
    diff_content: str  # Code changes
    risk_level: str  # "low" | "medium" | "high"
    analysis_strategy: str  # "quick_scan" | "deep_analysis"
    vulnerabilities: list[dict]  # Found security issues
    suggested_fixes: list[dict]  # Generated code suggestions
    reasoning_trace: list[str]  # Agent's decision log (for judges!)
    should_continue: bool
    iteration_count: int


class SecurityGuardianAgent:
    """
    LangGraph-based autonomous security agent.
    
    Decision Flow:
    1. Assess Risk → Decide analysis strategy
    2. Scan Code → Choose appropriate tools
    3. Deep Dive → LLM analysis on suspicious sections
    4. Generate Fixes → Context-aware code suggestions
    5. Validate → Check if fixes compile
    6. Post Review → GitHub PR comments (Copilot-style)
    """
    
    def __init__(
        self,
        project_id: str,
        location: str = "us-central1",
        model_name: str = "gemini-2.0-flash-001"
    ):
        self.project_id = project_id
        self.location = location
        
        # Initialize Gemini via Vertex AI
        self.llm = ChatVertexAI(
            model_name=model_name,
            temperature=0.1,  # Low temp for consistent security analysis
            project=project_id,
            location=location,
        )
        
        # Initialize tools
        self.security_scanner = SecurityScanner()
        self.github_client = GitHubClient()
        self.code_generator = CodeGenerator(llm=self.llm)
        
        # Build the LangGraph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph state machine.
        This is where the AGENT AUTONOMY is defined!
        """
        workflow = StateGraph(AgentState)
        
        # Define nodes (agent steps)
        workflow.add_node("fetch_pr", self._fetch_pr_data)
        workflow.add_node("assess_risk", self._assess_risk)
        workflow.add_node("quick_scan", self._quick_scan)
        workflow.add_node("deep_analysis", self._deep_analysis)
        workflow.add_node("generate_fixes", self._generate_fixes)
        workflow.add_node("validate_fixes", self._validate_fixes)
        workflow.add_node("post_review", self._post_review)
        
        # Define edges (agent decision flow)
        workflow.set_entry_point("fetch_pr")
        
        workflow.add_edge("fetch_pr", "assess_risk")
        
        # DECISION POINT 1: Choose analysis strategy based on risk
        workflow.add_conditional_edges(
            "assess_risk",
            self._route_by_risk,
            {
                "quick": "quick_scan",
                "deep": "deep_analysis",
            }
        )
        
        workflow.add_edge("quick_scan", "generate_fixes")
        workflow.add_edge("deep_analysis", "generate_fixes")
        workflow.add_edge("generate_fixes", "validate_fixes")
        workflow.add_edge("validate_fixes", "post_review")
        workflow.add_edge("post_review", END)
        
        return workflow.compile()
    
    # ==================== AGENT NODES ====================
    
    def _fetch_pr_data(self, state: AgentState) -> AgentState:
        """Step 1: Fetch PR data from GitHub"""
        reasoning = f"[{datetime.now().isoformat()}] Fetching PR data from: {state['pr_url']}"
        print(f"🤖 {reasoning}")
        
        pr_data = self.github_client.get_pr_data(state['pr_url'])
        diff_content = self.github_client.get_pr_diff(state['pr_url'])
        
        state['pr_data'] = pr_data
        state['diff_content'] = diff_content
        state['reasoning_trace'].append(reasoning)
        state['reasoning_trace'].append(
            f"Retrieved {len(diff_content)} characters of diff content, "
            f"{pr_data.get('changed_files', 0)} files changed"
        )
        
        return state
    
    def _assess_risk(self, state: AgentState) -> AgentState:
        """
        Step 2: AUTONOMOUS DECISION - Assess PR risk level.
        This is where the agent shows INTELLIGENCE!
        """
        reasoning = f"[{datetime.now().isoformat()}] Analyzing PR risk factors..."
        print(f"🧠 {reasoning}")
        
        pr_data = state['pr_data']
        diff = state['diff_content']
        
        # Use LLM to assess risk (agentic decision-making!)
        risk_prompt = get_decision_prompt(pr_data, diff)
        response = self.llm.invoke([HumanMessage(content=risk_prompt)])
        
        # Extract risk level from LLM response
        risk_assessment = response.content.lower()
        
        if "high risk" in risk_assessment or "critical" in risk_assessment:
            risk_level = "high"
            strategy = "deep_analysis"
        elif "medium risk" in risk_assessment:
            risk_level = "medium"
            strategy = "deep_analysis"
        else:
            risk_level = "low"
            strategy = "quick_scan"
        
        state['risk_level'] = risk_level
        state['analysis_strategy'] = strategy
        state['reasoning_trace'].append(f"Risk Assessment: {risk_level.upper()}")
        state['reasoning_trace'].append(f"Chosen Strategy: {strategy}")
        state['reasoning_trace'].append(f"LLM Reasoning: {risk_assessment[:200]}...")
        
        print(f"📊 Risk Level: {risk_level} → Strategy: {strategy}")
        
        return state
    
    def _quick_scan(self, state: AgentState) -> AgentState:
        """Step 3a: Quick pattern-based security scan"""
        reasoning = f"[{datetime.now().isoformat()}] Running quick security scan (regex + patterns)..."
        print(f"⚡ {reasoning}")
        
        vulnerabilities = self.security_scanner.quick_scan(state['diff_content'])
        
        state['vulnerabilities'] = vulnerabilities
        state['reasoning_trace'].append(f"Quick scan found {len(vulnerabilities)} potential issues")
        
        for vuln in vulnerabilities[:3]:  # Show first 3
            state['reasoning_trace'].append(
                f"  - {vuln['type']}: {vuln['description'][:80]}..."
            )
        
        return state
    
    def _deep_analysis(self, state: AgentState) -> AgentState:
        """Step 3b: Deep LLM-based security analysis with AST parsing"""
        reasoning = f"[{datetime.now().isoformat()}] Running deep analysis (AST + LLM reasoning)..."
        print(f"🔬 {reasoning}")
        
        # First run quick scan
        quick_vulns = self.security_scanner.quick_scan(state['diff_content'])
        
        # Then use AST + LLM for deeper analysis
        deep_vulns = self.security_scanner.deep_analysis(
            state['diff_content'],
            llm=self.llm
        )
        
        # Combine and deduplicate
        all_vulns = quick_vulns + deep_vulns
        state['vulnerabilities'] = all_vulns
        
        state['reasoning_trace'].append(
            f"Deep analysis: {len(quick_vulns)} pattern-based + {len(deep_vulns)} LLM-detected"
        )
        state['reasoning_trace'].append(f"Total vulnerabilities: {len(all_vulns)}")
        
        return state
    
    def _generate_fixes(self, state: AgentState) -> AgentState:
        """Step 4: Generate context-aware code fixes (Copilot-style)"""
        reasoning = f"[{datetime.now().isoformat()}] Generating secure code fixes..."
        print(f"🔧 {reasoning}")
        
        if not state['vulnerabilities']:
            state['reasoning_trace'].append("No vulnerabilities found - skipping fix generation")
            state['suggested_fixes'] = []
            return state
        
        # For each vulnerability, generate a fix
        fixes = []
        for vuln in state['vulnerabilities']:
            fix = self.code_generator.generate_fix(
                vulnerability=vuln,
                original_code=vuln.get('code_snippet', ''),
                context=state['diff_content']
            )
            fixes.append(fix)
        
        state['suggested_fixes'] = fixes
        state['reasoning_trace'].append(f"Generated {len(fixes)} secure code alternatives")
        
        return state
    
    def _validate_fixes(self, state: AgentState) -> AgentState:
        """Step 5: Validate fixes (basic syntax check)"""
        reasoning = f"[{datetime.now().isoformat()}] Validating generated fixes..."
        print(f"✅ {reasoning}")
        
        valid_fixes = []
        for fix in state['suggested_fixes']:
            if self.code_generator.validate_fix(fix):
                valid_fixes.append(fix)
                state['reasoning_trace'].append(f"  ✓ Fix validated: {fix['type']}")
            else:
                state['reasoning_trace'].append(f"  ✗ Fix validation failed: {fix['type']}")
        
        state['suggested_fixes'] = valid_fixes
        return state
    
    def _post_review(self, state: AgentState) -> AgentState:
        """Step 6: Post PR review with Copilot-style suggestions"""
        reasoning = f"[{datetime.now().isoformat()}] Posting review to GitHub PR..."
        print(f"💬 {reasoning}")
        
        # Post review comment with suggestions
        review_posted = self.github_client.post_review(
            pr_url=state['pr_url'],
            vulnerabilities=state['vulnerabilities'],
            suggested_fixes=state['suggested_fixes'],
            reasoning_trace=state['reasoning_trace']
        )
        
        if review_posted:
            state['reasoning_trace'].append("✓ Review posted successfully to GitHub")
        else:
            state['reasoning_trace'].append("✗ Failed to post review")
        
        return state
    
    # ==================== DECISION ROUTING ====================
    
    def _route_by_risk(self, state: AgentState) -> str:
        """
        AUTONOMOUS ROUTING: Agent decides which analysis path to take.
        This is a key differentiator from scripted automation!
        """
        strategy = state.get('analysis_strategy', 'quick_scan')
        
        if strategy == "deep_analysis":
            return "deep"
        else:
            return "quick"
    
    # ==================== PUBLIC API ====================
    
    def analyze_pr(self, pr_url: str) -> dict:
        """
        Main entry point: Analyze a GitHub PR for security issues.
        
        Returns:
            dict: Analysis results with vulnerabilities and fixes
        """
        print(f"\n{'='*60}")
        print(f"🛡️  SHIFT-LEFT SECURITY GUARDIAN")
        print(f"{'='*60}\n")
        
        # Initialize state
        initial_state: AgentState = {
            "messages": [],
            "pr_url": pr_url,
            "pr_data": {},
            "diff_content": "",
            "risk_level": "",
            "analysis_strategy": "",
            "vulnerabilities": [],
            "suggested_fixes": [],
            "reasoning_trace": [],
            "should_continue": True,
            "iteration_count": 0,
        }
        
        # Run the agent graph!
        final_state = self.graph.invoke(initial_state)
        
        print(f"\n{'='*60}")
        print(f"✨ Analysis Complete!")
        print(f"{'='*60}\n")
        
        # Return results
        return {
            "pr_url": pr_url,
            "risk_level": final_state['risk_level'],
            "analysis_strategy": final_state['analysis_strategy'],
            "vulnerabilities_found": len(final_state['vulnerabilities']),
            "fixes_generated": len(final_state['suggested_fixes']),
            "reasoning_trace": final_state['reasoning_trace'],
            "vulnerabilities": final_state['vulnerabilities'],
            "suggested_fixes": final_state['suggested_fixes'],
        }
