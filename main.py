import os
import ssl
import json
import random
import sqlite3
import hashlib
import datetime
import urllib.request
import urllib.parse
import gradio as gr

ssl_context = ssl._create_unverified_context()

# ================= CONFIGURATION =================
MY_WHATSAPP_NUMBER = "917980890889"
MY_UPI_ID = "7980890889@upi"
ADMIN_SECRET_KEY = "AZAM2026"
JSON_DB_FILE = "users_data.json"

PAYMENT_LINK = f"https://wa.me/{MY_WHATSAPP_NUMBER}?text=Bro%20mujhe%20Viral%20Script%20AI%20ka%20subscription%20chahiye"

# --- PERSISTENT JSON DATABASE ENGINE (Render Disk Reset Protection) ---
def load_db():
    if not os.path.exists(JSON_DB_FILE):
        default_data = {"users": {}, "history": [], "payments": {}}
        with open(JSON_DB_FILE, "w", encoding="utf-8") as f:
            json.dump(default_data, f, indent=4)
        return default_data
    try:
        with open(JSON_DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"users": {}, "history": [], "payments": {}}

def save_db(data):
    with open(JSON_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

# --- AUTH FUNCTIONS ---
def hash_pass(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    if not username or not password:
        return "⚠️ Please username aur password dono enter karein!"
    
    u_clean = username.strip().lower()
    if len(u_clean) < 3:
        return "⚠️ Username kam se kam 3 characters ka hona chahiye!"
        
    db = load_db()
    if u_clean in db["users"]:
        return "❌ Ye username pehle se exist karta hai! Abhi Login tab me jaakar login karein."
    
    today = datetime.date.today().strftime("%Y-%m-%d")
    db["users"][u_clean] = {
        "password": hash_pass(password),
        "vip_until": "FREE",
        "scripts_used": 0,
        "created_at": today
    }
    save_db(db)
    return f"✅ Account (@{u_clean}) ban gaya hai! Ab niche Login section me login karein."

def login_user(username, password):
    if not username or not password:
        return "⚠️ Username aur Password enter karein!", "guest"
    
    u_clean = username.strip().lower()
    db = load_db()
    
    if u_clean not in db["users"]:
        return "❌ User exist nahi karta! Pehle Register karein.", "guest"
    
    user = db["users"][u_clean]
    if user["password"] == hash_pass(password):
        return f"✅ **Welcome back @{u_clean}! Successfully Logged In.**", u_clean
    else:
        return "❌ Galat Password! Dubara try karein.", "guest"

# --- SCRIPT GENERATION ENGINE ---
HOOKS = [
    "Ruko! Agar tum {topic} me 10x growth chahte ho, toh ye 3 secrets miss mat karna!",
    "Kya tum bhi {topic} me ye sabse badi galti kar rahe ho? Dhyan se suno!",
    "99% log {topic} ke baare me ye secret formula nahi jaante! Abhi dekho."
]

INTROS = [
    "Most creators {topic} me bina strategy ke aate hain aur fail ho jaate hain. Lekin aaj main tumhe proven roadmap dunga.",
    "{topic} me success paana utna mushkil nahi hai jitna log sochte hain, bas sahi execution pata honi chahiye."
]

TIPS_SETS = [
    [
        "Tip 1: Always focus on strong execution and daily discipline.",
        "Tip 2: Analyze top performers in {topic} and reverse-engineer their success.",
        "Tip 3: Never stop learning—upgrade your techniques every single week."
    ]
]

CTAS = [
    "Agar ye content helpful laga toh abhi LIKE aur FOLLOW kar lo!",
    "Comment me batao tumhara favorite tip kaunsa tha aur dosto ke sath SHARE karo!"
]

def fallback_local_script(topic):
    topic_cap = topic.strip().capitalize()
    hook = random.choice(HOOKS).format(topic=topic_cap)
    intro = random.choice(INTROS).format(topic=topic_cap)
    tips = random.choice(TIPS_SETS)
    cta = random.choice(CTAS)
    rnd_num = random.randint(100, 999)
    
    return f"""### 🎬 VIRAL SCRIPT FOR: {topic_cap}

---

#### 📌 1. ATTENTION HOOK (0-3 Sec)
> 💥 "{hook}"

---

#### ⚡ 2. RETENTION INTRO (3-10 Sec)
> 🎯 "{intro}"

---

#### 💡 3. MAIN VALUE CONTENT (10-45 Sec)
* 📌 {tips[0].format(topic=topic_cap)}
* 📌 {tips[1].format(topic=topic_cap)}
* 📌 {tips[2].format(topic=topic_cap)}

---

#### 🚀 4. CALL TO ACTION (CTA)
> 🔥 "{cta}"

---

#### 🏷️ 5. VIRAL HASHTAGS
`#{topic_cap.replace(' ', '')}` `#{topic_cap.replace(' ', '')}Tips` `#ViralReels` `#TrendingNow` `#{rnd_num}`
"""

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
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ssl_context, timeout=12) as response:
            result = response.read().decode('utf-8')
            if result and len(result.strip()) > 50:
                return result
    except Exception:
        pass
    return None

def generate_script_authenticated(username_state, topic, vip_key):
    try:
        if not topic or not topic.strip():
            return "⚠️ **Pehle video ka topic enter karein!**", None
        
        target_user = username_state.strip().lower() if username_state else "guest"
        db = load_db()
        
        is_vip = False
        if target_user != "guest" and target_user in db["users"]:
            user = db["users"][target_user]
            vip_until = user.get("vip_until", "FREE")
            scripts_used = user.get("scripts_used", 0)
            
            if vip_until != "FREE":
                today = datetime.date.today().strftime("%Y-%m-%d")
                if vip_until >= today:
                    is_vip = True
            
            if not is_vip and scripts_used >= 2 and vip_key.strip() != ADMIN_SECRET_KEY:
                return f"""### 🔒 FREE LIMIT EXHAUSTED FOR (@{target_user})

Aapki 2 free scripts complete ho chuki hain! Unlimited access ke liye **Payment Tab** me jaakar ₹299 pay karke 12-Digit UTR enter karein ya VIP Key use karein!

👉 **[WHATSAPP PAR BUY KARNE KE LIYE YAHAN CLICK KAREIN]({PAYMENT_LINK})**
""", None

        # Script Generation
        script_output = fetch_ai_script(topic)
        if not script_output:
            script_output = fallback_local_script(topic)

        # Update JSON DB
        if target_user != "guest" and target_user in db["users"]:
            db["users"][target_user]["scripts_used"] += 1
            db["history"].append({
                "username": target_user,
                "topic": topic,
                "script": script_output,
                "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            save_db(db)

        # File Creation
        filename = f"Script_{topic.replace(' ', '_')}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(script_output)

        return script_output, filename

    except Exception as e:
        return f"❌ Error: {str(e)}", None

# --- STRICT UTR VERIFICATION ---
def submit_payment_utr(username, utr):
    if not username or username == "guest":
        return "❌ **Pehle Login Karo!** Account verify karne ke liye pehle login zaroori hai."
    
    utr_clean = utr.strip()
    if not utr_clean.isdigit() or len(utr_clean) != 12:
        return "❌ **INVALID UTR / TRANSACTION ID!**\n\nKripya sahi **12-digit numeric UTR** number enter karein (Jaise: `425619082341`). Fake text accept nahi hoga!"
    
    db = load_db()
    if utr_clean in db["payments"]:
        return "⚠️ **Ye UTR pehle se process ho chuka hai!** Naya transaction ID daalein."
    
    expiry = (datetime.date.today() + datetime.timedelta(days=30)).strftime("%Y-%m-%d")
    
    if username in db["users"]:
        db["users"][username]["vip_until"] = expiry
        db["payments"][utr_clean] = {
            "username": username,
            "status": "APPROVED",
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        save_db(db)
        return f"🎉 **PAYMENT SUCCESSFUL!**\n\nUTR `{utr_clean}` verify ho gaya hai! Account **@{username}** ko **{expiry}** tak VIP Access mil gaya hai."
    else:
        return "❌ User Account nahi mila. Pehle Login karein!"

# --- DASHBOARD LOAD ---
def load_user_dashboard(username):
    if not username or username == "guest":
        return "⚠️ Dashboard dekhne ke liye pehle **Login** karein."
    
    db = load_db()
    if username not in db["users"]:
        return "⚠️ User account nahi mila."
    
    u = db["users"][username]
    user_history = [h for h in db["history"] if h["username"] == username]
    user_history.reverse()
    
    out = f"### 👤 **User Profile Dashboard**\n"
    out += f"* 🆔 **Username:** `@{username}`\n"
    out += f"* 💎 **Subscription Status:** `{u.get('vip_until', 'FREE')}`\n"
    out += f"* 📊 **Total Scripts Generated:** `{u.get('scripts_used', 0)}`\n\n"
    out += f"--- \n### 📜 **Saved Scripts History**\n"
    
    if not user_history:
        out += "\n*Abhi tak koi saved script nahi hai. Generator tab me jaakar script banayein!*"
    else:
        for idx, r in enumerate(user_history[:10], 1):
            out += f"\n#### {idx}. 🎯 Topic: **{r['topic']}** *(Date: {r['created_at']})*\n```markdown\n{r['script'][:250]}...\n```\n"
            
    return out

# --- HIGH CONTRAST CSS (100% VISIBILITY FIX FOR ALL TEXT & HEADINGS) ---
custom_css = """
/* Background & Global Container */
body, .gradio-container, .main {
    background-color: #090d16 !important;
    color: #ffffff !important;
}

/* Force All Headings to High Contrast Cyan/White */
.gradio-container h1, 
.gradio-container h2, 
.gradio-container h3, 
.gradio-container h4, 
.gradio-container h5, 
.gradio-container h6,
.markdown-text h1, .markdown-text h2, .markdown-text h3, .markdown-text h4 {
    color: #38bdf8 !important;
    font-weight: 800 !important;
    margin-top: 10px !important;
    margin-bottom: 5px !important;
}

/* Force All Normal Text, List Items, and Paragraphs to Pure White */
.gradio-container p, 
.gradio-container li, 
.gradio-container ul, 
.gradio-container ol, 
.gradio-container span, 
.gradio-container label, 
.markdown-text p, 
.markdown-text li {
    color: #ffffff !important;
    font-size: 15px !important;
    line-height: 1.6 !important;
}

/* High Contrast Blockquotes for Script Hooks */
blockquote, blockquote p, blockquote span {
    background-color: #1e293b !important;
    border-left: 4px solid #8b5cf6 !important;
    color: #f8fafc !important;
    padding: 10px 14px !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
}

/* Container Cards */
div[class*="block"], .gr-form, .gr-box {
    background-color: #111827 !important;
    border: 1px solid #374151 !important;
    border-radius: 10px !important;
}

/* Input Text Fields */
input, textarea, select {
    background-color: #1f2937 !important;
    color: #ffffff !important;
    border: 1px solid #4b5563 !important;
    border-radius: 6px !important;
}

/* Primary Action Buttons */
.gr-button-primary {
    background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    border: none !important;
}
"""

# --- GRADIO INTERFACE ---
with gr.Blocks(css=custom_css, title="Viral Script AI Pro") as demo:
    
    active_user = gr.State(value="guest")
    
    gr.HTML("""
    <div style="background: linear-gradient(90deg, #1e1b4b 0%, #311b92 100%); padding: 20px; border-radius: 12px; text-align: center; border: 1px solid #6366f1; margin-bottom: 15px;">
        <h1 style="color: #ffffff !important; margin:0; font-size: 26px; font-weight: 800;">⚡ VIRAL SCRIPT AI PRO</h1>
        <p style="color: #e2e8f0 !important; margin-top: 5px; font-size: 14px;">Instant High Retention Scripts & SaaS Platform</p>
    </div>
    """)
    
    user_status_bar = gr.Markdown("🟢 **Status:** Guest Mode (Login to save history & get VIP)")
    
    with gr.Tab("🔐 Account Login / Register"):
        with gr.Row():
            with gr.Column():
                gr.Markdown("### 📝 Register Account")
                reg_user = gr.Textbox(label="Enter Username")
                reg_pass = gr.Textbox(label="Enter Password", type="password")
                reg_btn = gr.Button("Create Account", variant="primary")
                reg_output = gr.Markdown()
                reg_btn.click(fn=register_user, inputs=[reg_user, reg_pass], outputs=reg_output)
                
            with gr.Column():
                gr.Markdown("### 🔑 Login")
                log_user = gr.Textbox(label="Username")
                log_pass = gr.Textbox(label="Password", type="password")
                log_btn = gr.Button("Login Now", variant="primary")
                log_output = gr.Markdown()
                
                def handle_login(u, p):
                    msg, username = login_user(u, p)
                    if username != "guest":
                        status_text = f"🟢 **Logged in as:** @{username}"
                        return msg, username, status_text
                    return msg, "guest", "🟢 **Status:** Guest Mode"

                log_btn.click(
                    fn=handle_login, 
                    inputs=[log_user, log_pass], 
                    outputs=[log_output, active_user, user_status_bar]
                )

    with gr.Tab("🎬 Script Generator"):
        with gr.Row():
            topic_input = gr.Textbox(label="🎯 Enter Video Topic", placeholder="e.g. Boxing Workout, Gym Motivation...", scale=2)
            key_input = gr.Textbox(label="🔑 VIP Key / Admin Pass (Optional)", type="password", scale=1)
        
        submit_btn = gr.Button("🔥 Generate Viral Script", variant="primary")
        
        output_text = gr.Markdown(label="Generated Script Output")
        file_output = gr.File(label="📥 Download Script Text File")
        
        submit_btn.click(
            fn=generate_script_authenticated,
            inputs=[active_user, topic_input, key_input],
            outputs=[output_text, file_output]
        )

    with gr.Tab("💳 Instant UPI Payment"):
        gr.Markdown(f"""
        ### ⚡ Activate VIP Subscription (₹299 / Month)
        1. Pay ₹299 to UPI ID: `{MY_UPI_ID}`
        2. Enter your **12-Digit Numeric UTR / Transaction ID** below.
        """)
        
        utr_input = gr.Textbox(label="Enter 12-Digit UPI UTR Number", placeholder="e.g. 425619082341")
        pay_btn = gr.Button("🚀 Verify UTR & Activate VIP", variant="primary")
        pay_output = gr.Markdown()
        
        pay_btn.click(fn=submit_payment_utr, inputs=[active_user, utr_input], outputs=pay_output)

    with gr.Tab("📊 User Dashboard"):
        dash_refresh_btn = gr.Button("🔄 Refresh My Dashboard & History")
        dash_output = gr.Markdown()
        dash_refresh_btn.click(fn=load_user_dashboard, inputs=[active_user], outputs=dash_output)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
