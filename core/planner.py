"""
Advanced Planning System for Agentic AI
Handles complex multi-step reasoning and task decomposition.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json
from utils.gemini_helper import generate_response


@dataclass
class PlanStep:
    """Represents a single step in an execution plan."""
    step_number: int
    action: str
    tool: str
    reason: str
    dependencies: List[int]  # Which previous steps must complete first
    estimated_time: str = "quick"  # quick, medium, long
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "step": self.step_number,
            "action": self.action,
            "tool": self.tool,
            "reason": self.reason,
            "dependencies": self.dependencies,
            "estimated_time": self.estimated_time
        }


@dataclass
class ExecutionPlan:
    """Complete execution plan with metadata."""
    user_intent: str
    complexity: str  # simple, moderate, complex
    steps: List[PlanStep]
    proactive_suggestions: List[str]
    confidence: float
    reasoning: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "user_intent": self.user_intent,
            "complexity": self.complexity,
            "steps": [step.to_dict() for step in self.steps],
            "proactive_suggestions": self.proactive_suggestions,
            "confidence": self.confidence,
            "reasoning": self.reasoning
        }


class AgentPlanner:
    """
    Advanced planning system that breaks down complex tasks into steps.
    """
    
    def __init__(self, tool_registry):
        """
        Initialize planner with available tools.
        
        Args:
            tool_registry: ToolRegistry instance with available tools
        """
        self.tool_registry = tool_registry
        self.planning_history = []
    
    def create_plan(
        self, 
        user_request: str, 
        context: str = "", 
        has_pdf: bool = False,
        chat_history: List[Dict] = None
    ) -> ExecutionPlan:
        """
        Create an execution plan for the user's request.
        
        Args:
            user_request: User's input/question
            context: Recent conversation context
            has_pdf: Whether PDF content is available
            chat_history: Full chat history for pattern detection
            
        Returns:
            ExecutionPlan with steps and reasoning
        """
        # Get available tools info
        tools_info = self.tool_registry.get_tool_descriptions()
        
        # Analyze request complexity
        complexity = self._analyze_complexity(user_request)
        
        # Generate the plan
        planning_prompt = f"""
You are an expert AI planner for Study Buddy. Your job is to create a step-by-step execution plan.

USER REQUEST:
{user_request}

RECENT CONTEXT:
{context}

AVAILABLE TOOLS:
{tools_info}

PDF AVAILABLE: {has_pdf}

ANALYZE THE REQUEST:
1. What is the user's main goal?
2. Is this simple (1 tool) or complex (multiple tools)?
3. What's the logical sequence of steps?
4. Can we be proactive and offer additional value?

PLANNING RULES:
- Simple requests (e.g., "explain X") → 1 step
- Moderate requests (e.g., "explain X and quiz me") → 2-3 steps
- Complex requests (e.g., "help me prepare for exam") → 4+ steps
- Always consider if PDF context should be retrieved first
- Be proactive: suggest next helpful actions
- If user says "exam tomorrow" or "test preparation", create comprehensive plan

CREATE A PLAN IN THIS JSON FORMAT:
{{
    "user_intent": "Clear statement of what user wants",
    "complexity": "simple|moderate|complex",
    "reasoning": "Brief explanation of your planning logic",
    "steps": [
        {{
            "step": 1,
            "action": "Brief description of this step",
            "tool": "exact_tool_name",
            "reason": "Why this step is needed",
            "dependencies": [],
            "estimated_time": "quick|medium|long"
        }}
    ],
    "proactive_suggestions": [
        "Suggestion 1 (what else you could help with)",
        "Suggestion 2"
    ],
    "confidence": 0.85
}}

