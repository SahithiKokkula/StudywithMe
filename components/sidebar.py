import streamlit as st
import time
def sidebar_ui():
    """Sidebar with mode and Quizzer sub-mode selectors, and core controls."""

    st.sidebar.title("⚙️ Settings")

    # API/info
    st.sidebar.markdown("### AI Model")
    st.sidebar.info("**groq**")
    st.sidebar.caption("Running on your computer - 100% free!")

    # Mode selection
    st.sidebar.markdown("### 🧩 Choose Mode")
    mode = st.sidebar.radio(
        "Select a core function:",
        ["💡 Explainer", "📰 Summarizer", "🧩 Quizzer"],
        index=0
    )

    # Nested radio for Quizzer
    sub_mode = None
    if mode == "🧩 Quizzer":
        st.sidebar.markdown("### ✨ Quizzer Action")
        sub_mode = st.sidebar.radio(
            "Choose Quizzer action:",
            [
                "📝 Generate Questions",
                "📖 Solve Questions",
                "✅ Evaluate Answers"
            ],
            index=0
        )

    st.sidebar.markdown("---")
    
    # Agentic AI Controls
    st.sidebar.markdown("### 🤖 Agentic AI")
    agentic_mode = st.sidebar.toggle(
        "Enable Autonomous Agent",
        value=st.session_state.get("agentic_mode", True),
        help="Agent thinks independently and uses multiple tools automatically"
    )
    st.session_state.agentic_mode = agentic_mode
    
    if agentic_mode:
        show_thinking = st.sidebar.toggle(
            "Show Thinking Process",
            value=st.session_state.get("show_thinking", True),
            help="Display agent's planning and reasoning"
        )
        st.session_state.show_thinking = show_thinking
        
        # Show session statistics if memory exists
        if "memory" in st.session_state:
            memory = st.session_state.memory
            session_stats = memory.get_session_summary()
            with st.sidebar.expander("📊 Session Stats"):
                st.write(f"**Interactions:** {session_stats['total_interactions']}")
                st.write(f"**Duration:** {session_stats['duration_minutes']} min")
                if session_stats['tools_used']:
                    st.write("**Tools Used:**")
                    for tool, count in session_stats['tools_used'].items():
                        st.write(f"- {tool}: {count}x")
    
    st.sidebar.markdown("---")
    
    # RAG System Status
    if "rag_system" in st.session_state and st.session_state.get("rag_enabled"):
        rag_chunks = st.session_state.rag_system.get_chunk_count()
        st.sidebar.success(f"🧠 RAG Active: {rag_chunks} chunks indexed")
        if st.sidebar.button("🔄 Reset RAG System"):
            st.session_state.rag_system.reset()
            st.session_state.rag_enabled = False
            st.session_state.pdf_content = None
            st.rerun()
    elif st.session_state.get("pdf_content"):
        st.sidebar.info("📄 PDF loaded (using direct content)")
        st.sidebar.caption("RAG unavailable due to API quota limits")
    else:
        st.sidebar.info("📄 Upload a PDF to get started")
    
    st.sidebar.markdown("---")
    if st.sidebar.button("🆕 New Chat"):
        st.session_state.messages = []
        # Start new session in memory if available
        if "memory" in st.session_state:
            st.session_state.memory.start_new_session()
        # Success message that auto-disappears after 2 seconds
        success_placeholder = st.sidebar.empty()
        with success_placeholder.container():
            st.success("Started a new chat!")
        time.sleep(2)
        success_placeholder.empty()

    st.sidebar.markdown("---")
    st.sidebar.caption("✨ StudyBuddy - AI Powered Study Assistant")

    return mode, sub_mode
