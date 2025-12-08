"""
Agentic AI System - The Brain of Study Buddy
This module implements an intelligent agent that can:
- Reason about user requests
- Plan multi-step actions
- Use appropriate tools autonomously
- Learn from context and adapt
"""

import json
from typing import Dict, List, Any, Optional
from utils.gemini_helper import generate_response


class StudyBuddyAgent:
    """
    Main Agentic AI controller that thinks, plans, and executes tasks autonomously.
    """
    
    def __init__(self, rag_system=None, pdf_content: str = ""):
        """
        Initialize the agent with available resources.
        
        Args:
            rag_system: RAGSystem instance for document retrieval
            pdf_content: Full PDF text content if available
        """
        self.rag_system = rag_system
        self.pdf_content = pdf_content
        self.conversation_history = []
        self.tools_used = []
        self.current_plan = None
        
    def think(self, user_request: str, conversation_context: str = "") -> Dict[str, Any]:
        """
        Agent's thinking process - analyzes request and creates a plan.
        
        Args:
            user_request: What the user wants
            conversation_context: Recent chat history
            
        Returns:
            Dict with plan, reasoning, and suggested tools
        """
        thinking_prompt = f"""
You are the reasoning brain of Study Buddy AI Agent.

CONVERSATION CONTEXT:
{conversation_context}

USER REQUEST:
{user_request}

AVAILABLE RESOURCES:
- PDF Content: {"Available" if self.pdf_content or (self.rag_system and self.rag_system.is_ready()) else "Not available"}
- RAG System: {"Active" if self.rag_system and self.rag_system.is_ready() else "Inactive"}

AVAILABLE TOOLS:
1. concept_explainer - Explains academic concepts in simple terms
2. content_summarizer - Summarizes long text or PDF content
3. quiz_generator - Creates quizzes on topics
4. question_solver - Solves exam-style questions
5. answer_evaluator - Evaluates and grades user's answers
6. pdf_retriever - Retrieves relevant content from uploaded PDFs

YOUR TASK:
Analyze the user's request and create a plan. Think step by step:

1. What does the user actually want?
2. Is this a simple task (one tool) or complex (multiple tools)?
3. What information do I need from the PDF (if any)?
4. What's the best sequence of tools to use?
5. Should I be proactive and suggest additional help?

RESPOND IN THIS JSON FORMAT:
{{
    "user_intent": "Brief description of what user wants",
    "complexity": "simple" or "complex",
    "tools_needed": ["tool1", "tool2", ...],
    "execution_plan": [
        {{"step": 1, "action": "description", "tool": "tool_name", "reason": "why this step"}},
        ...
    ],
    "proactive_suggestions": ["suggestion1", "suggestion2", ...],
    "confidence": 0.0 to 1.0
}}

Think carefully and respond ONLY with valid JSON.
"""
        
        try:
            response = generate_response(thinking_prompt.strip())
            # Extract JSON from response (handle markdown code blocks)
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            plan = json.loads(response)
            self.current_plan = plan
            return plan
        except Exception as e:
            # Fallback plan if JSON parsing fails
            return {
                "user_intent": user_request,
                "complexity": "simple",
                "tools_needed": ["concept_explainer"],
                "execution_plan": [{"step": 1, "action": "Respond to user", "tool": "concept_explainer", "reason": "Direct response"}],
                "proactive_suggestions": [],
                "confidence": 0.5,
                "error": str(e)
            }
    
    def execute(self, user_request: str, conversation_context: str = "") -> Dict[str, Any]:
        """
        Main execution method - thinks, plans, and executes the task.
        
        Args:
            user_request: User's input
            conversation_context: Recent conversation history
            
        Returns:
            Dict containing response and metadata
        """
        # Step 1: Think and plan
        plan = self.think(user_request, conversation_context)
        
        # Step 2: Execute the plan
        results = []
        for step in plan.get("execution_plan", []):
            tool_name = step.get("tool")
            action = step.get("action")
            
            # Execute the tool
            result = self._execute_tool(tool_name, user_request, conversation_context)
            results.append({
                "step": step.get("step"),
                "action": action,
                "tool": tool_name,
                "result": result
            })
            self.tools_used.append(tool_name)
        
        # Step 3: Synthesize final response
        final_response = self._synthesize_response(user_request, results, plan)
        
        return {
            "response": final_response,
            "plan": plan,
            "tools_used": self.tools_used,
            "thinking_process": plan.get("execution_plan", []),
            "suggestions": plan.get("proactive_suggestions", [])
        }
    
    def _execute_tool(self, tool_name: str, user_input: str, context: str) -> str:
        """
        Execute a specific tool based on its name.
        
        Args:
            tool_name: Name of the tool to execute
            user_input: User's original request
            context: Conversation context
            
        Returns:
            Tool execution result
        """
        from core.explainer import explain_concept
        from core.summarizer import summarize_text
        from core.quizzer import generate_questions, solve_questions, evaluate_answers
        
        # Retrieve PDF context if needed
        pdf_context = ""
        if self.rag_system and self.rag_system.is_ready():
            pdf_context = self.rag_system.retrieve_context(user_input, k=3)
        elif self.pdf_content:
            pdf_context = self.pdf_content[:8000]
        
        # Execute appropriate tool
        if tool_name == "concept_explainer":
            return explain_concept(user_input, context, self.rag_system, self.pdf_content)
        
        elif tool_name == "content_summarizer":
            return summarize_text(
                text=pdf_context or user_input,
                previous_context=context,
                user_focus=user_input,
                extra_instruction="",
                rag_system=self.rag_system
            )
        
        elif tool_name == "quiz_generator":
            return generate_questions(user_input, context, self.rag_system)
        
        elif tool_name == "question_solver":
            return solve_questions(user_input, context, 100, self.rag_system)
        
        elif tool_name == "answer_evaluator":
            # This needs both questions and answers - extract from context
            return evaluate_answers(user_input, "", context, self.rag_system)
        
        elif tool_name == "pdf_retriever":
            if self.rag_system and self.rag_system.is_ready():
                return self.rag_system.retrieve_context(user_input, k=5)
            return pdf_context
        
        else:
            return f"Tool {tool_name} not found. Using default response."
    
    def _synthesize_response(self, user_request: str, results: List[Dict], plan: Dict) -> str:
        """
        Synthesize all tool results into a coherent final response.
        
        Args:
            user_request: Original user request
            results: List of tool execution results
            plan: The execution plan
            
        Returns:
            Final synthesized response
        """
        if len(results) == 1:
            # Simple single-tool response
            response = results[0]["result"]
        else:
            # Complex multi-tool response - combine intelligently
            synthesis_prompt = f"""
You are Study Buddy AI Agent synthesizing multiple tool results into a coherent response.

USER REQUEST:
{user_request}

EXECUTION RESULTS:
{json.dumps(results, indent=2)}

YOUR TASK:
Create a natural, flowing response that:
1. Directly addresses the user's request
2. Integrates all tool results smoothly
3. Uses clear section headings if multiple topics
4. Maintains an encouraging, helpful tone
5. Includes the proactive suggestions at the end if relevant

Respond naturally, not as JSON. Use Markdown formatting.
"""
            response = generate_response(synthesis_prompt.strip())
        
        # Add proactive suggestions if any
        suggestions = plan.get("proactive_suggestions", [])
        if suggestions:
            response += "\n\n---\n\n💡 **I can also help you with:**\n"
            for suggestion in suggestions:
                response += f"- {suggestion}\n"
        
        return response
    
    def reflect(self, response: str, user_feedback: Optional[str] = None) -> Dict[str, Any]:
        """
        Agent reflects on its own output to improve quality.
        
        Args:
            response: The response generated
            user_feedback: Optional user feedback
            
        Returns:
            Reflection analysis and improvement suggestions
        """
        reflection_prompt = f"""
You are Study Buddy's self-reflection module.

RESPONSE GENERATED:
{response[:1000]}...

USER FEEDBACK (if any):
{user_feedback or "None yet"}

Reflect on this response:
1. Was it clear and well-structured?
2. Did it fully address the request?
3. Was the tone appropriate?
4. What could be improved?
5. Should any additional help be offered?

Rate the response quality (1-10) and suggest improvements.

RESPOND IN JSON:
{{
    "quality_score": 1-10,
    "strengths": ["strength1", ...],
    "weaknesses": ["weakness1", ...],
    "improvements": ["improvement1", ...],
    "should_retry": true/false
}}
"""
        
        try:
            reflection = generate_response(reflection_prompt.strip())
            if "```json" in reflection:
                reflection = reflection.split("```json")[1].split("```")[0].strip()
            return json.loads(reflection)
        except:
            return {
                "quality_score": 7,
                "strengths": ["Completed the task"],
                "weaknesses": [],
                "improvements": [],
                "should_retry": False
            }
    
    def get_thinking_trace(self) -> List[str]:
        """
        Returns the agent's thinking trace for transparency.
        
        Returns:
            List of thinking steps
        """
        if not self.current_plan:
            return []
        
        trace = [f"**Intent:** {self.current_plan.get('user_intent', 'Unknown')}"]
        trace.append(f"**Complexity:** {self.current_plan.get('complexity', 'unknown')}")
        trace.append(f"**Tools:** {', '.join(self.current_plan.get('tools_needed', []))}")
        
        for step in self.current_plan.get("execution_plan", []):
            trace.append(f"**Step {step['step']}:** {step['action']} (using {step['tool']})")
        
        return trace
