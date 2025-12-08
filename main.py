import streamlit as st
from components.sidebar import sidebar_ui
from components.chat_ui import chat_ui
from components.pdf_handler import handle_pdf_upload
from core.rag_system import RAGSystem
from core.agent import StudyBuddyAgent
from core.tools import get_tool_registry, ToolExecutor
from core.planner import AgentPlanner
from core.memory import MemoryManager

st.set_page_config(page_title="StudyBuddy", page_icon="🧠", layout="wide")

# Initialize session state
if "pdf_content" not in st.session_state:
    st.session_state.pdf_content = None
if "user_focus" not in st.session_state:
    st.session_state.user_focus = ""
if "rag_system" not in st.session_state:
    st.session_state.rag_system = RAGSystem()
if "rag_enabled" not in st.session_state:
    st.session_state.rag_enabled = False

# Initialize Agentic AI components
if "agent" not in st.session_state:
    st.session_state.agent = StudyBuddyAgent(
        rag_system=st.session_state.rag_system,
        pdf_content=st.session_state.pdf_content or ""
    )
if "tool_registry" not in st.session_state:
    st.session_state.tool_registry = get_tool_registry()
if "tool_executor" not in st.session_state:
    st.session_state.tool_executor = ToolExecutor(st.session_state.tool_registry)
if "planner" not in st.session_state:
    st.session_state.planner = AgentPlanner(st.session_state.tool_registry)
if "memory" not in st.session_state:
    st.session_state.memory = MemoryManager()
if "agentic_mode" not in st.session_state:
    st.session_state.agentic_mode = True  # Enable by default
if "show_thinking" not in st.session_state:
    st.session_state.show_thinking = True  # Show agent's thinking process

# Unpack the tuple returned by sidebar_ui()
selected_mode, selected_sub_mode = sidebar_ui()

# Header
if st.session_state.get("agentic_mode", True):
    st.title("🧠 StudyBuddy - Your Agentic AI Study Assistant")
    st.caption("🤖 Powered by Autonomous AI Agent | Thinks, Plans & Executes Intelligently")
else:
    st.title("🧠 StudyBuddy - Your Smart Study Assistant")

# PDF Handler (optional upload)
st.markdown("### 📚 Upload a PDF (Optional)")
pdf_text, user_focus, summarize_clicked = handle_pdf_upload()

if summarize_clicked and pdf_text:
    from core.summarizer import summarize_text
    
    st.session_state.pdf_content = pdf_text
    st.session_state.user_focus = user_focus
    st.divider()
    
    # Auto-generate summary when button is clicked
    with st.spinner("💡 Generating summary..."):
        summary = summarize_text(
            text=pdf_text,
            previous_context="",
            user_focus=user_focus,
            extra_instruction=user_focus,
            rag_system=st.session_state.get("rag_system")
        )
    
    st.success("✅ Summary generated!")
    st.markdown("### 📝 Summary")
    st.markdown(summary)
    
    # Add to chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    st.session_state.messages.append({"role": "user", "content": f"Summarize with focus: {user_focus or 'general'}"})
    st.session_state.messages.append({"role": "assistant", "content": summary})

st.divider()

# Chat Interface
chat_ui(selected_mode, selected_sub_mode)