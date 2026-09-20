import os
import ssl
import json
import random
import time
import hashlib
import datetime
import urllib.request
import urllib.parse
import gradio as gr

ssl_context = ssl._create_unverified_context()

# ================= CONFIGURATION =================
MY_WHATSAPP_NUMBER = "917980890889"  # Tera WhatsApp Number
ADMIN_SECRET_KEY = "AZAM2026"         # Tera Admin Pass
KEY_SALT = "AZAM_SECRET_SALT_999"    # Key Protection

PAYMENT_LINK = f"https://wa.me/{MY_WHATSAPP_NUMBER}?text=Bro%20mujhe%20Viral%20Script%20AI%20ka%20subscription%20chahiye"

user_usage = {}

# --- DYNAMIC RANDOM FALLBACK SYSTEM (Har Baar Alag Script) ---
HOOKS = [
    "Ruko! Agar tum {topic} me secret growth chahte ho, toh ye 3 tips miss mat karna!",
    "Kya tum bhi {topic} me ye sabse badi galti kar rahe ho? Dhyan se suno!",
    "99% log {topic} ke baare me ye secret nahi jaante! Abhi dekho.",
    "Ye 1 simple trick tumhare {topic} ka pura game badal dega!",
    "Agar {topic} me pro banna hai, toh agle 30 seconds skip mat karna!"
]

INTROS = [
    "Most creators {topic} me bina plan ke aate hain aur fail ho jaate hain. Lekin aaj main tumhe proven formula bataunga.",
    "{topic} me success paana utna mushkil nahi hai jitna log sochte hain, bas sahi technique pata honi chahiye.",
    "Aaj main tumhe {topic} ke wo insider secrets dene wala hu jo koi bada creator nahi batata.",
    "Bina time waste kiye, chalo dekhte hain ki {topic} ko sahi tarike se kaise master karein."
]

TIPS_POOL = [
    ["Focus on core fundamentals and daily practice.", "Analyze top performers and learn from their moves.", "Be consistent for 30 days straight without excuses."],
    ["Stop copying others and build your own unique style.", "Track your progress weekly and adjust your strategy.", "Never ignore basic techniques and continuous improvement."],
    ["Quality > Quantity. Always double down on high-value execution.", "Build a solid routine and eliminate all distractions.", "Engage with the community to learn faster."]
]

CTAS = [
    "Agar ye secret pasand aaya toh abhi LIKE karke FOLLOW kar lo!",
    "Comment me batao tumhara favorite part kaunsa tha aur SHARE karo!",
    "Save kar lo ye reel warna baad me bhool jaoge! Follow for more."
]

def fallback_local_script(topic):
    topic_cap = topic.strip().capitalize()
    hook = random.choice(HOOKS).format(topic=topic_cap)
    intro = random.choice(INTROS).format(topic=topic_cap)
    tips = random.choice(TIPS_POOL)
    cta = random.choice(CTAS)
    rnd_num = random.randint(100, 999)
    
    return f"""🔥 **VIRAL SCRIPT FOR: {topic_cap}** 🔥

--- **1. ATTENTION HOOK (0-3 sec)** ---
"{hook}"

--- **2. RETENTION INTRO (3-10 sec)** ---
"{intro}"

--- **3. MAIN VALUE CONTENT (10-45 sec)** ---
• Tip 1: {tips[0]}
• Tip 2: {tips[1]}
• Tip 3: {tips[2]}

--- **4. CALL TO ACTION (CTA)** ---
"{cta}"

--- **5. VIRAL HASHTAGS** ---
#{topic_cap.replace(' ', '')} #{topic_cap.replace(' ', '')}Tips #ViralReels #TrendingNow #{rnd_num}
"""

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

# --- REAL AI GENERATOR WITH RANDOM SEED ---
def fetch_ai_script(topic):
    try:
        seed = random.randint(1000, 999999)
        prompt_text = f"Write a completely unique, highly viral short video script in Hinglish about {topic}. Include Retention Hook, Intro, 3 Concrete Tips, CTA, and Hashtags. Make it totally fresh and different (seed {seed})."
        encoded_prompt = urllib.parse.quote(prompt_text)
        
        url = f"https://text.pollinations.ai/{encoded_prompt}?model=openai&seed={seed}"
        
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req, context=ssl_context, timeout=12) as response:
            result = response.read().decode('utf-8')
            if result and len(result.strip()) > 50:
                return result
    except Exception:
        pass
    return None

def generate_script(topic, license_key, request: gr.Request):
    try:
        if not topic or not topic.strip():
            return "⚠️ **Please enter a video topic!**"
        
        clean_key = license_key.strip() if license_key else ""
        
        is_admin = (clean_key == ADMIN_SECRET_KEY)
        is_paid_client, key_msg = verify_client_key(clean_key) if clean_key else (False, "")

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

        # 1. Real AI Script Generator Try karo
        ai_response = fetch_ai_script(topic)
        if ai_response:
            return ai_response

        # 2. Random Dynamic Fallback Script
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
                placeholder="Enter topic (e.g. Fitness, Boxing, MMA, YouTube Growth)...",
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
