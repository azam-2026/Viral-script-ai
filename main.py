import os
import ssl
import json
import random
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

# --- EXPANDED DYNAMIC FALLBACK POOLS ---
HOOKS = [
    "Ruko! Agar tum {topic} me 10x growth chahte ho, toh ye 3 secrets miss mat karna!",
    "Kya tum bhi {topic} me ye sabse badi galti kar rahe ho? Dhyan se suno!",
    "99% log {topic} ke baare me ye secret formula nahi jaante! Abhi dekho.",
    "Ye 1 simple strategy tumhare {topic} ka pura game badal degi!",
    "Agar {topic} me master banna hai, toh agle 30 seconds skip mat karna!"
]

INTROS = [
    "Most creators {topic} me bina strategy ke aate hain aur fail ho jaate hain. Lekin aaj main tumhe proven roadmap dunga.",
    "{topic} me success paana utna mushkil nahi hai jitna log sochte hain, bas sahi execution pata honi chahiye.",
    "Aaj main tumhe {topic} ke wo insider secrets dene wala hu jo koi bada creator khulkar nahi batata.",
    "Bina time waste kiye, chalo dekhte hain ki {topic} ko step-by-step kaise master karein."
]

TIPS_SETS = [
    [
        "**Tip 1:** Always focus on strong execution and daily discipline.",
        "**Tip 2:** Analyze top performers in {topic} and reverse-engineer their success.",
        "**Tip 3:** Never stop learning—upgrade your techniques every single week."
    ],
    [
        "**Tip 1:** Stop copying others; build your own unique brand style.",
        "**Tip 2:** Track your weekly progress metrics and eliminate weak spots.",
        "**Tip 3:** Master the basics first before jumping into advanced tactics."
    ],
    [
        "**Tip 1:** Quality always beats quantity—deliver maximum value in minimum time.",
        "**Tip 2:** Maintain a structured daily routine without breaking consistency.",
        "**Tip 3:** Engage with your audience to build a loyal community."
    ]
]

CTAS = [
    "Agar ye content helpful laga toh abhi **LIKE** aur **FOLLOW** kar lo!",
    "Comment me batao tumhara favorite tip kaunsa tha aur dosto ke sath **SHARE** karo!",
    "Is reel ko **SAVE** kar lo warna baad me bhool jaoge! Follow for daily growth."
]

def fallback_local_script(topic):
    topic_cap = topic.strip().capitalize()
    hook = random.choice(HOOKS).format(topic=topic_cap)
    intro = random.choice(INTROS).format(topic=topic_cap)
    tips = random.choice(TIPS_SETS)
    cta = random.choice(CTAS)
    rnd_num = random.randint(100, 999)
    
    t1 = tips[0].format(topic=topic_cap)
    t2 = tips[1].format(topic=topic_cap)
    t3 = tips[2].format(topic=topic_cap)
    
    return f"""### 🎬 **VIRAL SCRIPT FOR: {topic_cap}**

---

#### 📌 **1. ATTENTION HOOK (0-3 Sec)**
> 💥 "{hook}"

---

#### ⚡ **2. RETENTION INTRO (3-10 Sec)**
> 🎯 "{intro}"

---

#### 💡 **3. MAIN VALUE CONTENT (10-45 Sec)**
* 📌 {t1}

* 📌 {t2}

* 📌 {t3}

---

#### 🚀 **4. CALL TO ACTION (CTA)**
> 🔥 "{cta}"

---

#### 🏷️ **5. VIRAL HASHTAGS**
`#{topic_cap.replace(' ', '')}` `#{topic_cap.replace(' ', '')}Tips` `#ViralReels` `#TrendingNow` `#{rnd_num}`
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

# --- REAL AI SCRIPT FETCH ---
def fetch_ai_script(topic):
    try:
        seed = random.randint(1000, 999999)
        prompt_text = (
            f"Write a viral short video script in Hinglish about '{topic}'. "
            f"Strictly format it in markdown with separate line breaks for each section:\n"
            f"1. Attention Hook (0-3s)\n"
            f"2. Retention Intro (3-10s)\n"
            f"3. Main Value Content (10-45s) - write 3 distinct bullet points on NEW lines.\n"
            f"4. Call To Action (CTA)\n"
            f"5. Viral Hashtags\n"
            f"Make it unique and high retention (Seed: {seed})."
        )
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
            return "⚠️ **Please enter a video topic first!**"
        
        clean_key = license_key.strip() if license_key else ""
        
        is_admin = (clean_key == ADMIN_SECRET_KEY)
        is_paid_client, key_msg = verify_client_key(clean_key) if clean_key else (False, "")

        if not is_admin and not is_paid_client:
            client_ip = request.client.host if request else "default_user"
            current_count = user_usage.get(client_ip, 0)
            
            if current_count >= 2:
                status_note = f"\n\n*(Reason: {key_msg})*" if (clean_key and not is_paid_client) else ""
                return f"""### 🔒 **FREE TRIAL EXHAUSTED!**{status_note}

Aapki 2 free scripts complete ho chuki hain. Unlimited AI Script generation ke liye subscription lein:

👉 **[CLICK HERE TO PAY & UNLOCK UNLIMITED VIP ACCESS (₹299/MONTH)]({PAYMENT_LINK})**

*(Upar Blue Link par click karke WhatsApp par DM karein. Payment ke baad instant 1-Month Access Key mil jayega!)*
"""
            user_usage[client_ip] = current_count + 1

        # 1. Real AI Fetch
        ai_response = fetch_ai_script(topic)
        if ai_response:
            return ai_response

        # 2. Dynamic Fallback
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

# --- GRADIO INTERFACE (PAISA VASOOL LOOK) ---
with gr.Blocks(title="Viral AI Script Generator Pro v2.0") as demo:
    gr.Markdown("""
    # ⚡ **Viral AI Script Generator Pro v2.0**
    > *Welcome! Create High-Retention Viral Video Scripts in 5 Seconds.*
    
    ---
    """)
    
    with gr.Tab("🎬 Script Generator"):
        with gr.Row():
            topic_input = gr.Textbox(
                label="🎯 Video Topic", 
                placeholder="Enter topic (e.g. Fitness, Boxing, MMA, YouTube Growth, Business)...",
                scale=2
            )
            key_input = gr.Textbox(
                label="🔑 VIP Access Key / Admin Pass (Optional)", 
                placeholder="Enter VIP Key for Unlimited Access...", 
                type="password",
                scale=1
            )
        
        submit_btn = gr.Button("🔥 Generate Viral Script Now", variant="primary")
        
        gr.Markdown("### 📜 Generated Script Output")
        output_text = gr.Markdown()
        
        submit_btn.click(
            fn=generate_script,
            inputs=[topic_input, key_input],
            outputs=output_text
        )

    with gr.Tab("🔑 Admin Panel (For Owner)"):
        gr.Markdown("### 🛠️ Generate 30-Day VIP Access Keys")
        admin_pass_input = gr.Textbox(label="Enter Admin Secret Pass", type="password", placeholder="AZAM2026")
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
