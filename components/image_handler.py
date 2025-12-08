import streamlit as st
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
import torch

# Global variables for model caching
_image_model = None
_image_processor = None

def load_image_model():
    """Load BLIP model for image analysis (one-time load)"""
    global _image_model, _image_processor
    
    if _image_model is None:
        try:
            print("🔄 Loading BLIP image model (first time: ~1-2 minutes)...")
            _image_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
            _image_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
            print("✅ Image model loaded successfully!")
        except Exception as e:
            print(f"❌ Error loading image model: {e}")
            return False
    return True

def analyze_image(image: Image.Image, question: str = None) -> str:
    """
    Analyze an image and optionally answer a question about it.
    
    Args:
        image: PIL Image object
        question: Optional question about the image
        
    Returns:
        str: Description or answer
    """
    try:
        if not load_image_model():
            return "❌ Image model not loaded. Please restart the app."
        
        # Resize image if too large (for faster processing)
        max_size = 512
        if max(image.size) > max_size:
            image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        if question:
            # Visual Question Answering mode
            inputs = _image_processor(image, question, return_tensors="pt")
        else:
            # Image captioning mode
            inputs = _image_processor(image, return_tensors="pt")
        
        # Generate description/answer
        with torch.no_grad():
            out = _image_model.generate(**inputs, max_new_tokens=100)
        
        result = _image_processor.decode(out[0], skip_special_tokens=True)
        return result
        
    except Exception as e:
        return f"❌ Error analyzing image: {str(e)}"

def handle_image_upload():
    """
    Handles image upload and analysis in the sidebar.
    Returns tuple: (image_description, analyze_clicked)
    """
    uploaded_image = st.file_uploader("🖼️ Upload an image (diagram, chart, screenshot)", type=["png", "jpg", "jpeg"])
    
    if uploaded_image:
        # Display the uploaded image
        image = Image.open(uploaded_image)
        st.image(image, caption="Uploaded Image", use_container_width=True)
        
        # Optional question about the image
        question = st.text_input(
            "Ask a question about the image (optional):",
            placeholder="E.g., 'What does this diagram show?', 'Explain this chart'",
            help="Leave empty for general description"
        )
        
        # Analyze button
        if st.button("🔍 Analyze Image", use_container_width=True, key="analyze_image_btn"):
            with st.spinner("🤖 Analyzing image..."):
                description = analyze_image(image, question if question.strip() else None)
                
                if description and not description.startswith("❌"):
                    st.success("✅ Analysis complete!")
                    return description, True
                else:
                    st.error(description)
                    return None, False
    
    return None, False
