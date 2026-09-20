import os
import json
import urllib.request
import urllib.parse
import gradio as gr

def generate_script(topic):
    if not topic or not topic.strip():
        return "Please enter a topic!"
    
    prompt = f"Write a complete viral video script, retention hooks, and hashtags for: {topic}"
    
    # Method 1: JSON POST Request (Bypasses 429 Rate Limits & GitHub key revocation)
    try:
        url = "https://text.pollinations.ai/"
        payload = json.dumps({
            "messages": [
                {"role": "system", "content": "You are an expert viral video scriptwriter."},
                {"role": "user", "content": prompt}
            ],
            "model": "openai",
            "seed": 42
        }).encode('utf-8')
        
        req = urllib.request.Request(
            url, 
            data=payload, 
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
            }
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            res_text = response.read().decode('utf-8')
            if res_text and len(res_text.strip()) > 0:
                return res_text
    except Exception:
        pass

    # Method 2: Automatic Fallback Engine
    try:
        encoded_prompt = urllib.parse.quote(prompt)
        url_fb = f"https://text.pollinations.ai/{encoded_prompt}?model=mistral"
        req_fb = urllib.request.Request(
            url_fb, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req_fb, timeout=30) as resp_fb:
            return resp_fb.read().decode('utf-8')
    except Exception:
        return "Server thoda busy hai, please 5 seconds baad dobara Submit par click karo."

demo = gr.Interface(
    fn=generate_script,
    inputs=gr.Textbox(label="Video Topic", placeholder="Enter topic (e.g. Youtube, Fitness, Boxing)..."),
    outputs=gr.Textbox(label="Generated Script"),
    title="Viral AI Script Generator"
)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
