import os
import ssl
import json
import hashlib
import datetime
import urllib.request
import urllib.parse
import gradio as gr

ssl_context = ssl._create_unverified_context()

# ================= CONFIGURATION =================
MY_WHATSAPP_NUMBER = "917980890889"  # Tera WhatsApp Number
ADMIN_SECRET_KEY = "AZAM2026"         # Tera Admin Pass
KEY_SALT = "AZAM_SECRET_SALT_999"    # Key Tamper Protection

PAYMENT_LINK = f"https://wa.me/{MY_WHATSAPP_NUMBER}?text=Bro%20mujhe%20Viral%20Script%20AI%20ka%20subscription%20chahiye"

user_usage = {}

def fallback_local_script(topic):
    topic_cap = topic.strip().capitalize()
    return f"""🔥 **VIRAL SCRIPT FOR: {topic_cap}** 🔥

--- **1. ATTENTION HOOK (0-3 sec)** ---
"Ruko! Agar tum {topic_cap} me grow karna chahte ho, toh ye 3 galtiyan bilkul mat karna!"

--- **2. RETENTION INTRO (3-10 sec)** ---
"90% log {topic_cap} me fail ho jaate hain. Aaj main bataunga secret formula jo kaam karta hai."

--- **3. MAIN VALUE CONTENT (10-45 sec)** ---
• Tip 1: Consistency aur clear strategy banao.
• Tip 2: Quality pe focus karo aur roz improvement dekho.
• Tip 3: Audience ke sath strong connection banao.

--- **4. CALL TO ACTION (CTA)** ---
"Agar ye tips helpful lagi toh abhi LIKE aur FOLLOW karo!"

--- **5. VIRAL HASHTAGS** ---
#{topic_cap.replace(' ', '')} #ViralReels #TrendingNow #ContentCreation
"""

# --- 1-MONTH AUTO EXPIRY LOGIC ---
def generate_client_key(days=30):
    expiry_date = datetime.date.today() + datetime.timedelta(days=days)
    date_str = expiry_date.strftime("%Y%m%d")
    raw_signature = f"{date_str}_{KEY_SALT}"
    sig = hashlib.sha256(raw_signature.encode()).hexdigest()[:6].upper()
    return f"VIP-{date_str}-{sig}"

def verify_client_key(key_str):
    try:
        parts = key_str.strip().upper().split("-")
        if len(parts) != 3 or parts[0] != "VIP":
            return False, "Invalid Key Format"
        
        date_str, sig = parts[1], parts[2]
        expected_sig = hashlib.sha256(f"{date_str}_{KEY_SALT}".encode()).hexdigest()[:6].upper()
        
        if sig != expected_sig:
            return False, "Invalid Key"
            
        expiry_date = datetime.datetime.strptime(date_str, "%Y%m%d").date()
        today = datetime.date.today()
        
        if today > expiry_date:
            return False, f"Key Expired on {expiry_date.strftime('%d-%b-%Y')}"
            
        return True, f"Valid until {expiry_date.strftime('%d-%b-%Y')}"
    except Exception:
        return False, "Invalid Key"

# --- MAIN AI GENERATOR ---
def generate_script(topic, license_key, request: gr.Request):
    try:
        if not topic or not topic.strip():
            return "⚠️ **Please enter a video topic!**"
        
        clean_key = license_key.strip() if license_key else ""
        
        is_admin = (clean_key == ADMIN_SECRET_KEY)
        is_paid_client, key_msg = verify_client_key(clean_key) if clean_key else (False, "")

        # Free User Tracking (2 Free Generations)
        if not is_admin and not is_paid_client:
            client_ip = request.client.host if request else "default_user"
            current_count = user_usage.get(client_ip, 0)
            
            if current_count >= 2:
                status_note = f"\n\n*(Reason: {key_msg})*" if (clean_key and not is_paid_client) else ""
                return f"""🔒 **FREE TRIAL EXHAUSTED!**{status_note}

Aapki 2 free scripts complete ho chuki hain. Unlimited AI Script generation ke liye subscription lein:

👉 **[CLICK HERE TO PAY & UNLOCK UNLIMITED ACCESS (₹299/MONTH)]({PAYMENT_LINK})**

*(Upar Blue Link par click karke WhatsApp par DM karein, payment ke baad aapko 1 Month VIP Access Key mil jayega)*
"""
            user_usage[client_ip] = current_count + 1

        prompt = f"Write a complete viral video script, retention hooks, body content, CTA, and hashtags for topic: {topic}"
        
        try:
            url = "https://text.pollinations.ai/"
            payload = json.dumps({
                "messages": [
                    {"role": "system", "content": "You are a top viral content creator and scriptwriter."},
                    {"role": "user", "content": prompt}
                ],
                "model": "openai"
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
            pass

        return fallback_local_script(topic)
        
    except Exception as e:
        return f"❌ Error: {str(e)}"

# --- ADMIN PANEL LOGIC ---
def admin_generate_key(admin_pass):
    if admin_pass.strip() == ADMIN_SECRET_KEY:
        new_key = generate_client_key(days=30)
        return f"✅ **New 30-Day VIP Key Generated:**\n\n`{new_key}`\n\n*(Copy this key and send to client. Automatically valid for 30 days!)*"
    else:
        return "❌ Incorrect Admin Pass!"

# Gradio Interface Setup
with gr.Blocks(title="Viral AI Script Generator Pro") as demo:
    gr.Markdown("# 🚀 **Viral AI Script Generator Pro (SaaS)**")
    
    with gr.Tab("🎬 Script Generator"):
        with gr.Row():
            topic_input = gr.Textbox(
                label="Video Topic", 
                placeholder="Enter topic (e.g. Fitness, Boxing, YouTube Growth)...",
                scale=2
            )
            key_input = gr.Textbox(
                label="License / VIP Key (Optional)", 
                placeholder="Enter Pass or VIP Key...", 
                type="password",
                scale=1
            )
        
        submit_btn = gr.Button("🔥 Generate Viral Script", variant="primary")
        output_text = gr.Markdown(label="Generated Script / Output")
        
        submit_btn.click(
            fn=generate_script,
            inputs=[topic_input, key_input],
            outputs=output_text
        )

    with gr.Tab("🔑 Admin Key Generator (For You)"):
        gr.Markdown("### 🛠️ Generate 30-Day VIP Keys For Paid Customers")
        admin_pass_input = gr.Textbox(label="Enter Admin Pass", type="password", placeholder="AZAM2026")
        gen_btn = gr.Button("Generate 1-Month Key", variant="secondary")
        key_output = gr.Markdown()
        
        gen_btn.click(
            fn=admin_generate_key,
            inputs=[admin_pass_input],
            outputs=key_output
        )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
