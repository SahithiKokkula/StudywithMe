from utils.groq_helper import generate_response

def explain_concept(concept: str, previous_context: str = "", rag_system=None, pdf_content: str = "") -> str:
    """
    Explain a concept in simple terms, using RAG retrieval if available, otherwise using full PDF.
    
    Args:
        concept: The topic or concept to explain
        previous_context: Recent chat history for context
        rag_system: RAGSystem instance for retrieving relevant PDF content
        pdf_content: Full PDF text as fallback when RAG is unavailable
    """
    
    # Try to get relevant context from RAG if available, otherwise use PDF content
    rag_context = ""
    if rag_system and rag_system.is_ready():
        rag_context = rag_system.retrieve_context(concept, k=3)
        if rag_context:
            rag_context = f"\n[Relevant material from your uploaded PDF (RAG retrieval):]:\n{rag_context}\n"
    elif pdf_content:
        # Fallback: Use a reasonable portion of the PDF (first 8000 chars to stay within limits)
        rag_context = f"\n[Content from your uploaded PDF:]:\n{pdf_content[:8000]}\n"
    
    prompt = f"""
You are Study Buddy, an AI-powered academic explainer.
[Recent chat for context:]
{previous_context}
{rag_context}
[Current topic/question:]
{concept}

Instructions:
- If relevant PDF content is provided above, prioritize using it as your primary source for the explanation
- If this is a topic (e.g., "Heap Sort", "Normalization in DBMS"):
    - Start with a simple definition or analogy/real-life example.
    - Follow with a step-by-step breakdown or main characteristics in bullet points.
    - Add common mistakes or misconceptions (if any).
    - End with 2-3 quick 'Key Takeaways' for revision.
- If the input sounds like an instruction ("make a quiz", "summarize this"):
    - Gently respond: "It looks like you might want to use the Quizzer or Summarizer mode instead."
- Use information from the previous chat for follow-up or clarifying answers.
- Keep language concise, avoid jargon unless needed, and always favor clarity.
- Use Markdown formatting for structure.
"""
    return generate_response(prompt.strip())
