import streamlit as st
from PyPDF2 import PdfReader

def handle_pdf_upload():
    """
    Handles PDF upload with editable extraction and RAG processing.
    Returns tuple: (pdf_text, user_extra_prompt, summarize_clicked)
    """
    uploaded_file = st.file_uploader("📚 Upload your study material (PDF)", type=["pdf"])
    pdf_text = ""
    user_extra = ""

    if uploaded_file:
        with st.spinner("Extracting text from PDF..."):
            try:
                reader = PdfReader(uploaded_file)
                for page in reader.pages:
                    pdf_text += page.extract_text() or ""
            except Exception as e:
                st.error(f"❌ Error reading PDF: {str(e)}")
                return None, None, False

        st.success("✅ PDF processed successfully!")

        # Preserve full extracted text across reruns and initialize editable preview
        preview = pdf_text[:3000] if pdf_text else ""
        last_name = uploaded_file.name if hasattr(uploaded_file, "name") else None
        if ("pdf_raw" not in st.session_state) or (st.session_state.get("last_upload_name") != last_name):
            st.session_state["pdf_raw"] = pdf_text
            st.session_state["pdf_edited"] = preview
            st.session_state["last_upload_name"] = last_name
            
            # Store PDF content for direct use (fallback when RAG not available)
            st.session_state.pdf_content = pdf_text
            
            # Try to process with RAG, but gracefully handle quota errors
            if st.session_state.get("rag_system") and len(pdf_text.strip()) >= 50:
                try:
                    with st.spinner("🧠 Trying to enable RAG (creating embeddings)..."):
                        success, message = st.session_state.rag_system.process_pdf(pdf_text)
                        if success:
                            st.session_state.rag_enabled = True
                            st.success(message + " - Smart retrieval active!")
                        else:
                            st.session_state.rag_enabled = False
                            if "quota" in message.lower() or "429" in message:
                                st.info("ℹ️ RAG embedding quota exceeded. App will use direct PDF content instead (still works great!)")
                            else:
                                st.warning(f"RAG not available: {message}. Using direct PDF content.")
                except Exception as e:
                    st.session_state.rag_enabled = False
                    st.info("ℹ️ RAG unavailable (quota limits). Using direct PDF content - your app still works perfectly!")

        # Let user edit the extracted text (show a preview to keep UI snappy)
        st.markdown("### 📝 Review & Edit Extracted Text")
        st.text_area(
            "Edit extracted text below (review, trim, or add notes):",
            value=st.session_state.get("pdf_edited", preview),
            height=300,
            help="You can modify the text before summarizing",
            key="pdf_edited"
        )

        # Show character counts and info
        raw_len = len(st.session_state.get("pdf_raw", "").strip())
        edited_len = len(st.session_state.get("pdf_edited", "").strip())
        st.caption(f"Full extracted text: {raw_len} chars — Current editable text: {edited_len} chars")
        if raw_len < 50:
            st.info("Text extraction is very short (<50 chars). Summarization will be blocked. Try another PDF or use OCR for scanned documents.")

        # Extra custom prompt for summarization with voice input
        st.markdown("### 🎯 Customization Options")
        
        col1, col2 = st.columns([10, 1])
        with col1:
            user_extra = st.text_input(
                "Any specific focus? (e.g., 'Focus on applications', 'Make exam-ready', 'Explain with examples')",
                placeholder="Leave empty for general summary or use",
                help="This will guide the AI on how to summarize",
                key="summary_focus_text"
            )
        
        

        # Summarize / Clear buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🚀 Summarize", use_container_width=True, key="summarize_btn"):
                # Decide which text to summarize:
                edited = st.session_state.get("pdf_edited", "").strip()
                raw = st.session_state.get("pdf_raw", "").strip()
                # If edited equals the preview of raw, prefer the full raw text
                preview_of_raw = raw[:3000]
                if not edited and raw:
                    text_to_summarize = raw
                elif edited == preview_of_raw:
                    text_to_summarize = raw
                else:
                    text_to_summarize = edited

                if text_to_summarize and len(text_to_summarize) >= 50:
                    return text_to_summarize, user_extra, True
                else:
                    st.warning("⚠️ No valid text to summarize. Please upload a valid PDF and ensure the extracted text is at least 50 characters.")
                    return None, None, False

        with col2:
            if st.button("🔄 Clear", use_container_width=True, key="clear_btn"):
                for k in ("pdf_raw", "pdf_edited", "last_upload_name"):
                    if k in st.session_state:
                        del st.session_state[k]
                st.rerun()

        return st.session_state.get("pdf_edited", preview), user_extra, False

    return None, None, False