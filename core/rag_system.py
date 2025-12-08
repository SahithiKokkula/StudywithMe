# core/rag_system.py
# RAG (Retrieval-Augmented Generation) system for intelligent document retrieval

import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
import os
from dotenv import load_dotenv

load_dotenv()

class RAGSystem:
    """Handles document chunking, embedding, storage, and retrieval"""
    
    def __init__(self):
        self.vectorstore = None
        self.embeddings = None
        self.chunk_count = 0
        self._initialize_embeddings()
        
    def _initialize_embeddings(self):
        """Initialize embedding model - using HuggingFace (free, no quota limits)"""
        try:
            from sentence_transformers import SentenceTransformer
            # Using sentence-transformers directly for embeddings (runs locally, no API needed)
            class SimpleSentenceTransformerEmbeddings:
                def __init__(self, model_name):
                    self.model = SentenceTransformer(model_name)
                
                def embed_documents(self, texts):
                    return self.model.encode(texts, normalize_embeddings=True).tolist()
                
                def embed_query(self, text):
                    return self.model.encode(text, normalize_embeddings=True).tolist()
            
            self.embeddings = SimpleSentenceTransformerEmbeddings("all-MiniLM-L6-v2")
            print("✅ HuggingFace embeddings initialized successfully")
        except Exception as e:
            print(f"Warning: Could not initialize embeddings: {e}")
            self.embeddings = None
        
    def process_pdf(self, pdf_text: str, chunk_size: int = 1500, chunk_overlap: int = 150):
        """
        Split PDF text into chunks and store in vector database
        
        Args:
            pdf_text: Extracted text from PDF
            chunk_size: Size of each text chunk (default 1500 chars - larger for speed)
            chunk_overlap: Overlap between chunks (default 150 chars - less overlap for speed)
            
        Returns:
            tuple: (success: bool, message: str)
        """
        if not pdf_text or len(pdf_text.strip()) < 50:
            return False, "❌ PDF text too short to process (minimum 50 characters required)"
        
        if not self.embeddings:
            return False, "❌ Embedding model not initialized. Check GEMINI_API_KEY."
        
        try:
            print(f"📊 Processing PDF text ({len(pdf_text)} chars)...")
            # Step 1: Split text into manageable chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                length_function=len,
                separators=["\n\n", "\n", ". ", " ", ""]
            )
            chunks = text_splitter.split_text(pdf_text)
            self.chunk_count = len(chunks)
            print(f"✂️ Split into {self.chunk_count} chunks")
            
            if self.chunk_count == 0:
                return False, "❌ No chunks created from PDF text"
            
            # Step 2: Create embeddings and store in ChromaDB (in-memory)
            print(f"🧠 Creating embeddings (this may take 10-30 seconds)...")
            self.vectorstore = Chroma.from_texts(
                texts=chunks,
                embedding=self.embeddings,
                persist_directory=None  # In-memory for simplicity
            )
            print(f"✅ RAG system ready with {self.chunk_count} chunks!")
            
            return True, f"✅ RAG enabled: {self.chunk_count} chunks created & indexed"
            
        except Exception as e:
            return False, f"❌ Error processing PDF for RAG: {str(e)}"
    
    def retrieve_context(self, query: str, k: int = 3) -> str:
        """
        Retrieve most relevant chunks for a query using semantic search
        
        Args:
            query: User's question or topic
            k: Number of chunks to retrieve (default 3)
            
        Returns:
            Combined text from relevant chunks
        """
        if not self.vectorstore:
            return ""
        
        try:
            # Semantic search for relevant chunks
            docs = self.vectorstore.similarity_search(query, k=k)
            
            if not docs:
                return ""
            
            # Combine retrieved chunks with clear separators
            context = "\n\n--- Retrieved Section ---\n\n".join([doc.page_content for doc in docs])
            return context
            
        except Exception as e:
            print(f"⚠️ Retrieval error: {e}")
            return ""
    
    def is_ready(self) -> bool:
        """Check if vector store has been initialized and is ready for queries"""
        return self.vectorstore is not None
    
    def get_chunk_count(self) -> int:
        """Get the number of chunks in the vector store"""
        return self.chunk_count
    
    def reset(self):
        """Clear the vector store and reset state"""
        self.vectorstore = None
        self.chunk_count = 0
