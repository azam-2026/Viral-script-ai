import os
import ssl
import json
import urllib.request
import urllib.parse
import gradio as gr

# Render par SSL Certificate error bypass karne ke liye
ssl_context = ssl._create_unverified_context()

def fallback_local_script(topic):
    topic_cap = topic.strip().capitalize()
    return f"""🔥 VIRAL SCRIPT FOR: {topic_cap} 🔥

--- 1. ATTENTION HOOK (0-3 sec) ---
"Ruko! Agar tum {topic_cap} me grow karna chahte ho, toh ye 3 galtiyan bilkul mat karna!"

--- 2. RETENTION INTRO (3-10 sec) ---
"90% log {topic_cap} me fail ho jaate hain kyunki wo galat tarika use karte hain. Aaj main bataunga secret formula jo kaam karta hai."

--- 3. MAIN VALUE CONTENT (10-45 sec) ---
• Tip 1: Consistency aur clear strategy banao.
• Tip 2: Quality pe focus karo aur roz improvement dekho.
• Tip 3: Audience ke sath strong connection banao.

--- 4. CALL TO ACTION (CTA) ---
"Agar ye tips helpful lagi toh abhi LIKE aur FOLLOW karo daily viral content ke liye!"

--- 5. VIRAL HASHTAGS ---
#{topic_cap.replace(' ', '')} #ViralReels #TrendingNow #ContentCreation #GrowthHacks
"""

def generate_script(topic):
    if not topic or not topic.strip():
        return "Please enter a topic!"
    
    prompt = f"Write a complete viral video script, retention hooks, body content, CTA, and hashtags for topic: {topic}"
    
    # 1. Try Online AI Models with SSL Bypass
    models = ["openai", "mistral", "qwen"]
    for m in models:
        try:
            url = "https://text.pollinations.ai/"
            payload = json.dumps({
                "messages": [
                    {"role": "system", "content": "You are a top viral content creator and scriptwriter."},
                    {"role": "user", "content": prompt}
                ],
                "model": m
            }).encode('utf-8')
            
            req = urllib.request.Request(
                url,
                data=payload,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
                }
            )
            with urllib.request.urlopen(req, context=ssl_context, timeout=10) as response:
                result = response.read().decode('utf-8')
                if result and len(result.strip()) > 30:
                    return result
        except Exception:
            continue

    # 2. Secondary AI GET Request Backup
    try:
        encoded_prompt = urllib.parse.quote(prompt)
        url_get = f"https://text.pollinations.ai/{encoded_prompt}"
        req_get = urllib.request.Request(
            url_get,
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req_get, context=ssl_context, timeout=10) as response:
            result = response.read().decode('utf-8')
            if result and len(result.strip()) > 30:
                return result
    except Exception:
        pass

    # 3. 100% Guaranteed Local Script Generator (Never fails)
    return fallback_local_script(topic)

demo = gr.Interface(
    fn=generate_script,
    inputs=gr.Textbox(label="Video Topic", placeholder="Enter topic (e.g. Fitness, Boxing, Youtube)..."),
    outputs=gr.Textbox(label="Generated Script"),
    title="Viral AI Script Generator"
)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
