"""
Tool Registry and Definitions for Agentic AI
This module defines all available tools that the agent can use.
"""

from typing import Dict, List, Callable, Any
from dataclasses import dataclass


@dataclass
class Tool:
    """Definition of a tool that the agent can use."""
    name: str
    description: str
    parameters: List[str]
    function: Callable
    category: str
    requires_pdf: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert tool to dictionary format for agent reasoning."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "category": self.category,
            "requires_pdf": self.requires_pdf
        }


class ToolRegistry:
    """
    Central registry of all available tools for the agent.
    """
    
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register all default Study Buddy tools."""
        
        # Import tool functions
        from core.explainer import explain_concept
        from core.summarizer import summarize_text
        from core.quizzer import generate_questions, solve_questions, evaluate_answers
        
        # Explainer Tool
        self.register_tool(Tool(
            name="concept_explainer",
            description="Explains academic concepts, topics, or questions in simple, easy-to-understand terms. Best for: 'Explain X', 'What is Y', 'Help me understand Z'. Uses PDF content if available.",
            parameters=["concept", "previous_context", "rag_system", "pdf_content"],
            function=explain_concept,
            category="learning",
            requires_pdf=False
        ))
        
        # Summarizer Tool
        self.register_tool(Tool(
            name="content_summarizer",
            description="Summarizes long text, notes, or PDF documents into concise key points. Best for: 'Summarize this', 'Give me the main points', 'TL;DR of chapter X'. Requires content to summarize.",
            parameters=["text", "previous_context", "user_focus", "extra_instruction", "rag_system"],
            function=summarize_text,
            category="comprehension",
            requires_pdf=True
        ))
        
        # Quiz Generator Tool
        self.register_tool(Tool(
            name="quiz_generator",
            description="Creates practice quizzes with multiple choice, true/false, fill-in-the-blank, and short answer questions. Best for: 'Make a quiz on X', 'Test me on Y', 'Practice questions for Z'. Includes answer key.",
            parameters=["text", "previous_context", "rag_system"],
            function=generate_questions,
            category="assessment",
            requires_pdf=False
        ))
        
        # Question Solver Tool
        self.register_tool(Tool(
            name="question_solver",
            description="Solves exam-style questions with detailed answers. Adapts answer length based on marks/word limits. Best for: 'Solve this question', 'Answer: Q1. ...', 'Help with this problem'. Uses PDF as reference if available.",
            parameters=["user_questions", "previous_context", "word_limit", "rag_system"],
            function=solve_questions,
            category="problem_solving",
            requires_pdf=False
        ))
        
        # Answer Evaluator Tool
        self.register_tool(Tool(
            name="answer_evaluator",
            description="Evaluates and grades user's answers to questions. Provides detailed feedback, marks allocation, and improvement suggestions. Best for: 'Check my answer', 'Evaluate this', 'How did I do?'",
            parameters=["questions", "user_answers", "previous_context", "rag_system"],
            function=evaluate_answers,
            category="assessment",
            requires_pdf=False
        ))
    
    def register_tool(self, tool: Tool):
        """Register a new tool in the registry."""
        self.tools[tool.name] = tool
    
    def get_tool(self, name: str) -> Tool:
        """Get a tool by name."""
        return self.tools.get(name)
    
    def get_all_tools(self) -> List[Tool]:
        """Get all registered tools."""
        return list(self.tools.values())
    
    def get_tools_by_category(self, category: str) -> List[Tool]:
        """Get all tools in a specific category."""
        return [tool for tool in self.tools.values() if tool.category == category]
    
    def get_tool_descriptions(self) -> str:
        """Get formatted descriptions of all tools for agent reasoning."""
        descriptions = []
        for i, tool in enumerate(self.tools.values(), 1):
            descriptions.append(
                f"{i}. **{tool.name}** ({tool.category})\n"
                f"   - {tool.description}\n"
                f"   - Requires PDF: {'Yes' if tool.requires_pdf else 'No'}"
            )
        return "\n\n".join(descriptions)
    
    def suggest_tools(self, user_request: str, has_pdf: bool = False) -> List[str]:
        """
        Suggest appropriate tools based on user request.
        
        Args:
            user_request: User's input
            has_pdf: Whether PDF content is available
            
        Returns:
            List of suggested tool names
        """
        request_lower = user_request.lower()
        suggestions = []
        
        # Keyword-based suggestions
        explain_keywords = ["explain", "what is", "how does", "help me understand", "clarify"]
        summarize_keywords = ["summarize", "summary", "tldr", "main points", "key points", "condense"]
        quiz_keywords = ["quiz", "test", "practice", "questions", "mcq", "exam prep"]
        solve_keywords = ["solve", "answer", "solution", "work out", "calculate"]
        evaluate_keywords = ["check", "evaluate", "grade", "feedback", "review my answer"]
        
        if any(keyword in request_lower for keyword in explain_keywords):
            suggestions.append("concept_explainer")
        
        if any(keyword in request_lower for keyword in summarize_keywords):
            suggestions.append("content_summarizer")
        
        if any(keyword in request_lower for keyword in quiz_keywords):
            suggestions.append("quiz_generator")
        
        if any(keyword in request_lower for keyword in solve_keywords):
            suggestions.append("question_solver")
        
        if any(keyword in request_lower for keyword in evaluate_keywords):
            suggestions.append("answer_evaluator")
        
        # If no specific keywords found, default to explainer
        if not suggestions:
            suggestions.append("concept_explainer")
        
        # Filter out PDF-requiring tools if no PDF available
        if not has_pdf:
            suggestions = [s for s in suggestions if not self.tools[s].requires_pdf or s == "concept_explainer"]
        
        return suggestions


class ToolExecutor:
    """
    Executes tools with proper parameter handling and error recovery.
    """
    
    def __init__(self, tool_registry: ToolRegistry):
        self.registry = tool_registry
        self.execution_history = []
    
    def execute(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a tool with given parameters.
        
        Args:
            tool_name: Name of the tool to execute
            **kwargs: Parameters for the tool
            
        Returns:
            Dict with result and metadata
        """
        tool = self.registry.get_tool(tool_name)
        
        if not tool:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found",
                "result": None
            }
        
        try:
            # Execute the tool
            result = tool.function(**kwargs)
            
            # Record execution
            self.execution_history.append({
                "tool": tool_name,
                "success": True,
                "result_length": len(str(result))
            })
            
            return {
                "success": True,
                "error": None,
                "result": result,
                "tool": tool_name
            }
            
        except Exception as e:
            # Record failure
            self.execution_history.append({
                "tool": tool_name,
                "success": False,
                "error": str(e)
            })
            
            return {
                "success": False,
                "error": str(e),
                "result": None,
                "tool": tool_name
            }
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get summary of tool executions."""
        total = len(self.execution_history)
        successful = sum(1 for exec in self.execution_history if exec["success"])
        
        return {
            "total_executions": total,
            "successful": successful,
            "failed": total - successful,
            "success_rate": successful / total if total > 0 else 0,
            "history": self.execution_history
        }


# Global registry instance
_global_registry = ToolRegistry()


def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry instance."""
    return _global_registry


def get_available_tools_info() -> str:
    """Get formatted information about all available tools."""
    return _global_registry.get_tool_descriptions()
