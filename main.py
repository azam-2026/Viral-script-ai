import os
import ssl
import json
import urllib.request
import urllib.parse
import gradio as gr

ssl_context = ssl._create_unverified_context()

# TERI CONFIGURATION (Yahan apna Admin Code aur Payment Link set kar)
ADMIN_SECRET_KEY = "AZAM2026"  # Ye tera Secret Code hai
PAYMENT_LINK = "https://razorpay.me/@yourlink" # Tera Razorpay UPI Payment Link

# Session tracker for free limit
user_usage = {}

def fallback_local_script(topic):
    topic_cap = topic.strip().capitalize()
    return f"""🔥 VIRAL SCRIPT FOR: {topic_cap} 🔥

--- 1. ATTENTION HOOK (0-3 sec) ---
"Ruko! Agar tum {topic_cap} me grow karna chahte ho, toh ye 3 galtiyan bilkul mat karna!"

--- 2. RETENTION INTRO (3-10 sec) ---
"90% log {topic_cap} me fail ho jaate hain. Aaj main bataunga secret formula jo kaam karta hai."

--- 3. MAIN VALUE CONTENT (10-45 sec) ---
• Tip 1: Consistency aur clear strategy banao.
• Tip 2: Quality pe focus karo aur roz improvement dekho.
• Tip 3: Audience ke sath strong connection banao.

--- 4. CALL TO ACTION (CTA) ---
"Agar ye tips helpful lagi toh abhi LIKE aur FOLLOW karo!"

--- 5. VIRAL HASHTAGS ---
#{topic_cap.replace(' ', '')} #ViralReels #TrendingNow #ContentCreation
"""

def generate_script(topic, license_key, request: gr.Request):
    if not topic or not topic.strip():
        return "Please enter a topic!"
    
    # Check Admin Pass
    if license_key and license_key.strip() == ADMIN_SECRET_KEY:
        is_admin = True
    else:
        is_admin = False

    # Free Limit Tracking
    client_ip = request.client.host if request else "default_user"
    
    if not is_admin:
        current_count = user_usage.get(client_ip, 0)
        if current_count >= 2:
            return f"""🔒 FREE LIMIT EXHAUSTED!

Aapki 2 free scripts complete ho chuki hain. Unlimited access ke liye subscription lein:

👉 Unlock Unlimited Scripts (₹299/Month):
{PAYMENT_LINK}

(Payment ke baad Admin Code activate karwane ke liye DM karein)
"""
        user_usage[client_ip] = current_count + 1

    prompt = f"Write a complete viral video script, retention hooks, body content, CTA, and hashtags for topic: {topic}"
    
    # Try AI Models
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
                url, data=payload, 
                headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
            )
            with urllib.request.urlopen(req, context=ssl_context, timeout=10) as response:
                result = response.read().decode('utf-8')
                if result and len(result.strip()) > 30:
                    return result
        except Exception:
            continue

    return fallback_local_script(topic)

# Gradio Interface Setup
with gr.Blocks(title="Viral AI Script Generator") as demo:
    gr.Markdown("# 🚀 Viral AI Script Generator (SaaS)")
    
    with gr.Row():
        topic_input = gr.Textbox(label="Video Topic", placeholder="Enter topic (e.g. Fitness, Boxing, Youtube)...")
        key_input = gr.Textbox(label="Admin / License Key (Optional)", placeholder="Enter Secret Pass for Unlimited Access...", type="password")
    
    submit_btn = gr.Button("Generate Script", variant="primary")
    output_text = gr.Textbox(label="Generated Script / Output", lines=12)
    
    submit_btn.click(
        fn=generate_script,
        inputs=[topic_input, key_input],
        outputs=output_text
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
