import streamlit as st
from core.explainer import explain_concept
from core.summarizer import summarize_text
from core.quizzer import (
    generate_questions,
    solve_questions,
    evaluate_answers
)
from utils.agent_prompts import ConversationTemplates

def get_previous_messages_summary(messages, limit=3):
    context_messages = messages[-2*limit:]
    return "\n".join(f"{m['role'].capitalize()}: {m['content']}" for m in context_messages)

def use_agentic_mode(prompt, previous_context):
    """Use the agentic AI system to handle the request."""
    agent = st.session_state.get("agent")
    memory = st.session_state.get("memory")
    show_thinking = st.session_state.get("show_thinking", True)
    
    if not agent:
        return "Agent not initialized. Please refresh the page."
    
    # Update agent with latest PDF content
    agent.pdf_content = st.session_state.get("pdf_content", "")
    agent.rag_system = st.session_state.get("rag_system")
    
    # Show thinking process if enabled
    if show_thinking:
        with st.expander("🧠 Agent's Thinking Process", expanded=False):
            thinking_msg = st.empty()
            thinking_msg.info(ConversationTemplates.get_thinking_message())
            
            # Execute agent with plan
            result = agent.execute(prompt, previous_context)
            
            # Show thinking trace
            trace = agent.get_thinking_trace()
            if trace:
                st.markdown("### Planning & Reasoning:")
                for step in trace:
                    st.markdown(f"- {step}")
            
            thinking_msg.success("✅ Plan complete! Executing...")
    else:
        # Execute without showing thinking
        result = agent.execute(prompt, previous_context)
    
    # Remember the interaction
    if memory:
        memory.remember_interaction(
            user_input=prompt,
            agent_response=result["response"],
            tools_used=result.get("tools_used", []),
            plan_complexity=result.get("plan", {}).get("complexity", "simple")
        )
    
    return result["response"]

def chat_ui(selected_mode, selected_sub_mode=None):
    """Main chat interface with mode and optional sub-mode for Quizzer."""
    
    # Build subheader dynamically
    if selected_sub_mode:
        st.subheader(f"💬 StudyBuddy Chat — {selected_mode} | {selected_sub_mode}")
    else:
        st.subheader(f"💬 StudyBuddy Chat — {selected_mode}")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input(f"Type your message…")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        previous_context = get_previous_messages_summary(st.session_state.messages[:-1], limit=3)
        assistant_response = ""
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            
            # Check if agentic mode is enabled
            agentic_mode = st.session_state.get("agentic_mode", True)
            
            try:
                with st.spinner("💡 Study Buddy is thinking…"):
                    # Use Agentic AI if enabled, otherwise use traditional mode selection
                    if agentic_mode:
                        assistant_response = use_agentic_mode(prompt, previous_context)
                    elif selected_mode == "💡 Explainer":
                        assistant_response = explain_concept(
                            prompt, 
                            previous_context,
                            rag_system=st.session_state.get("rag_system"),
                            pdf_content=st.session_state.get("pdf_content", "")
                        )

                    elif selected_mode == "📰 Summarizer":
                        # Use uploaded PDF if available; treat chat prompt as extra instruction or follow-up
                        pdf = st.session_state.get("pdf_content")
                        user_focus = st.session_state.get("user_focus", "")

                        # detect a likely follow-up question (short, starts with wh-word or ends with '?')
                        p = prompt.strip()
                        first_word = p.split()[0].lower() if p else ""
                        is_short = len(p.split()) <= 12
                        is_question = p.endswith("?") or first_word in ("what","why","how","when","which","who","where","explain","describe")
                        is_followup = bool(p) and (is_short or is_question)

                        if pdf:
                            # If follow-up and there is prior assistant content, prefer adapting the previous summary
                            if is_followup:
                                extra = f"Follow-up question: {p}. Use the previous assistant response and the PDF content to answer concisely."
                            else:
                                extra = p or user_focus

                            assistant_response = summarize_text(
                                text=pdf,
                                previous_context=previous_context,
                                user_focus=user_focus,
                                extra_instruction=extra,
                                rag_system=st.session_state.get("rag_system")
                            )
                        else:
                            # No PDF loaded — summarize the user's prompt directly (legacy behavior)
                            assistant_response = summarize_text(
                                p, 
                                previous_context,
                                rag_system=st.session_state.get("rag_system")
                            )

                    elif selected_mode == "🧩 Quizzer":
                        if selected_sub_mode == "📝 Generate Questions":
                            st.info(
                                "Paste a subject/topic or relevant passage. "
                                "Questions will be listed first, answers as a separate numbered key at the end."
                            )
                            assistant_response = generate_questions(
                                prompt, 
                                previous_context,
                                rag_system=st.session_state.get("rag_system")
                            )
                        elif selected_sub_mode == "📖 Solve Questions":
                            st.info(
                                "Paste your exam questions here. If specifying marks/word range, include this in each question."
                            )
                            # No word limit input needed; backend smartly adapts using prompt instructions
                            assistant_response = solve_questions(
                                prompt, 
                                previous_context,
                                rag_system=st.session_state.get("rag_system")
                            )
                        elif selected_sub_mode == "✅ Evaluate Answers":
                            qs_ans = prompt.split("---")
                            assistant_response = evaluate_answers(
                                qs_ans[0].strip(), 
                                qs_ans[1].strip(), 
                                previous_context,
                                rag_system=st.session_state.get("rag_system")
                            )
                        else:
                            assistant_response = "⚠️ Unknown Quizzer sub-mode."
                    else:
                        assistant_response = "⚠️ Unknown mode selected."
            except Exception as e:
                assistant_response = (
                    "❌ Sorry, there was an error processing your request. "
                    "Please try again in a few seconds.\n\n"
                    f"Error: {str(e)}"
                )
            response_placeholder.markdown(assistant_response)
            st.code(assistant_response, language="markdown")

            st.markdown("**Was this response helpful?**")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("👍 Helpful", key=f"fb_yes_{len(st.session_state.messages)}"):
                    st.success("Thank you for your feedback!")
            with col2:
                if st.button("👎 Not Helpful", key=f"fb_no_{len(st.session_state.messages)}"):
                    st.info(
                        "We appreciate your input! Please let us know how we can improve."
                    )

        st.session_state.messages.append({"role": "assistant", "content": assistant_response})
