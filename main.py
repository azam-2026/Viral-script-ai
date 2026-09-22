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
ADMIN_SECRET_KEY = "AZAM2026"         # Tera Admin Pass
KEY_SALT = "AZAM_SECRET_SALT_999"    # Key Protection
DB_FILE = "app_database.db"          # SQLite Database File

PAYMENT_LINK = f"https://wa.me/{MY_WHATSAPP_NUMBER}?text=Bro%20mujhe%20Viral%20Script%20AI%20ka%20subscription%20chahiye"

user_usage = {}

# --- 1. SQLITE DATABASE SETUP (Persistent Storage) ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS keys (
            key_text TEXT PRIMARY KEY,
            expiry_date TEXT,
            created_at TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT,
            script TEXT,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- DYNAMIC FALLBACK POOLS ---
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
    key_text = f"VIP-{date_str}-{sig}"
    
    # Save key to database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO keys VALUES (?, ?, ?)", 
                   (key_text, expiry_date.strftime("%Y-%m-%d"), datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
    conn.commit()
    conn.close()
    
    return key_text

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

def save_script_to_db(topic, script):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO history (topic, script, created_at) VALUES (?, ?, ?)",
                       (topic, script, datetime.datetime.now().strftime("%Y-%m-%d %H:%M")))
        conn.commit()
        conn.close()
    except Exception:
        pass

def generate_script_and_file(topic, license_key, request: gr.Request):
    try:
        if not topic or not topic.strip():
            return "⚠️ **Please enter a video topic first!**", None
        
        clean_key = license_key.strip() if license_key else ""
        
        is_admin = (clean_key == ADMIN_SECRET_KEY)
        is_paid_client, key_msg = verify_client_key(clean_key) if clean_key else (False, "")

        if not is_admin and not is_paid_client:
            client_ip = request.client.host if request else "default_user"
            current_count = user_usage.get(client_ip, 0)
            
            if current_count >= 2:
                status_note = f"\n\n*(Reason: {key_msg})*" if (clean_key and not is_paid_client) else ""
                pay_msg = f"""### 🔒 **FREE TRIAL EXHAUSTED!**{status_note}

Aapki 2 free scripts complete ho chuki hain. Unlimited AI Script generation ke liye subscription lein:

👉 **[CLICK HERE TO PAY & UNLOCK UNLIMITED VIP ACCESS (₹299/MONTH)]({PAYMENT_LINK})**

*(Upar Blue Link par click karke WhatsApp par DM karein. Payment ke baad instant 1-Month Access Key mil jayega!)*
"""
                return pay_msg, None
            user_usage[client_ip] = current_count + 1

        # Fetch AI Script or Fallback
        script_output = fetch_ai_script(topic)
        if not script_output:
            script_output = fallback_local_script(topic)

        # Save to SQLite Database
        save_script_to_db(topic, script_output)

        # Create Downloadable TXT File
        clean_topic_name = "".join(c for c in topic if c.isalnum() or c in (' ', '_')).rstrip()
        filename = f"Script_{clean_topic_name.replace(' ', '_')}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(script_output)

        return script_output, filename
        
    except Exception as e:
        return f"❌ Error: {str(e)}", None

# --- HISTORY FETCH LOGIC ---
def get_recent_history():
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT topic, created_at, script FROM history ORDER BY id DESC LIMIT 5")
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return "### 📭 **No Script History Found Yet.**"
        
        output = "### 🕒 **Recently Generated Scripts (SQLite Database)**\n\n"
        for idx, row in enumerate(rows, 1):
            output += f"#### {idx}. 🎯 Topic: **{row[0]}** *(Generated at: {row[1]})*\n"
            output += f"```markdown\n{row[2][:250]}...\n```\n---\n"
        return output
    except Exception as e:
        return f"Error loading history: {str(e)}"

# --- ADMIN ANALYTICS LOGIC ---
def admin_generate_key_and_stats(admin_pass):
    if admin_pass.strip() != ADMIN_SECRET_KEY:
        return "❌ Incorrect Admin Pass!", "### ⚠️ Access Denied"
    
    new_key = generate_client_key(days=30)
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM history")
    total_scripts = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM keys")
    total_keys = cursor.fetchone()[0]
    conn.close()
    
    est_revenue = total_keys * 299
    
    key_msg = f"✅ **New 30-Day VIP Key Generated:**\n\n`{new_key}`\n\n*(Send this key to your paid customer!)*"
    
    stats_md = f"""### 📊 **Live Owner Analytics Dashboard**
* 🚀 **Total Scripts Generated:** `{total_scripts}`
* 🔑 **Total Paid VIP Keys Created:** `{total_keys}`
* 💰 **Estimated Revenue Earned:** `₹{est_revenue}`
* 💾 **Database Status:** `SQLite Connected (Active)`
"""
    return key_msg, stats_md

