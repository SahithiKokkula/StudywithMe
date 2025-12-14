from utils.groq_helper import generate_response

def summarize_text(text: str, previous_context: str = "", user_focus: str = "", 
                   extra_instruction: str = "", rag_system=None) -> str:
    """
    Summarize study materials using RAG retrieval if available and user specified a focus.

    Args:
        text: The content to summarize
        previous_context: Recent chat history
        user_focus: User's specified focus area
        extra_instruction: Additional instructions for customization
        rag_system: RAGSystem instance for intelligent retrieval
        
    Notes:
    - Keeps backwards compatibility with existing callers
    - Uses RAG to retrieve focused chunks when user_focus or extra_instruction is provided
    """
    print(f"📝 SUMMARIZER CALLED - text length: {len(text) if text else 0}, RAG ready: {rag_system.is_ready() if rag_system else False}")
    
    # Short-text guard
    if not text or len(text.strip()) < 50:
        return "⚠️ This text is too short to summarize. Please provide longer content."

    # Prefer extra_instruction, fall back to user_focus (keeps compatibility)
    instruction = extra_instruction.strip() if extra_instruction else user_focus.strip()
    
    # Use RAG to get focused chunks if available (ALWAYS use RAG for speed!)
    content_to_summarize = text
    rag_note = ""
    
    # If RAG available, use it to reduce content size (much faster!)
    if rag_system and rag_system.is_ready():
        if instruction:
            # User has specific focus - retrieve relevant sections
            retrieved = rag_system.retrieve_context(instruction, k=4)
            if retrieved:
                content_to_summarize = retrieved
                rag_note = " (Using RAG: Retrieved most relevant sections)"
        else:
            # No focus - sample first few chunks for speed (instead of entire PDF)
            retrieved = rag_system.retrieve_context(content_to_summarize[:1500], k=8)
            if retrieved:
                content_to_summarize = retrieved
                rag_note = " (Using RAG: Overview from key sections)"
    else:
        # Fallback: limit to first 8000 chars for speed
        if len(content_to_summarize) > 8000:
            content_to_summarize = content_to_summarize[:8000]
            rag_note = " (Using first 8000 chars)"

    prompt = f"""
You are Study Buddy, an academic summary AI.

- If text is VERY short (<50 words), say: "This text is too short to summarize. Please provide longer content."
- Otherwise, create a compact, exam-ready summary in clear, bullet-point sections:
  - Core definitions
  - Most important points (bullets)
  - Key formulas or diagrams (if present)
  - Application scenarios or examples
  - Add 2-3 practice/follow-up questions based on the content

If the user gives extra instructions (below), adapt output accordingly (e.g., "focus on applications"):
{instruction}{rag_note}

Reference prior chat context if relevant:
{previous_context}

Content:
{content_to_summarize}
"""
    print(f"📤 Sending prompt to Groq (length: {len(prompt)} chars)")
    result = generate_response(prompt.strip())
    print(f"📥 Got response from Groq (length: {len(result) if result else 0} chars)")
    return result
# ...existing code...