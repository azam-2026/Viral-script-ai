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
MY_WHATSAPP_NUMBER = "917980890889"  # WhatsApp Number
MY_UPI_ID = "7980890889@upi"          # UPI ID for Payment
ADMIN_SECRET_KEY = "AZAM2026"         # Admin Secret Key
DB_FILE = "app_database.db"          # SQLite Database File

PAYMENT_LINK = f"https://wa.me/{MY_WHATSAPP_NUMBER}?text=Bro%20mujhe%20Viral%20Script%20AI%20ka%20subscription%20chahiye"

# --- 1. SQLITE DATABASE INITIALIZATION ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            vip_until TEXT,
            scripts_used INTEGER DEFAULT 0,
            created_at TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            topic TEXT,
            script TEXT,
            created_at TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            utr TEXT PRIMARY KEY,
            username TEXT,
            status TEXT,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- AUTH & SECURITY FUNCTIONS ---
def hash_pass(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    if not username or not password:
        return "⚠️ Kripya username aur password dono enter karein!"
    
    u_clean = username.strip().lower()
    if len(u_clean) < 3:
        return "⚠️ Username kam se kam 3 characters ka hona chahiye!"
        
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE username = ?", (u_clean,))
    if cursor.fetchone():
        conn.close()
        return "❌ Ye username pehle se exist karta hai! Dusra try karein ya Login karein."
    
    hashed = hash_pass(password)
    today = datetime.date.today().strftime("%Y-%m-%d")
    cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)", 
                   (u_clean, hashed, "FREE", 0, today))
    conn.commit()
    conn.close()
    return "✅ Account Safaltapoorvak Ban Gaya! Ab Login tab me jaakar login karein."

def login_user(username, password):
    if not username or not password:
        return "⚠️ Username aur Password enter karein!", "guest"
    
    u_clean = username.strip().lower()
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    hashed = hash_pass(password)
    cursor.execute("SELECT username, vip_until, scripts_used FROM users WHERE username = ? AND password = ?", 
                   (u_clean, hashed))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return f"✅ **Login Successful! Welcome @{user[0]}**", user[0]
    else:
        return "❌ Galat Username ya Password!", "guest"

# --- AI & FALLBACK SCRIPT GENERATOR ---
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
        "**Tip 1:** Always focus on strong execution and daily discipline.",
        "**Tip 2:** Analyze top performers in {topic} and reverse-engineer their success.",
        "**Tip 3:** Never stop learning—upgrade your techniques every single week."
    ]
]

CTAS = [
    "Agar ye content helpful laga toh abhi **LIKE** aur **FOLLOW** kar lo!",
    "Comment me batao tumhara favorite tip kaunsa tha aur dosto ke sath **SHARE** karo!"
]

def fallback_local_script(topic):
    topic_cap = topic.strip().capitalize()
    hook = random.choice(HOOKS).format(topic=topic_cap)
    intro = random.choice(INTROS).format(topic=topic_cap)
    tips = random.choice(TIPS_SETS)
    cta = random.choice(CTAS)
    rnd_num = random.randint(100, 999)
    
    return f"""### 🎬 **VIRAL SCRIPT FOR: {topic_cap}**

---

#### 📌 **1. ATTENTION HOOK (0-3 Sec)**
> 💥 "{hook}"

---

#### ⚡ **2. RETENTION INTRO (3-10 Sec)**
> 🎯 "{intro}"

---

#### 💡 **3. MAIN VALUE CONTENT (10-45 Sec)**
* 📌 {tips[0].format(topic=topic_cap)}
* 📌 {tips[1].format(topic=topic_cap)}
* 📌 {tips[2].format(topic=topic_cap)}

---

#### 🚀 **4. CALL TO ACTION (CTA)**
> 🔥 "{cta}"

---

#### 🏷️ **5. VIRAL HASHTAGS**
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
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        is_vip = False
        if target_user != "guest":
            cursor.execute("SELECT vip_until, scripts_used FROM users WHERE username = ?", (target_user,))
            user_data = cursor.fetchone()
            if user_data:
                vip_until, scripts_used = user_data[0], user_data[1]
                if vip_until != "FREE":
                    today = datetime.date.today().strftime("%Y-%m-%d")
                    if vip_until >= today:
                        is_vip = True
                
                if not is_vip and scripts_used >= 2 and vip_key.strip() != ADMIN_SECRET_KEY:
                    conn.close()
                    return f"""### 🔒 **FREE LIMIT EXHAUSTED FOR (@{target_user})**

Aapki 2 free scripts complete ho chuki hain! Unlimited access ke liye **Payment Tab** me jaakar ₹299 pay karke 12-Digit UTR enter karein ya VIP Key use karein!

