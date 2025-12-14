import os
from dotenv import load_dotenv

# Load local .env for development
load_dotenv()

# Groq API Configuration (FAST & FREE!)
USE_GROQ = True  # Set to False to use local LLM instead
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = "llama-3.3-70b-versatile"  # Latest fast and powerful model

api_configured = False
_config_error = ""
groq_client = None
generator = None

# Try Groq API first
if USE_GROQ and GROQ_API_KEY:
    try:
        from groq import Groq
        groq_client = Groq(api_key=GROQ_API_KEY)
        api_configured = True
        print(f"✅ Groq API configured successfully with model: {GROQ_MODEL}")
        print("⚡ Lightning-fast responses enabled!")
    except ImportError:
        print("⚠️ Groq package not installed. Run: pip install groq")
        USE_GROQ = False
    except Exception as e:
        print(f"⚠️ Groq API error: {e}")
        USE_GROQ = False


def generate_response(prompt: str) -> str:
    """Generate response using Groq API (FAST!) or local LLM as fallback."""
    if not api_configured:
        return f"""❌ No LLM configured. 

{_config_error}

Please set up Groq API:
1. Get free API key from: https://console.groq.com
2. Add to .env file: GROQ_API_KEY=your_key_here
3. Restart the app

"""
    
    # Use Groq API (FAST!)
    if USE_GROQ and groq_client:
        try:
            print(f"⚡ Generating response with Groq API... (prompt length: {len(prompt)} chars)")
            
            chat_completion = groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are Study Buddy, a helpful AI tutor. Provide clear, educational responses."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=GROQ_MODEL,
                temperature=0.7,
                max_tokens=2048,
                top_p=0.9,
            )
            
            response = chat_completion.choices[0].message.content
            print(f"✅ Groq API responded (length: {len(response)} chars)")
            return response
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Groq API error: {error_msg}")
            return f"❌ Groq API error: {error_msg}\n\nPlease check your API key in .env file."
    
    # Fallback to local LLM
    elif generator is not None:
        try:
            print(f"🤖 Generating response with local LLM... (prompt length: {len(prompt)} chars)")
            
            formatted_prompt = f"<|system|>\nYou are Study Buddy, a helpful AI tutor.</s>\n<|user|>\n{prompt}</s>\n<|assistant|>\n"
            
            result = generator(
                formatted_prompt,
                max_new_tokens=1024,
                do_sample=True,
                temperature=0.7,
                top_p=0.95,
                pad_token_id=generator.tokenizer.eos_token_id
            )
            
            full_text = result[0]['generated_text']
            response = full_text.split("<|assistant|>")[-1].strip()
            
            print(f"✅ Local LLM responded (length: {len(response)} chars)")
            return response if response else "⚠️ No response generated."
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Local LLM error: {error_msg}")
            return f"❌ Error generating response: {error_msg}"
    
    return "❌ No LLM available. Please configure Groq API or install transformers for local LLM."