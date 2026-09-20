import os
import urllib.parse
import urllib.request
import gradio as gr
from groq import Groq

GROQ_API_KEY = "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"

client = Groq(api_key=GROQ_API_KEY)

MODELS = [
    "llama-3.1-8b-instant",
    "llama-3.3-70b-versatile"
]

def generate_script_backup(topic):
    try:
        prompt = f"Write a complete viral video script, retention hooks, and hashtags for: {topic}"
        encoded_prompt = urllib.parse.quote(prompt)
        url = f"https://text.pollinations.ai/{encoded_prompt}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        return f"Error: {str(e)}"

def generate_script(topic):
    if not topic or not topic.strip():
        return "Please enter a topic!"
    
    # 1. Try Groq API
    for model_id in MODELS:
        try:
            completion = client.chat.completions.create(
                model=model_id,
                messages=[{
                    "role": "user",
                    "content": f"Write a complete viral video script, retention hooks, and hashtags for: {topic}"
                }]
            )
            return completion.choices[0].message.content
        except Exception:
            continue
            
    # 2. Automatic Backup AI Engine (Zero API Key, Never fails)
    return generate_script_backup(topic)

demo = gr.Interface(
    fn=generate_script,
    inputs=gr.Textbox(label="Video Topic", placeholder="Enter topic (e.g. Fitness, Boxing)..."),
    outputs=gr.Textbox(label="Generated Script"),
    title="Viral AI Script Generator"
)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
