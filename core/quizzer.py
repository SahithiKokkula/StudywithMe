from utils.gemini_helper import generate_response

def generate_questions(text: str, previous_context: str = "", rag_system=None) -> str:
    """
    Generate a quiz using RAG retrieval if available.
    
    Args:
        text: Topic or content for quiz generation
        previous_context: Recent chat history
        rag_system: RAGSystem instance for retrieving relevant content
    """
    
    # If user asks for questions on a topic and RAG is available, retrieve context
    content = text
    if rag_system and rag_system.is_ready() and len(text.split()) < 20:
        # User probably entered a topic name, retrieve relevant chunks
        retrieved = rag_system.retrieve_context(text, k=4)
        if retrieved:
            content = retrieved
    
    prompt = f"""
You are Study Buddy, an academic quiz generator.

Context:
{previous_context}

Content/topic:
{content}

Instructions:
- Create a mix of questions: Multiple Choice (with options A-D, each on a separate line), True/False, Fill in the Blanks, Short Descriptive.
- List all questions in order. If useful, include a short hint with a question.
- Do NOT show the correct answer right after each question.
- Instead, after ALL questions, provide a numbered "Answer Key" listing each answer (e.g., "1. B", "2. True", "3. Photosynthesis", ...).
- Number every question and answer for clarity.
- Format so the student can attempt first, then check answers.
"""
    return generate_response(prompt.strip())

def solve_questions(user_questions: str, previous_context: str = "", word_limit: int = 100, rag_system=None) -> str:
    """
    Solve exam-style questions, retrieving context from PDF if available.
    
    Args:
        user_questions: Questions to solve
        previous_context: Recent chat history
        word_limit: Default word limit (deprecated, kept for compatibility)
        rag_system: RAGSystem instance for retrieving relevant content
    """
    
    # Retrieve relevant context for the questions
    rag_context = ""
    if rag_system and rag_system.is_ready():
        rag_context = rag_system.retrieve_context(user_questions, k=3)
        if rag_context:
            rag_context = f"\n[Relevant material from uploaded PDF:]\n{rag_context}\n"
    
    prompt = f"""
You are Study Buddy, a question-solving AI.

Questions:
{user_questions}
{rag_context}
Recent context:
{previous_context}

Instructions:
- Use the PDF material above if relevant to answer the questions
- For each question, decide what type it is (very short, short, long) and adapt your answer length:
  • Very short answer (objective, 0.5–1 mark): 25–40 words or 1–2 sentences.
  • Short answer (2–3 marks): 90–130 words, mention any diagrams/visuals if relevant.
  • Long answer (4–5 marks): 160–220 words, stepwise breakdowns/mention any diagrams if relevant.
- If user gives a word limit or mark value, follow it.
- Number all answers; use Markdown formatting (bold for questions/answers, bullet points, headings for diagrams).
"""
    return generate_response(prompt.strip())

def evaluate_answers(questions: str, user_answers: str, previous_context: str = "", rag_system=None) -> str:
    """
    Evaluate user's answers with reference material from RAG.
    
    Args:
        questions: The questions being answered
        user_answers: User's provided answers
        previous_context: Recent chat history
        rag_system: RAGSystem instance for retrieving reference material
    """
    
    # Get reference material for evaluation
    rag_context = ""
    if rag_system and rag_system.is_ready():
        rag_context = rag_system.retrieve_context(questions, k=2)
        if rag_context:
            rag_context = f"\n[Reference material from PDF:]\n{rag_context}\n"
    
    prompt = f"""
You are Study Buddy, an answer evaluator.

Questions:
{questions}

User's Answers:
{user_answers}
{rag_context}
Recent chat:
{previous_context}

Instructions:
- Compare user answers against the reference material if available
- For each answer, indicate if it's correct/incorrect.
- Give specific suggestions for improvement, point out missing facts/examples if relevant.
- Assign a score out of the maximum possible (e.g., 1 mark, 3 marks, etc.)—be detailed.
- Summarize overall strengths and improvement areas.
- Use numbered feedback, concise language.
"""
    return generate_response(prompt.strip())
