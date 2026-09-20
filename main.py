import os
import gradio as gr
from groq import Groq

# Teri Groq API key pre-filled hai
GROQ_API_KEY = "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"

client = Groq(api_key=GROQ_API_KEY)

def generate_script(topic):
    if not topic or not topic.strip():
        return "Please enter a topic!"
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{
                "role": "user",
                "content": f"Write a complete viral video script, retention hooks, and hashtags for: {topic}"
            }]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

demo = gr.Interface(
    fn=generate_script,
    inputs=gr.Textbox(label="Video Topic", placeholder="Enter topic (e.g. Fitness tips)..."),
    outputs=gr.Textbox(label="Generated Script"),
    title="Viral AI Script Generator"
)

if __name__ == "__main__":
    # Render dynamic port fix
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
