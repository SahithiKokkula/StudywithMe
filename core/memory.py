"""
Memory System for Agentic AI
Implements short-term and long-term memory for context awareness and learning.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
import json


@dataclass
class ConversationTurn:
    """Represents a single turn in the conversation."""
    timestamp: str
    user_input: str
    agent_response: str
    tools_used: List[str]
    plan_complexity: str
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class StudySession:
    """Represents a complete study session."""
    session_id: str
    start_time: str
    end_time: Optional[str]
    topics_covered: List[str]
    tools_used_count: Dict[str, int]
    total_turns: int
    pdf_used: bool
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ShortTermMemory:
    """
    Manages recent conversation context (current session).
    """
    
    def __init__(self, max_turns: int = 10):
        """
        Initialize short-term memory.
        
        Args:
            max_turns: Maximum conversation turns to remember
        """
        self.max_turns = max_turns
        self.conversation: List[ConversationTurn] = []
        self.current_context = ""
        
    def add_turn(
        self, 
        user_input: str, 
        agent_response: str,
        tools_used: List[str],
        plan_complexity: str = "simple",
        metadata: Dict[str, Any] = None
    ):
        """
        Add a conversation turn to memory.
        
        Args:
            user_input: User's message
            agent_response: Agent's response
            tools_used: List of tools used
            plan_complexity: Complexity of the plan
            metadata: Additional information
        """
        turn = ConversationTurn(
            timestamp=datetime.now().isoformat(),
            user_input=user_input,
            agent_response=agent_response[:500],  # Store truncated response
            tools_used=tools_used,
            plan_complexity=plan_complexity,
            metadata=metadata or {}
        )
        
        self.conversation.append(turn)
        
        # Keep only last N turns
        if len(self.conversation) > self.max_turns:
            self.conversation.pop(0)
        
        # Update current context
        self._update_context()
    
    def _update_context(self):
        """Update the current context string from recent turns."""
        recent_turns = self.conversation[-5:]  # Last 5 turns
        context_parts = []
        
        for turn in recent_turns:
            context_parts.append(f"User: {turn.user_input}")
            context_parts.append(f"Assistant: {turn.agent_response[:200]}...")
        
        self.current_context = "\n".join(context_parts)
    
    def get_context(self, max_length: int = 2000) -> str:
        """
        Get recent conversation context.
        
        Args:
            max_length: Maximum context length
            
        Returns:
            Formatted context string
        """
        context = self.current_context
        if len(context) > max_length:
            context = context[-max_length:]
        return context
    
    def get_recent_topics(self, n: int = 3) -> List[str]:
        """
        Extract topics from recent conversation.
        
        Args:
            n: Number of recent turns to analyze
            
        Returns:
            List of identified topics
        """
        topics = []
        recent = self.conversation[-n:]
        
        for turn in recent:
            # Simple topic extraction (can be enhanced)
            words = turn.user_input.lower().split()
            if len(words) > 2:
                # Take key phrases
                topics.append(turn.user_input[:50])
        
        return topics
    
    def get_tool_usage(self) -> Dict[str, int]:
        """
        Get statistics on tool usage in current session.
        
        Returns:
            Dict mapping tool names to usage counts
        """
        usage = {}
        for turn in self.conversation:
            for tool in turn.tools_used:
                usage[tool] = usage.get(tool, 0) + 1
        return usage
    
    def clear(self):
        """Clear short-term memory (start new session)."""
        self.conversation = []
        self.current_context = ""


class LongTermMemory:
    """
    Manages persistent memory across sessions (simulated - would use DB in production).
    """
    
    def __init__(self):
        """Initialize long-term memory."""
        self.study_sessions: List[StudySession] = []
        self.user_preferences = {
            "preferred_explanation_style": "simple",
            "quiz_difficulty": "medium",
            "topics_of_interest": []
        }
        self.learning_patterns = {
            "most_used_tools": {},
            "common_topics": [],
            "study_times": [],
            "weak_areas": []
        }
    
    def save_session(self, session: StudySession):
        """
        Save a completed study session.
        
        Args:
            session: StudySession to save
        """
        self.study_sessions.append(session)
        self._update_patterns(session)
    
    def _update_patterns(self, session: StudySession):
        """Update learning patterns based on new session."""
        # Update tool usage
        for tool, count in session.tools_used_count.items():
            current = self.learning_patterns["most_used_tools"].get(tool, 0)
            self.learning_patterns["most_used_tools"][tool] = current + count
        
        # Update common topics
        self.learning_patterns["common_topics"].extend(session.topics_covered)
        
        # Keep only unique recent topics (last 20)
        self.learning_patterns["common_topics"] = list(set(
            self.learning_patterns["common_topics"][-20:]
        ))
    
    def get_user_history_summary(self) -> str:
        """
        Get a summary of user's learning history.
        
        Returns:
            Formatted summary string
        """
        if not self.study_sessions:
            return "This is your first session!"
        
        total_sessions = len(self.study_sessions)
        most_used_tool = max(
            self.learning_patterns["most_used_tools"].items(),
            key=lambda x: x[1],
            default=("None", 0)
        )[0]
        
        recent_topics = self.learning_patterns["common_topics"][-5:]
        
        summary = f"""