Respond ONLY with valid JSON. Be smart and proactive!
"""
        
        try:
            response = generate_response(planning_prompt.strip())
            
            # Extract JSON
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            
            plan_data = json.loads(response)
            
            # Convert to ExecutionPlan object
            steps = [
                PlanStep(
                    step_number=s["step"],
                    action=s["action"],
                    tool=s["tool"],
                    reason=s.get("reason", ""),
                    dependencies=s.get("dependencies", []),
                    estimated_time=s.get("estimated_time", "quick")
                )
                for s in plan_data.get("steps", [])
            ]
            
            plan = ExecutionPlan(
                user_intent=plan_data.get("user_intent", user_request),
                complexity=plan_data.get("complexity", "simple"),
                steps=steps,
                proactive_suggestions=plan_data.get("proactive_suggestions", []),
                confidence=plan_data.get("confidence", 0.7),
                reasoning=plan_data.get("reasoning", "Plan created")
            )
            
            self.planning_history.append(plan)
            return plan
            
        except Exception as e:
            # Fallback plan
            return self._create_fallback_plan(user_request, has_pdf)
    
    def _analyze_complexity(self, user_request: str) -> str:
        """
        Quickly analyze request complexity.
        
        Args:
            user_request: User's input
            
        Returns:
            Complexity level: simple, moderate, or complex
        """
        request_lower = user_request.lower()
        
        # Complex indicators
        complex_indicators = [
            "exam", "test preparation", "prepare for", "study plan",
            "help me learn", "master", "comprehensive", "everything about"
        ]
        
        # Moderate indicators (multiple actions)
        moderate_indicators = [
            " and ", " then ", "also", "after that", "quiz me",
            "test me", "check my"
        ]
        
        if any(ind in request_lower for ind in complex_indicators):
            return "complex"
        
        if any(ind in request_lower for ind in moderate_indicators):
            return "moderate"
        
        return "simple"
    
    def _create_fallback_plan(self, user_request: str, has_pdf: bool) -> ExecutionPlan:
        """
        Create a simple fallback plan if main planning fails.
        
        Args:
            user_request: User's request
            has_pdf: PDF availability
            
        Returns:
            Simple ExecutionPlan
        """
        # Suggest appropriate tool
        suggested_tools = self.tool_registry.suggest_tools(user_request, has_pdf)
        primary_tool = suggested_tools[0] if suggested_tools else "concept_explainer"
        
        step = PlanStep(
            step_number=1,
            action="Respond to user request",
            tool=primary_tool,
            reason="Direct response to user query",
            dependencies=[],
            estimated_time="quick"
        )
        
        return ExecutionPlan(
            user_intent=user_request,
            complexity="simple",
            steps=[step],
            proactive_suggestions=["Would you like a quiz on this topic?"],
            confidence=0.6,
            reasoning="Fallback plan - using best-guess tool"
        )
    
    def optimize_plan(self, plan: ExecutionPlan, execution_results: List[Dict]) -> ExecutionPlan:
        """
        Optimize plan based on execution results (adaptive planning).
        
        Args:
            plan: Original plan
            execution_results: Results from executed steps
            
        Returns:
            Optimized plan (may add/remove steps)
        """
        # Check if any steps failed
        failed_steps = [r for r in execution_results if not r.get("success", True)]
        
        if failed_steps:
            # Remove failed steps or replace with alternatives
            remaining_steps = [
                step for step in plan.steps 
                if step.step_number not in [f["step"] for f in failed_steps]
            ]
            plan.steps = remaining_steps
        
        return plan
    
    def generate_sub_plan(self, parent_step: PlanStep, context: Dict) -> List[PlanStep]:
        """
        Generate sub-steps for a complex step (hierarchical planning).
        
        Args:
            parent_step: The step to break down
            context: Context information
            
        Returns:
            List of sub-steps
        """
        # For future enhancement: break down complex steps into smaller ones
        return [parent_step]
    
    def get_planning_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about planning history.
        
        Returns:
            Dict with planning stats
        """
        if not self.planning_history:
            return {"total_plans": 0}
        
        return {
            "total_plans": len(self.planning_history),
            "avg_steps": sum(len(p.steps) for p in self.planning_history) / len(self.planning_history),
            "complexity_distribution": {
                "simple": sum(1 for p in self.planning_history if p.complexity == "simple"),
                "moderate": sum(1 for p in self.planning_history if p.complexity == "moderate"),
                "complex": sum(1 for p in self.planning_history if p.complexity == "complex")
            },
            "avg_confidence": sum(p.confidence for p in self.planning_history) / len(self.planning_history)
        }


class ProactiveSuggestionEngine:
    """
    Generates proactive suggestions based on context and user patterns.
    """
    
    def __init__(self):
        self.user_patterns = {}
    
    def generate_suggestions(
        self, 
        current_request: str,
        chat_history: List[Dict],
        plan: ExecutionPlan
    ) -> List[str]:
        """
        Generate smart proactive suggestions.
        
        Args:
            current_request: Current user request
            chat_history: Full conversation history
            plan: Current execution plan
            
        Returns:
            List of proactive suggestions
        """
        suggestions = []
        request_lower = current_request.lower()
        
        # Pattern 1: After explanation, suggest quiz
        if plan.complexity == "simple" and "explain" in request_lower:
            suggestions.append("Would you like a quiz to test your understanding?")
            suggestions.append("Should I provide some practice problems?")
        
        # Pattern 2: After quiz, suggest evaluation
        if "quiz" in request_lower or "test" in request_lower:
            suggestions.append("After attempting, I can evaluate your answers")
            suggestions.append("Want me to explain any concepts from the quiz?")
        
        # Pattern 3: After summarization, suggest deep dive
        if "summarize" in request_lower or "summary" in request_lower:
            suggestions.append("Need detailed explanation of any specific point?")
            suggestions.append("Should I create a quiz based on this summary?")
        
        # Pattern 4: Exam preparation
        if "exam" in request_lower or "test" in request_lower:
            suggestions.append("I can create a comprehensive study schedule")
            suggestions.append("Want me to identify the most important topics?")
        
        # Pattern 5: Learning trajectory
        if len(chat_history) > 5:
            suggestions.append("I can summarize what we've covered in this session")
            suggestions.append("Ready for a comprehensive assessment?")
        
        return suggestions[:3]  # Limit to top 3 suggestions
