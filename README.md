# 🧠 **Study Buddy — Agentic AI Study Assistant**

![Streamlit](https://img.shields.io/badge/Framework-Streamlit-red?logo=streamlit)
![Groq](https://img.shields.io/badge/AI-Groq%20API-blue?logo=ai)
![LLaMA](https://img.shields.io/badge/Model-LLaMA%203.3%2070B-orange?logo=meta)
![Python](https://img.shields.io/badge/Language-Python-yellow?logo=python)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)
![Version](https://img.shields.io/badge/version-2.1.0-purple)
![Agentic](https://img.shields.io/badge/AI-Agentic%20System-blueviolet)
![RAG](https://img.shields.io/badge/RAG-Enabled-success)

---

## 📖 **Table of Contents**
- [Overview](#-project-overview)
- [What's New - Agentic AI](#-now-powered-by-agentic-ai)
- [Features](#-core-features)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Usage](#-usage)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Future Scope](#-future-scope)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🧠 **Project Overview**

**Study Buddy** is an intelligent, autonomous AI-powered study assistant powered by **Groq API with LLaMA 3.3 70B** for lightning-fast responses. Get started in minutes with a free Groq API key!

Built for students who need help with:
- 📚 Understanding complex academic concepts
- 📝 Summarizing lengthy study materials and PDFs
- ❓ Generating practice quizzes and solving exam questions
- ✅ Getting detailed feedback on their answers
- 🎯 Creating personalized study plans
- ⚡ Ultra-fast AI responses (0.5-2 seconds)

---

## 🤖 **Now Powered by Agentic AI!**

### **Version 2.0 introduces autonomous intelligence:**

Unlike traditional chatbots that simply respond to commands, Study Buddy v2.0 features an **Agentic AI system** that:

✨ **Thinks Independently**
- Analyzes your request to understand your true intent
- No need to select modes — just ask naturally!

📋 **Plans Multi-Step Solutions**
- Breaks complex tasks into logical steps
- Orchestrates multiple tools automatically
- Example: "Help me prepare for my exam" → Agent creates comprehensive prep plan

💾 **Remembers & Learns**
- Short-term memory: Maintains conversation context
- Long-term memory: Learns your study patterns across sessions
- Personalizes suggestions based on your learning style

💡 **Acts Proactively**
- Suggests helpful next steps
- "Would you like a quiz on this topic?"
- "Should I explain any specific part in detail?"

🔄 **Self-Improves**
- Reflects on its own responses
- Ensures quality before delivering answers
- Adapts approach based on your feedback

🎯 **Natural Interaction**
- Chat like you would with a human tutor
- No special commands or formats needed
- Agent figures out what you need

---

## 🎁 **Core Features**

### **Autonomous Agent System**
- 🧠 **Agent Brain**: Central intelligence that thinks, plans, and executes
- 🛠️ **Tool Registry**: 6 specialized tools working together
- 📊 **Session Memory**: Tracks your progress and patterns
- 🔍 **Smart Planning**: Breaks down complex requests automatically

### **Learning Tools**

| Tool | What It Does | Example Use |
|------|-------------|-------------|
| 🧠 **Concept Explainer** | Simplifies complex topics | "Explain binary search trees" |
| 📄 **Content Summarizer** | Condenses long documents | "Summarize Chapter 5" |
| ❓ **Quiz Generator** | Creates practice tests | "Quiz me on algorithms" |
| 📖 **Question Solver** | Solves exam questions | "Solve: What is polymorphism?" |
| ✅ **Answer Evaluator** | Grades and provides feedback | "Check my answer on inheritance" |
| 🔍 **PDF Retriever** | Searches through documents | Automatic with PDF upload |

### **Smart Document Processing (RAG System)**

**RAG = Retrieval-Augmented Generation**

Instead of sending entire PDFs to the AI (which is slow and inefficient), Study Buddy uses RAG:

**How it works:**
1. 📄 **Upload PDF** → Text extracted
2. ✂️ **Chunking** → Splits into manageable pieces (1500 chars each)
3. 🧠 **Embedding** → Converts chunks to numerical vectors
4. 💾 **Storage** → Saves in ChromaDB vector database
5. 🔍 **Query** → Your question converted to vector
6. 🎯 **Search** → Finds most relevant chunks (semantic similarity)
7. 💬 **Generation** → AI uses only relevant chunks for answer

**Benefits:**
- ⚡ **Faster**: Only processes relevant content
- 🎯 **Accurate**: Focuses on specific information
- 📚 **Scalable**: Works with large documents (100+ pages)
- 💾 **Efficient**: No token limits or memory issues

**Features:**
- 📂 PDF upload and text extraction
- 🔍 Semantic search (understands meaning, not just keywords)
- 📚 Chapter-specific content retrieval
- 🧩 Context-aware responses from your documents

### **User Experience**
- 💬 Clean, intuitive chat interface
- 🎨 Dark theme for comfortable studying
- 📊 Real-time session statistics
- 🔄 Easy chat reset and session management
- 🧩 Optional thinking process visualization

---

## 🏗️ **Architecture**

### **Agentic AI Flow**
```
User Input
    ↓
🧠 Agent Brain (Analyzes Intent)
    ↓
📋 Planner (Creates Strategy)
    ↓
🛠️ Tool Selection (Picks Best Tools)
    ↓
⚡ Execution (Runs Tools)
    ↓
🎨 Synthesis (Combines Results)
    ↓
💬 Response + Suggestions
    ↓
💾 Memory (Learns from Interaction)
```

### **System Components**

**Frontend Layer:**
- Streamlit web interface
- Component-based UI (sidebar, chat, PDF handler)
- Real-time updates and spinners

**Agentic Layer:**
- `core/agent.py` - Main agent controller
- `core/planner.py` - Task planning and reasoning
- `core/tools.py` - Tool registry and executor
- `core/memory.py` - Session and learning memory
- `utils/agent_prompts.py` - Prompt templates

**AI Backend:**
- Groq API with LLaMA 3.3 70B (Lightning-fast inference)
- Sentence Transformers embeddings (for RAG)
- ChromaDB vector store (for document search)
- Fallback to local TinyLlama 1.1B (optional)

**Processing Layer:**
- PDF text extraction (PyPDF2)
- Text chunking and embedding
- Semantic search and retrieval

---

## 🔍 **RAG System Deep Dive**

### **What is RAG?**

**Retrieval-Augmented Generation** is a technique that combines:
- **Information Retrieval**: Finding relevant content from documents
- **Text Generation**: Using AI to create natural responses

### **Why RAG?**

**Without RAG (Traditional Approach):**
```
❌ Send entire 100-page PDF to AI
❌ Hits token limits
❌ Expensive API costs
❌ Slow processing
❌ AI gets confused with too much info
```

**With RAG (Smart Approach):**
```
✅ Send only 3-4 relevant chunks
✅ No token limit issues
✅ Fast and efficient
✅ AI focuses on what matters
✅ Works offline locally
```

### **RAG Pipeline in Study Buddy**

```
📄 PDF Document
    ↓
[Text Extraction] → PyPDF2 extracts all text
    ↓
[Chunking] → Split into 1500-char pieces with 150-char overlap
    ↓
[Embedding] → all-MiniLM-L6-v2 converts text to vectors
    ↓
[Vector Store] → ChromaDB stores embeddings
    ↓
[User Query] → "Explain recursion from Chapter 3"
    ↓
[Query Embedding] → Convert question to vector
    ↓
[Similarity Search] → Find top 3-5 most similar chunks
    ↓
[Context Retrieval] → Pull relevant text chunks
    ↓
[Prompt Engineering] → Combine query + retrieved context
    ↓
[AI Generation] → Groq LLaMA 3.3 70B generates answer using context
    ↓
[Response] → Accurate answer based on YOUR document
```

### **Technical Implementation**

**Embedding Model:**
- Model: `all-MiniLM-L6-v2` (Sentence Transformers)
- Dimensions: 384-dimensional vectors
- Size: ~80MB
- Speed: ~1000 sentences/second on CPU

**Vector Database:**
- Database: ChromaDB (open-source)
- Storage: Local disk (no cloud)
- Search: Cosine similarity
- Retrieval: Top-K nearest neighbors

**Chunking Strategy:**
- Chunk size: 1500 characters
- Overlap: 150 characters (10%)
- Splitter: RecursiveCharacterTextSplitter
- Preserves: Sentence boundaries

**Retrieval Parameters:**
- Default K: 3 chunks for normal queries
- Max K: 5 chunks for complex questions
- Similarity threshold: Automatic (top K)
- Context window: ~4500 characters total

### **RAG in Action**

**Example 1: Simple Query**
```
User: "What is binary search?"
→ RAG finds chunks mentioning "binary search"
→ Retrieves definition, example, complexity
→ AI explains using your PDF's specific content
```

**Example 2: Chapter-Specific**
```
User: "Quiz me on Chapter 5"
→ RAG identifies chunks from Chapter 5
→ Retrieves key concepts from that chapter
→ AI generates questions based on chapter content
```

**Example 3: Complex Topic**
```
User: "Compare merge sort and quick sort"
→ RAG finds chunks about both algorithms
→ Retrieves complexity, use cases, pseudocode
→ AI provides side-by-side comparison from PDF
```

### **Advantages of Local RAG**

✅ **Privacy**: Documents never leave your computer  
✅ **Cost**: Zero API costs  
✅ **Speed**: No network latency  
✅ **Offline**: Works without internet  
✅ **Control**: Full control over chunking and retrieval  
✅ **Scalability**: Handle large documents easily  

### **RAG System Files**

- `core/rag_system.py` - Main RAG implementation
- Uses HuggingFace embeddings (local)
- ChromaDB for vector storage
- LangChain for text splitting

---

## 📦 **Installation**

### **Prerequisites**
- Python 3.9 or higher
- Free Groq API key (get at: https://console.groq.com/keys)
- 2GB+ RAM recommended
- 500MB disk space (for embedding models)

### **Step 1: Clone Repository**
```bash
git clone https://github.com/YOUR_USERNAME/AI_StudyBuddy.git
cd AI_StudyBuddy
```

### **Step 2: Install Dependencies**
```bash
pip install -r requirements.txt
```

**Key packages installed:**
- `streamlit` - Web interface
- `groq` - Groq API client
- `sentence-transformers` - Text embeddings
- `langchain` - Document processing
- `chromadb` - Vector database
- `PyPDF2` - PDF processing
- `transformers` - (Optional) Local LLM fallback

### **Step 3: Get Groq API Key**
1. Go to: **https://console.groq.com/keys**
2. Sign up (free - use Google/GitHub)
3. Click **"Create API Key"**
4. Copy the key (starts with `gsk_`)

### **Step 4: Configure API Key**
1. Open the `.env` file in project root
2. Add your API key:
   ```
   GROQ_API_KEY=gsk_your_actual_key_here
   ```
3. Save the file

### **Step 5: Run the App**
```bash
streamlit run main.py
```

**Note:** First launch will download embedding model (~80MB) for RAG. This is one-time only!

### **Step 6: Access App**
Open browser to: `http://localhost:8501`

---

## 🚀 **Usage**

### **Quick Start**

1. **Launch the app**
   ```bash
   streamlit run main.py
   ```

2. **Enable Agentic Mode** (default ON)
   - Check sidebar: "Enable Autonomous Agent" toggle

3. **Start chatting naturally!**
   ```
   "Explain recursion"
   "Help me study for my OS exam tomorrow"
   "Quiz me on data structures"
   "Summarize this PDF and test me on it"
   ```

### **With PDF Documents**

1. **Upload your study material**
   - Click "Browse files" in PDF section
   - Select any PDF textbook or notes

2. **Ask questions about it**
   ```
   "Summarize Chapter 3"
   "Explain the diagram on page 15"
   "Create a quiz from Section 2.4"
   ```

3. **Agent automatically searches and uses relevant content!**

### **Example Interactions**

**Simple Question:**
```
You: "Explain binary search"

Agent: [Thinks] → Uses explainer tool → Provides clear explanation
       → Suggests: "Want a quiz?" or "Need code examples?"
```

**Complex Request:**
```
You: "I have an exam tomorrow on sorting algorithms"

Agent: [Thinks] → Creates 4-step plan:
       1. Retrieve sorting content from PDF
       2. Summarize key algorithms
       3. Generate comprehensive quiz
       4. Provide exam tips
       
       → Executes all steps automatically
       → Delivers complete study package
```

**Learning Flow:**
```
Session 1: "Explain linked lists"
Session 2: Agent remembers → "Ready to learn trees? They build on linked lists!"
Session 3: Agent suggests → "Want a comprehensive quiz on data structures?"
```

### **Viewing Agent's Thinking**

Enable "Show Thinking Process" in sidebar to see:
- Agent's intent analysis
- Step-by-step plan
- Tool selection reasoning
- Confidence levels

---

## 💻 **Tech Stack**

### **Core Technologies**

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Frontend** | Streamlit | Web UI framework |
| **AI Model** | Groq API (LLaMA 3.3 70B) | Lightning-fast inference |
| **ML Framework** | Sentence Transformers | Embedding generation |
| **Embeddings** | all-MiniLM-L6-v2 | Text similarity (384-dim) |
| **Vector DB** | ChromaDB | Document storage |
| **PDF Processing** | PyPDF2 | Text extraction |
| **Language** | Python 3.9+ | Main programming language |
| **Fallback** | TinyLlama 1.1B (Optional) | Local LLM fallback |

### **Agentic AI Stack**

| Module | File | Responsibility |
|--------|------|---------------|
| Agent Brain | `core/agent.py` | Main controller, reasoning |
| Planner | `core/planner.py` | Task decomposition |
| Tools | `core/tools.py` | Tool registry & execution |
| Memory | `core/memory.py` | Context & learning |
| Prompts | `utils/agent_prompts.py` | Agent instructions |

### **Why Groq API?**

✅ **Lightning Fast** - 0.5-2 second responses (vs 5-30s local)  
✅ **Free Tier** - 14,400 requests/day per model  
✅ **Powerful** - LLaMA 3.3 70B (vs 1.1B local)  
✅ **Quality** - Superior reasoning and accuracy  
✅ **Easy Setup** - Just add API key and go  
✅ **Fallback Available** - Optional local LLM support  

---

## 📁 **Project Structure**

```
AI_StudyBuddy/
├── main.py                      # Entry point
├── requirements.txt             # Dependencies
├── README.md                    # This file
├── CHANGELOG.md                 # Version history
├── LICENSE                      # MIT License
│
├── components/                  # UI Components
│   ├── sidebar.py              # Sidebar controls
│   ├── chat_ui.py              # Chat interface
│   └── pdf_handler.py          # PDF upload/processing
│
├── core/                        # Core Logic
│   ├── agent.py                # 🤖 Agentic AI brain
│   ├── planner.py              # 📋 Task planning
│   ├── tools.py                # 🛠️ Tool system
│   ├── memory.py               # 💾 Memory management
│   ├── explainer.py            # Concept explanations
│   ├── summarizer.py           # Content summarization
│   ├── quizzer.py              # Quiz generation
│   └── rag_system.py           # Document retrieval
│
└── utils/                       # Utilities
    ├── gemini_helper.py        # LLM interface (Groq API + fallback)
    └── agent_prompts.py        # Agent prompt templates
```

---

## 🎯 **Usage Modes**

### **Traditional Mode** (Optional)
If you prefer manual control, disable "Autonomous Agent" and select modes:

**💡 Explainer Mode**
- Explains concepts in simple language
- Provides analogies and examples
- Breaks down complex topics

**📰 Summarizer Mode**
- Condenses long texts
- Extracts key points
- Creates study notes

**🧩 Quizzer Mode**
- **Generate Questions**: Creates MCQs, T/F, short answers
- **Solve Questions**: Answers your exam questions
- **Evaluate Answers**: Grades and provides feedback

### **Agentic Mode** (Recommended)
Agent automatically chooses the right approach — just ask naturally!

---

## 📊 **Session Statistics**

Track your study progress:
- **Interactions**: Number of Q&A exchanges
- **Duration**: Study session length
- **Tools Used**: Which features you used most
- **Topics Covered**: What you've studied

Access via sidebar "📊 Session Stats" when agentic mode is enabled.

---

## 🎓 **Use Cases**

### **For Students**
- 📚 Quick concept clarification before exams
- 📝 Summarizing textbooks and lecture notes
- ❓ Practice questions with instant feedback
- 🧠 Understanding difficult topics step-by-step

### **For Self-Learners**
- 🎯 Structured learning paths
- 📖 Breaking down technical documentation
- ✅ Self-assessment and progress tracking
- 💡 Personalized study recommendations

### **For Exam Preparation**
- ⏰ Last-minute revision support
- 📋 Comprehensive study packages
- 🎯 Topic-specific quizzes
- ✍️ Answer evaluation and improvement tips

---

## 🔮 **Future Scope**

### **Planned Features**
- 🗣️ Voice interaction (speech-to-text/text-to-speech)
- 🌐 Multi-language support
- 📊 Advanced analytics and learning insights
- 🎴 Flashcard generation for spaced repetition
- 📱 Mobile-responsive design
- 🔗 Integration with note-taking apps

### **AI Enhancements**
- 🚀 Option to use larger models (Llama 2, Mistral)
- 🧠 Enhanced memory with persistent storage
- 🤝 Multi-agent collaboration
- 📈 Adaptive difficulty based on performance

---



### **Contribution Guidelines**
- Follow existing code style
- Add comments for complex logic
- Test thoroughly before submitting
- Update documentation if needed

---

## 📜 **License**

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---



## 🙏 **Acknowledgments**

- **Groq** for the lightning-fast API and free tier
- **Meta AI** for LLaMA 3.3 70B model
- **HuggingFace** for Sentence Transformers
- **Streamlit** for the amazing web framework
- **LangChain** for document processing tools
- **TinyLlama** team for the local fallback option
- All contributors and users!

---

## ⭐ **Show Your Support**

If you find Study Buddy helpful, please:
- ⭐ Star this repository
- 🐛 Report bugs and issues
- 💡 Suggest new features
- 🤝 Contribute improvements
- 📢 Share with fellow students!


---

<div align="center">

**Made with ❤️ for students everywhere**

*Empowering learning through autonomous AI*

</div>
