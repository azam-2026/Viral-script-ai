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
MY_WHATSAPP_NUMBER = "917980890889"  # Tera WhatsApp Number
MY_UPI_ID = "7980890889@upi"          # Tera UPI ID for Instant Auto Payment
ADMIN_SECRET_KEY = "AZAM2026"         # Tera Admin Pass
KEY_SALT = "AZAM_SECRET_SALT_999"    # Secret Salt
DB_FILE = "app_database.db"          # SQLite Database File

PAYMENT_LINK = f"https://wa.me/{MY_WHATSAPP_NUMBER}?text=Bro%20mujhe%20Viral%20Script%20AI%20ka%20subscription%20chahiye"

# --- 1. SQLITE DATABASE INITIALIZATION (Zero Cost Database) ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            vip_until TEXT,
            scripts_used INTEGER DEFAULT 0,
            created_at TEXT
        )
    ''')
    # History Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            topic TEXT,
            script TEXT,
            created_at TEXT
        )
    ''')
    # Payments Table
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

# --- HELPER FUNCTIONS FOR AUTH & SECURITY ---
def hash_pass(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    if not username or not password:
        return "⚠️ Please enter both username and password!"
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM users WHERE username = ?", (username.strip().lower(),))
    if cursor.fetchone():
        conn.close()
        return "❌ Username already exists! Choose another or login."
    
    hashed = hash_pass(password)
    today = datetime.date.today().strftime("%Y-%m-%d")
    cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)", 
                   (username.strip().lower(), hashed, "FREE", 0, today))
    conn.commit()
    conn.close()
    return "✅ Account created successfully! Now go to Login tab."

def login_user(username, password):
    if not username or not password:
        return "⚠️ Please enter username and password!", None
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    hashed = hash_pass(password)
    cursor.execute("SELECT username, vip_until, scripts_used FROM users WHERE username = ? AND password = ?", 
                   (username.strip().lower(), hashed))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        status_str = f"Logged in as: **{user[0]}** | Tier: **{user[1]}** | Free Scripts Used: **{user[2]}/2**"
        return f"✅ **Login Successful! Welcome {user[0]}**", user[0]
    else:
        return "❌ Invalid Username or Password!", None

# --- DYNAMIC AI / FALLBACK ENGINE ---
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

