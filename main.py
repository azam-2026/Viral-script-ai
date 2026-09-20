import os
import gradio as gr
from groq import Groq

# Teri Groq API key pre-filled hai
GROQ_API_KEY = "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"

client = Groq(api_key=GROQ_API_KEY)

# Permanent Fallback Models List (Ek fail hoga toh doosra auto-try hoga)
MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "llama3-70b-8192",
    "gemma2-9b-it"
]

def generate_script(topic):
    if not topic or not topic.strip():
        return "Please enter a topic!"
    
    last_error = ""
    for model_name in MODELS:
        try:
            completion = client.chat.completions.create(
                model=model_name,
                messages=[{
                    "role": "user",
                    "content": f"Write a complete viral video script, retention hooks, and hashtags for: {topic}"
                }]
            )
            return completion.choices[0].message.content
        except Exception as e:
            last_error = str(e)
            continue
            
    return f"Error: {last_error}"

demo = gr.Interface(
    fn=generate_script,
    inputs=gr.Textbox(label="Video Topic", placeholder="Enter topic (e.g. Fitness tips)..."),
    outputs=gr.Textbox(label="Generated Script"),
    title="Viral AI Script Generator"
)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