# --- GRADIO INTERFACE (FULL SAAS LOOK) ---
with gr.Blocks(title="Viral AI Script Generator Pro SaaS v3.0") as demo:
    
    # Custom CSS / Floating Support Widget
    gr.HTML(f"""
    <div style="background: linear-gradient(90deg, #1E1E2F 0%, #2D2B55 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 15px;">
        <h1 style="margin: 0; font-size: 28px;">⚡ Viral AI Script Generator Pro</h1>
        <p style="margin: 5px 0 0 0; opacity: 0.9;">Create Viral Short Video Scripts, Hooks & CTAs in 5 Seconds</p>
    </div>
    """)
    
    with gr.Tab("🏠 Home & Pricing"):
        gr.Markdown("""
        ### 🚀 **Welcome to Viral AI Script Generator Pro**
        *The #1 AI Tool for Reels, Shorts & TikTok Creators.*
        
        ---
        
        #### ✨ **Why Choose Us?**
        * 🎯 **10x Retention Hooks:** Never lose viewers in the first 3 seconds.
        * ⚡ **Full Hinglish Support:** Optimized for Indian social media audience.
        * 📥 **Instant 1-Click Download:** Get your script ready in .txt format.
        * 🛡️ **30-Day VIP Pass:** Unlimited generations without limit.
        
        ---
        
        #### 💳 **Subscription Plans**
        | Plan | Price | Scripts Limit | Access |
        | :--- | :--- | :--- | :--- |
        | **Free Trial** | ₹0 | 2 Scripts Total | Instant Access |
        | **VIP Monthly Pass** | **₹299 / Month** | **UNLIMITED** | **30 Days Access + Support** |
        
        👉 **[Click Here to Purchase VIP Pass via WhatsApp](https://wa.me/917980890889?text=Bro%20mujhe%20Viral%20Script%20AI%20ka%20subscription%20chahiye)**
        
        ---
        
        #### ❓ **Frequently Asked Questions (FAQ)**
        * **Q: VIP Key kitne time tak chalega?**
          * *Ans:* Pure 30 din tak valid rahega.
        * **Q: Kya main har topic par script bana sakta hu?**
          * *Ans:* Haan! Fitness, Gaming, Tech, Boxing, MMA, Finance sab par kaam karta hai.
        """)
        
    with gr.Tab("🎬 Script Generator"):
        with gr.Row():
            topic_input = gr.Textbox(
                label="🎯 Enter Video Topic", 
                placeholder="e.g. Fitness Tips, Boxing Basics, YouTube Growth...",
                scale=2
            )
            key_input = gr.Textbox(
                label="🔑 VIP Key / Pass (Optional)", 
                placeholder="Enter VIP Key for Unlimited Access...", 
                type="password",
                scale=1
            )
        
        submit_btn = gr.Button("🔥 Generate Viral Script Now", variant="primary")
        
        with gr.Row():
            output_text = gr.Markdown(label="Generated Script Output")
            file_output = gr.File(label="📥 Download Script (.txt)")
        
        submit_btn.click(
            fn=generate_script_and_file,
            inputs=[topic_input, key_input],
            outputs=[output_text, file_output]
        )

    with gr.Tab("🕒 Recent History"):
        history_btn = gr.Button("🔄 Refresh Database History")
        history_output = gr.Markdown()
        history_btn.click(fn=get_recent_history, outputs=history_output)

    with gr.Tab("🔑 Admin & Analytics Panel"):
        gr.Markdown("### 🛠️ Owner Admin Control Center")
        admin_pass_input = gr.Textbox(label="Enter Admin Pass", type="password", placeholder="AZAM2026")
        gen_btn = gr.Button("Generate 1-Month Key & View Live Analytics", variant="secondary")
        
        key_output = gr.Markdown()
        stats_output = gr.Markdown()
        
        gen_btn.click(
            fn=admin_generate_key_and_stats,
            inputs=[admin_pass_input],
            outputs=[key_output, stats_output]
        )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(server_name="0.0.0.0", server_port=port)
