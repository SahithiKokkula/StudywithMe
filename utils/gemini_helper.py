from transformers import pipeline
import os
from dotenv import load_dotenv

# Load local .env for development
load_dotenv()

# Using a LOCAL model via transformers pipeline (100% FREE, runs on your computer!)
# Using TinyLlama - small, fast, runs locally without any API
MODEL = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

api_configured = False
_config_error = ""
generator = None

try:
    print(f"🔄 Loading local LLM: {MODEL} (first time may take 1-2 minutes to download)...")
    # Load model locally - completely free, no API needed
    generator = pipeline(
        "text-generation",
        model=MODEL,
        device_map="auto",  # Automatically use CPU
        max_new_tokens=1024,
        do_sample=True,
        temperature=0.7,
        top_p=0.95,
    )
    api_configured = True
    print(f"✅ Local LLM loaded successfully: {MODEL}")
except Exception as e:
    _config_error = str(e)
    api_configured = False
    print(f"⚠️ Error loading local model: {e}")

def generate_response(prompt: str) -> str:
    """Generate response using LOCAL LLM (TinyLlama - runs on your computer!)."""
    if not api_configured or generator is None:
        return f"""❌ Local LLM not loaded. 

{_config_error}

The app is trying to load TinyLlama-1.1B locally.
Please wait or restart the app."""
    
    try:
        print(f"🤖 Generating response with local LLM... (prompt length: {len(prompt)} chars)")
        
        # Format prompt for TinyLlama chat format
        formatted_prompt = f"<|system|>\nYou are Study Buddy, a helpful AI tutor.</s>\n<|user|>\n{prompt}</s>\n<|assistant|>\n"
        
        # Generate response locally (no API call!)
        result = generator(
            formatted_prompt,
            max_new_tokens=1024,
            do_sample=True,
            temperature=0.7,
            top_p=0.95,
            pad_token_id=generator.tokenizer.eos_token_id
        )
        
        # Extract generated text (remove the prompt part)
        full_text = result[0]['generated_text']
        # Get only the assistant's response
        response = full_text.split("<|assistant|>")[-1].strip()
        
        print(f"✅ Local LLM responded (length: {len(response)} chars)")
        return response if response else "⚠️ No response generated."
        
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Local LLM error: {error_msg}")
        return f"❌ Error generating response: {error_msg}"