**Your Learning History:**
- Total study sessions: {total_sessions}
- Most used feature: {most_used_tool}
- Recent topics: {', '.join(recent_topics) if recent_topics else 'None'}
"""
        return summary.strip()
    
    def get_personalized_suggestions(self) -> List[str]:
        """
        Generate personalized suggestions based on history.
        
        Returns:
            List of suggestions
        """
        suggestions = []
        
        # Based on tool usage
        if self.learning_patterns["most_used_tools"].get("concept_explainer", 0) > 5:
            suggestions.append("You learn well through explanations - keep that up!")
        
        # Based on topics
        if len(self.learning_patterns["common_topics"]) > 3:
            suggestions.append("Ready for a comprehensive quiz on all your recent topics?")
        
        return suggestions


class MemoryManager:
    """
    Unified memory management system combining short-term and long-term memory.
    """
    
    def __init__(self):
        """Initialize memory manager."""
        self.short_term = ShortTermMemory(max_turns=10)
        self.long_term = LongTermMemory()
        self.current_session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_start_time = datetime.now().isoformat()
    
    def remember_interaction(
        self,
        user_input: str,
        agent_response: str,
        tools_used: List[str],
        plan_complexity: str = "simple",
        metadata: Dict[str, Any] = None
    ):
        """
        Remember a user-agent interaction.
        
        Args:
            user_input: User's message
            agent_response: Agent's response
            tools_used: Tools used in this interaction
            plan_complexity: Complexity level
            metadata: Additional data
        """
        self.short_term.add_turn(
            user_input=user_input,
            agent_response=agent_response,
            tools_used=tools_used,
            plan_complexity=plan_complexity,
            metadata=metadata
        )
    
    def get_relevant_context(self, current_query: str = "") -> str:
        """
        Get relevant context for current query.
        
        Args:
            current_query: Current user query
            
        Returns:
            Relevant context string
        """
        # Get short-term context
        short_context = self.short_term.get_context()
        
        # Get long-term insights
        long_context = self.long_term.get_user_history_summary()
        
        return f"{short_context}\n\n{long_context}"
    
    def get_session_summary(self) -> Dict[str, Any]:
        """
        Get summary of current session.
        
        Returns:
            Session summary dict
        """
        topics = self.short_term.get_recent_topics()
        tools = self.short_term.get_tool_usage()
        
        return {
            "session_id": self.current_session_id,
            "duration_minutes": (datetime.now() - datetime.fromisoformat(self.session_start_time)).seconds // 60,
            "topics_covered": topics,
            "tools_used": tools,
            "total_interactions": len(self.short_term.conversation)
        }
    
    def end_session(self, pdf_used: bool = False):
        """
        End current session and save to long-term memory.
        
        Args:
            pdf_used: Whether PDF was used in this session
        """
        summary = self.get_session_summary()
        
        session = StudySession(
            session_id=self.current_session_id,
            start_time=self.session_start_time,
            end_time=datetime.now().isoformat(),
            topics_covered=summary["topics_covered"],
            tools_used_count=summary["tools_used"],
            total_turns=summary["total_interactions"],
            pdf_used=pdf_used
        )
        
        self.long_term.save_session(session)
        self.short_term.clear()
    
    def start_new_session(self):
        """Start a new study session."""
        self.end_session()
        self.current_session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_start_time = datetime.now().isoformat()
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """
        Get insights about user's learning patterns.
        
        Returns:
            Dict with insights
        """
        return {
            "current_session": self.get_session_summary(),
            "patterns": self.long_term.learning_patterns,
            "suggestions": self.long_term.get_personalized_suggestions()
        }
    
    def recall_similar_interaction(self, query: str) -> Optional[str]:
        """
        Recall if user asked something similar before.
        
        Args:
            query: Current query
            
        Returns:
            Previous similar interaction if found
        """
        query_lower = query.lower()
        
        # Check recent conversations
        for turn in reversed(self.short_term.conversation):
            if any(word in turn.user_input.lower() for word in query_lower.split()[:3]):
                return f"Previously, you asked about: {turn.user_input}"
        
        return None