👉 **[WHATSAPP PAR BUY KARNE KE LIYE YAHAN CLICK KAREIN]({PAYMENT_LINK})**
""", None

        # Script Generation
        script_output = fetch_ai_script(topic)
        if not script_output:
            script_output = fallback_local_script(topic)

        # Database Update
        if target_user != "guest":
            cursor.execute("UPDATE users SET scripts_used = scripts_used + 1 WHERE username = ?", (target_user,))
            cursor.execute("INSERT INTO history (username, topic, script, created_at) VALUES (?, ?, ?, ?)",
                           (target_user, topic, script_output, datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
            conn.commit()
        conn.close()

        # File Creation
        filename = f"Script_{topic.replace(' ', '_')}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(script_output)

        return script_output, filename

    except Exception as e:
        return f"❌ Error: {str(e)}", None

# --- STRICT UTR VERIFICATION SYSTEM (FIXED BUG) ---
def submit_payment_utr(username, utr):
    if not username or username == "guest":
        return "❌ **Pehle Login Karo!** Payment verify karne ke liye pehle account login hona zaroori hai."
    
    utr_clean = utr.strip()
    
    # STRICT VALIDATION: Exactly 12 digits and ONLY NUMBERS
    if not utr_clean.isdigit() or len(utr_clean) != 12:
        return "❌ **INVALID UTR / TRANSACTION ID!**\n\nKripya sahi **12-digit numeric UTR** number enter karein (Jaise: `425619082341`). Fake text, letters ya galat length accept nahi hogi!"
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Check duplicate UTR
    cursor.execute("SELECT utr FROM payments WHERE utr = ?", (utr_clean,))
    if cursor.fetchone():
        conn.close()
        return "⚠️ **Ye UTR pehle se process ho chuka hai!** Kripya apna new Transaction ID daalein."
    
    # Valid UTR - Grant 30 Days VIP
    expiry = (datetime.date.today() + datetime.timedelta(days=30)).strftime("%Y-%m-%d")
    cursor.execute("UPDATE users SET vip_until = ? WHERE username = ?", (expiry, username.strip().lower()))
    cursor.execute("INSERT INTO payments VALUES (?, ?, ?, ?)", 
                   (utr_clean, username.strip().lower(), "APPROVED", datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    conn.close()
    
    return f"🎉 **PAYMENT SUCCESSFUL!**\n\nUTR `{utr_clean}` successfully verify ho gaya hai! Account **@{username}** ko **{expiry}** tak VIP Unlimited Access mil gaya hai."

# --- DASHBOARD LOAD ---
def load_user_dashboard(username):
    if not username or username == "guest":
        return "⚠️ Dashboard dekhne ke liye pehle **Login** karein."
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT vip_until, scripts_used, created_at FROM users WHERE username = ?", (username.strip().lower(),))
    u = cursor.fetchone()
    
    cursor.execute("SELECT topic, created_at, script FROM history WHERE username = ? ORDER BY id DESC LIMIT 10", (username.strip().lower(),))
    history_rows = cursor.fetchall()
    conn.close()
    
    status = u[0] if u else "FREE"
    used = u[1] if u else 0
    
    out = f"### 👤 **User Profile Dashboard**\n"
    out += f"* 🆔 **Username:** `@{username}`\n"
    out += f"* 💎 **Subscription Status:** `{status}`\n"
    out += f"* 📊 **Total Scripts Generated:** `{used}`\n\n"
    out += f"--- \n### 📜 **Saved Scripts History**\n"
    
    if not history_rows:
        out += "\n*Abhi tak koi saved script nahi hai. Generator tab me jaakar script banayein!*"
    else:
        for idx, r in enumerate(history_rows, 1):
            out += f"\n#### {idx}. 🎯 Topic: **{r[0]}** *(Date: {r[1]})*\n```markdown\n{r[2][:250]}...\n```\n"
            
    return out

# --- HIGH CONTRAST DARK MODE CSS (MOBILE FRIENDLY) ---
custom_css = """
/* Force High Contrast Text & Colors */
body, .gradio-container {
    background-color: #0b0f19 !important;
    color: #ffffff !important;
    font-family: 'Inter', sans-serif !important;
}

/* Fix Unreadable Text Bug */
p, span, label, h1, h2, h3, h4, h5, h6, .markdown-text, .gr-text-input, code {
    color: #f1f5f9 !important;
}

/* Card Boxes */
div[class*="block"], .gr-form, .gr-box {
    background-color: #161e2e !important;
    border: 1px solid #374151 !important;
    border-radius: 10px !important;
}

/* Input Fields */
input, textarea, select {
    background-color: #1e293b !important;
    color: #ffffff !important;
    border: 1px solid #475569 !important;
    border-radius: 6px !important;
    font-size: 15px !important;
}

/* Primary Action Buttons */
.gr-button-primary {
    background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 8px !important;
}

/* Active Tabs */
button[role="tab"] {
    color: #9ca3af !important;
    font-weight: 600 !important;
    background: transparent !important;
}

button[role="tab"][aria-selected="true"] {
    color: #ffffff !important;
    border-bottom: 3px solid #8b5cf6 !important;
    background-color: #1e293b !important;
}
"""

# --- GRADIO INTERFACE ---
with gr.Blocks(css=custom_css, title="Viral Script AI Pro") as demo:
    
    active_user = gr.State(value="guest")
    
    gr.HTML("""
    <div style="background: linear-gradient(90deg, #1e1b4b 0%, #311b92 100%); padding: 20px; border-radius: 12px; text-align: center; border: 1px solid #6366f1; margin-bottom: 15px;">
        <h1 style="color: #ffffff; margin:0; font-size: 26px; font-weight: 800;">⚡ VIRAL SCRIPT AI PRO</h1>
        <p style="color: #e2e8f0; margin-top: 5px; font-size: 14px;">Instant High Retention Scripts & Automated SaaS Platform</p>
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
            topic_input = gr.Textbox(label="🎯 Enter Video Topic", placeholder="e.g. Boxing Workout, Gym Motivation, Mobile Editing...", scale=2)
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