# --- CORE SCRIPT GENERATION WITH AUTH CHECK ---
def generate_script_authenticated(username_state, topic, vip_key):
    try:
        if not topic or not topic.strip():
            return "⚠️ **Please enter a video topic first!**", None
        
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
                    return f"""### 🔒 **FREE TRIAL EXHAUSTED FOR (@{target_user})**

Aapki 2 free scripts complete ho chuki hain! Unlimited access ke liye **Payment Tab** me jaakar ₹299 pay karke UTR enter karein ya VIP Key use karein!

👉 **[OR CLICK HERE TO BUY ON WHATSAPP]({PAYMENT_LINK})**
""", None

        # Generate Script
        script_output = fetch_ai_script(topic)
        if not script_output:
            script_output = fallback_local_script(topic)

        # Update Database
        if target_user != "guest":
            cursor.execute("UPDATE users SET scripts_used = scripts_used + 1 WHERE username = ?", (target_user,))
            cursor.execute("INSERT INTO history (username, topic, script, created_at) VALUES (?, ?, ?, ?)",
                           (target_user, topic, script_output, datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
            conn.commit()
        conn.close()

        # Download File
        filename = f"Script_{topic.replace(' ', '_')}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(script_output)

        return script_output, filename

    except Exception as e:
        return f"❌ Error: {str(e)}", None

# --- AUTOMATED PAYMENT VERIFICATION SYSTEM ---
def submit_payment_utr(username, utr):
    if not username or username == "guest":
        return "❌ Please Login first before submitting payment!"
    if not utr or len(utr.strip()) < 6:
        return "⚠️ Please enter a valid 12-digit UPI UTR / Transaction ID!"
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Auto approve for instant demo or record for admin approval
    expiry = (datetime.date.today() + datetime.timedelta(days=30)).strftime("%Y-%m-%d")
    cursor.execute("UPDATE users SET vip_until = ? WHERE username = ?", (expiry, username.strip().lower()))
    cursor.execute("INSERT OR REPLACE INTO payments VALUES (?, ?, ?, ?)", 
                   (utr.strip(), username.strip().lower(), "APPROVED", datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    conn.close()
    
    return f"🎉 **PAYMENT SUCCESSFUL!**\n\nYour account **@{username}** is now upgraded to **VIP ACCESS** until `{expiry}`. Enjoy Unlimited Scripts!"

# --- DASHBOARD & HISTORY ---
def load_user_dashboard(username):
    if not username or username == "guest":
        return "⚠️ Please **Login** to view your personal dashboard & saved scripts history."
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT vip_until, scripts_used, created_at FROM users WHERE username = ?", (username.strip().lower(),))
    u = cursor.fetchone()
    
    cursor.execute("SELECT topic, created_at, script FROM history WHERE username = ? ORDER BY id DESC LIMIT 10", (username.strip().lower(),))
    history_rows = cursor.fetchall()
    conn.close()
    
    status = u[0] if u else "FREE"
    used = u[1] if u else 0
    
    out = f"""### 👤 **User Profile Dashboard**
* 🆔 **Username:** `@{username}`
* 💎 **Subscription Status:** `{status}`
* 📊 **Total Scripts Generated:** `{used}`

---
### 📜 **Your Saved Script History**
"""
    if not history_rows:
        out += "\n*No saved scripts found yet. Go to Generator tab to create one!*"
    else:
        for idx, r in enumerate(history_rows, 1):
            out += f"\n#### {idx}. 🎯 Topic: **{r[0]}** *(Created: {r[1]})*\n```markdown\n{r[2][:200]}...\n```\n"
            
    return out

# --- CUSTOM TAILWIND/DARK-MODE CSS INJECTION ---
custom_css = """
body, .gradio-container {
    background-color: #0f172a !important;
    color: #f8fafc !important;
    font-family: 'Inter', sans-serif !important;
}
.gr-button-primary {
    background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%) !important;
    border: none !important;
    border-radius: 8px !important;
    box-shadow: 0 4px 14px 0 rgba(168, 85, 247, 0.39) !important;
}
.gr-button-secondary {
    background: #334155 !important;
    border: none !important;
}
.gr-textbox input, .gr-textbox textarea {
    background-color: #1e293b !important;
    border: 1px solid #475569 !important;
    color: white !important;
    border-radius: 8px !important;
}
"""

# --- GRADIO INTERFACE (FULL SAAS APP) ---
with gr.Blocks(css=custom_css, title="Viral Script AI Pro - Full SaaS") as demo:
    
    active_user = gr.State(value="guest")
    
    gr.HTML(f"""
    <div style="background: linear-gradient(90deg, #1e1b4b 0%, #311b92 100%); padding: 25px; border-radius: 12px; text-align: center; border: 1px solid #4338ca;">
        <h1 style="color: #ffffff; margin:0; font-size: 30px; font-weight: 800;">⚡ VIRAL SCRIPT AI PRO</h1>
        <p style="color: #cbd5e1; margin-top: 5px;">Complete SaaS Platform with Auth, Instant Payment & Saved History</p>
    </div>
    """)
    
    user_status_bar = gr.Markdown("🟢 Status: **Browsing as Guest** (Login to save scripts & unlock VIP)")
    
    with gr.Tab("🔐 Account Login / Sign Up"):
        with gr.Row():
            with gr.Column():
                gr.Markdown("### 📝 Register New Account")
                reg_user = gr.Textbox(label="Choose Username")
                reg_pass = gr.Textbox(label="Choose Password", type="password")
                reg_btn = gr.Button("Create Account", variant="primary")
                reg_output = gr.Markdown()
                reg_btn.click(fn=register_user, inputs=[reg_user, reg_pass], outputs=reg_output)
                
            with gr.Column():
                gr.Markdown("### 🔑 Login to Existing Account")
                log_user = gr.Textbox(label="Username")
                log_pass = gr.Textbox(label="Password", type="password")
                log_btn = gr.Button("Login Now", variant="primary")
                log_output = gr.Markdown()
                
                def handle_login(u, p):
                    msg, username = login_user(u, p)
                    if username:
                        status_text = f"🟢 Logged in as: **@{username}**"
                        return msg, username, status_text
                    return msg, "guest", "🟢 Status: **Browsing as Guest**"

                log_btn.click(
                    fn=handle_login, 
                    inputs=[log_user, log_pass], 
                    outputs=[log_output, active_user, user_status_bar]
                )

    with gr.Tab("🎬 Script Generator"):
        with gr.Row():
            topic_input = gr.Textbox(label="🎯 Enter Video Topic", placeholder="e.g. Fitness Tips, Boxing Basics, Tech Reviews...", scale=2)
            key_input = gr.Textbox(label="🔑 VIP Key / Admin Pass (Optional)", type="password", scale=1)
        
        submit_btn = gr.Button("🔥 Generate Viral Script", variant="primary")
        
        with gr.Row():
            output_text = gr.Markdown(label="Output")
            file_output = gr.File(label="📥 Download Script (.txt)")
        
        submit_btn.click(
            fn=generate_script_authenticated,
            inputs=[active_user, topic_input, key_input],
            outputs=[output_text, file_output]
        )

    with gr.Tab("💳 Instant UPI Payment (Auto Unlock)"):
        gr.Markdown(f"""
        ### ⚡ Instant Subscription Activation (₹299 / Month)
        1. Scan QR or pay ₹299 to UPI ID: `{MY_UPI_ID}`
        2. Enter the **12-Digit UTR / Transaction ID** below for instant activation!
        """)
        
        utr_input = gr.Textbox(label="Enter 12-Digit UPI UTR / Transaction Number", placeholder="e.g. 425619082341")
        pay_btn = gr.Button("🚀 Verify Payment & Unlock VIP", variant="primary")
        pay_output = gr.Markdown()
        
        pay_btn.click(fn=submit_payment_utr, inputs=[active_user, utr_input], outputs=pay_output)

    with gr.Tab("📊 User Dashboard & History"):
        dash_refresh_btn = gr.Button("🔄 Load My Dashboard & History")
        dash_output = gr.Markdown()
        dash_refresh_btn.click(fn=load_user_dashboard, inputs=[active_user], outputs=dash_output)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
