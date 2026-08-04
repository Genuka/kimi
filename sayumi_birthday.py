import streamlit as st
import base64
import os
import random
from datetime import datetime, timedelta
import time

# ═══════════════════════════════════════════════════════════════════════════════
# SAYUMI'S BIRTHDAY SURPRISE — Streamlit App
# Solves the iframe click issue by using native Streamlit components
# for ALL interactions. HTML is only used for non-interactive visuals.
# ═══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Happy Birthday Sayumi! 🎂",
    page_icon="🎀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── SESSION STATE INITIALIZATION ─────────────────────────────────────────────
def init_state():
    defaults = {
        'page': 0,
        'code': '',
        'code_error': False,
        'roast_idx': 0,
        'photo_idx': 0,
        'q_idx': 0,
        'no_escapes': 0,
        'show_confetti': False,
        'show_hearts': False,
        'countdown_target': datetime(2026, 8, 6, 0, 0, 0),
        'dev_mode': False,
        'yes_clicked': False,
        'yes_msg': '',
        'confetti_key': 0,
        'hearts_key': 0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ─── HELPERS ──────────────────────────────────────────────────────────────────
def get_base64_file(filename):
    """Read a file and return base64 string."""
    filepath = os.path.join(os.path.dirname(__file__), filename)
    if os.path.exists(filepath):
        with open(filepath, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

def get_photo_base64(idx):
    return get_base64_file(f"photo{idx}.jpg")

def trigger_confetti():
    st.session_state.show_confetti = True
    st.session_state.confetti_key += 1

def trigger_hearts():
    st.session_state.show_hearts = True
    st.session_state.hearts_key += 1

# ─── GLOBAL CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Hide Streamlit UI */
    #MainMenu {visibility: hidden !important;}
    footer {visibility: hidden !important;}
    header {visibility: hidden !important;}
    .stDeployButton {display: none !important;}
    .stToolbar {display: none !important;}
    [data-testid="stSidebar"] {display: none !important;}
    [data-testid="stBottomBlockContainer"] {display: none !important;}

    /* Remove default padding */
    .block-container {
        padding: 0.5rem 1rem 0 !important;
        max-width: 100% !important;
    }
    .main > div {
        padding: 0 !important;
    }

    /* Base background */
    .stApp {
        background: linear-gradient(135deg, #fce7f3 0%, #e9d5ff 40%, #ffffff 100%) !important;
        min-height: 100vh;
    }

    /* Smooth page entrance */
    .page-container {
        animation: pageEnter 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }
    @keyframes pageEnter {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Shake animation for wrong code */
    .shake {
        animation: shake 0.5s cubic-bezier(.36,.07,.19,.97) both;
    }
    @keyframes shake {
        10%, 90% { transform: translate3d(-2px, 0, 0); }
        20%, 80% { transform: translate3d(4px, 0, 0); }
        30%, 50%, 70% { transform: translate3d(-6px, 0, 0); }
        40%, 60% { transform: translate3d(6px, 0, 0); }
    }

    /* Gradient text */
    .gradient-text {
        background: linear-gradient(90deg, #ec4899, #8b5cf6, #3b82f6, #ec4899);
        background-size: 300% 100%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: gradientShift 4s ease infinite;
        font-weight: 800;
    }
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Card styles */
    .card {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 8px 32px rgba(168, 85, 247, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.5);
    }

    /* Floating hearts background (CSS only, injected into main DOM) */
    .heart-bg {
        position: fixed;
        font-size: 22px;
        pointer-events: none;
        z-index: 0;
        opacity: 0.5;
        animation: floatUp linear infinite;
    }
    @keyframes floatUp {
        0% { transform: translateY(100vh) rotate(0deg); opacity: 0; }
        15% { opacity: 0.5; }
        85% { opacity: 0.5; }
        100% { transform: translateY(-10vh) rotate(360deg); opacity: 0; }
    }

    /* Confetti particles */
    .confetti-piece {
        position: fixed;
        width: 10px;
        height: 10px;
        pointer-events: none;
        z-index: 9999;
        animation: confettiFall 4s ease-out forwards;
        top: -10px;
    }
    @keyframes confettiFall {
        0% { transform: translateY(0) rotate(0deg) translateX(0); opacity: 1; }
        25% { transform: translateY(25vh) rotate(180deg) translateX(20px); }
        50% { transform: translateY(50vh) rotate(360deg) translateX(-20px); }
        75% { transform: translateY(75vh) rotate(540deg) translateX(10px); opacity: 0.8; }
        100% { transform: translateY(105vh) rotate(720deg) translateX(0); opacity: 0; }
    }

    /* Heart shower emojis */
    .heart-shower {
        position: fixed;
        font-size: 28px;
        pointer-events: none;
        z-index: 9998;
        animation: heartShower 3s ease-out forwards;
        top: -10px;
    }
    @keyframes heartShower {
        0% { transform: translateY(0) scale(0.5); opacity: 0; }
        20% { opacity: 1; transform: translateY(20vh) scale(1.2); }
        100% { transform: translateY(105vh) scale(1); opacity: 0; }
    }

    /* Fade scale for photos */
    .photo-anim {
        animation: photoFade 0.5s ease;
    }
    @keyframes photoFade {
        from { opacity: 0; transform: scale(0.9); }
        to { opacity: 1; transform: scale(1); }
    }

    /* Roast card fade */
    .roast-anim {
        animation: roastFade 0.4s ease;
    }
    @keyframes roastFade {
        from { opacity: 0; transform: translateX(-10px); }
        to { opacity: 1; transform: translateX(0); }
    }

    /* Music bars */
    .music-bar {
        display: inline-block;
        width: 10px;
        background: linear-gradient(to top, #ec4899, #8b5cf6);
        border-radius: 5px;
        margin: 0 3px;
        animation: barBounce 1.2s ease-in-out infinite;
    }
    @keyframes barBounce {
        0%, 100% { height: 20px; }
        50% { height: 60px; }
    }

    /* Custom button overrides */
    .stButton > button {
        border-radius: 16px !important;
        border: none !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(168, 85, 247, 0.3);
    }
    .stButton > button:active {
        transform: translateY(0);
    }

    /* Keypad buttons */
    .keypad-btn > button {
        background: rgba(255,255,255,0.2) !important;
        color: #e9d5ff !important;
        font-size: 28px !important;
        height: 72px !important;
        border: 1px solid rgba(233, 213, 255, 0.3) !important;
    }
    .keypad-btn > button:hover {
        background: rgba(255,255,255,0.35) !important;
    }

    /* Pink action buttons */
    .pink-btn > button {
        background: linear-gradient(135deg, #ec4899, #a855f7) !important;
        color: white !important;
        padding: 14px 28px !important;
        font-size: 16px !important;
    }

    /* Secondary buttons */
    .secondary-btn > button {
        background: rgba(255,255,255,0.6) !important;
        color: #7c3aed !important;
        border: 1px solid rgba(168, 85, 247, 0.2) !important;
    }

    /* Scrollable message card */
    .scroll-card {
        max-height: 60vh;
        overflow-y: auto;
        padding-right: 10px;
    }
    .scroll-card::-webkit-scrollbar {
        width: 6px;
    }
    .scroll-card::-webkit-scrollbar-thumb {
        background: rgba(168, 85, 247, 0.3);
        border-radius: 3px;
    }

    /* Countdown card */
    .countdown-card {
        background: white;
        border-radius: 16px;
        padding: 16px 8px;
        text-align: center;
        box-shadow: 0 4px 16px rgba(0,0,0,0.05);
        min-width: 70px;
    }

    /* Dev button */
    .dev-btn > button {
        background: transparent !important;
        color: rgba(168, 85, 247, 0.3) !important;
        font-size: 10px !important;
        border: none !important;
        padding: 4px !important;
    }

    /* Nav dot buttons */
    .nav-dot > button {
        background: transparent !important;
        border: none !important;
        padding: 2px !important;
        min-height: 0 !important;
        height: auto !important;
        font-size: 12px !important;
        color: #c4b5fd !important;
        opacity: 0.6;
    }
    .nav-dot > button:hover {
        opacity: 1;
        transform: scale(1.3);
        color: #a855f7 !important;
    }
    .nav-dot-active > button {
        color: #ec4899 !important;
        opacity: 1 !important;
        transform: scale(1.2);
    }
</style>
""", unsafe_allow_html=True)

# ─── FLOATING HEARTS BACKGROUND (always visible, CSS-only) ───────────────────
hearts = ['💗', '🌸', '✨', '💜', '🩷', '🌺', '💖', '💫']
heart_html = ""
for i in range(18):
    left = random.randint(2, 95)
    delay = random.uniform(0, 12)
    duration = random.uniform(10, 18)
    heart = random.choice(hearts)
    size = random.uniform(16, 28)
    heart_html += f'<div class="heart-bg" style="left:{left}%; animation-delay:{delay}s; animation-duration:{duration}s; font-size:{size}px;">{heart}</div>'

st.markdown(heart_html, unsafe_allow_html=True)

# ─── CONFETTI EFFECT (triggered by buttons) ───────────────────────────────────
if st.session_state.show_confetti:
    colors = ['#ec4899', '#a855f7', '#3b82f6', '#fbbf24', '#f472b6', '#8b5cf6']
    shapes = ['■', '●', '▲', '★']
    confetti_html = ""
    for i in range(60):
        left = random.randint(0, 100)
        delay = random.uniform(0, 1.5)
        color = random.choice(colors)
        shape = random.choice(shapes)
        rot = random.randint(0, 360)
        confetti_html += f'<div class="confetti-piece" style="left:{left}%; animation-delay:{delay}s; background:{color}; transform:rotate({rot}deg);">{shape}</div>'
    st.markdown(confetti_html, unsafe_allow_html=True)
    st.session_state.show_confetti = False

# ─── HEART SHOWER EFFECT ──────────────────────────────────────────────────────
if st.session_state.show_hearts:
    shower_emojis = ['💗', '💖', '💜', '🩷', '💕', '💓', '💘', '💝']
    shower_html = ""
    for i in range(40):
        left = random.randint(5, 95)
        delay = random.uniform(0, 2)
        emoji = random.choice(shower_emojis)
        shower_html += f'<div class="heart-shower" style="left:{left}%; animation-delay:{delay}s;">{emoji}</div>'
    st.markdown(shower_html, unsafe_allow_html=True)
    st.session_state.show_hearts = False

# ─── MAIN LAYOUT: Content + Right Nav ─────────────────────────────────────────
content_col, nav_col = st.columns([5, 1])

# ─── RIGHT SIDE NAV DOTS (native buttons) ─────────────────────────────────────
with nav_col:
    st.markdown("<div style='height: 20vh;'></div>", unsafe_allow_html=True)
    for i in range(11):
        is_active = i == st.session_state.page
        dot_class = "nav-dot-active" if is_active else "nav-dot"
        dot_label = "●" if is_active else "○"
        st.markdown(f"<div class='{dot_class}'>", unsafe_allow_html=True)
        if st.button(dot_label, key=f"navdot_{i}"):
            st.session_state.page = i
            st.session_state.show_confetti = False
            st.session_state.show_hearts = False
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# ─── MAIN CONTENT AREA ────────────────────────────────────────────────────────
with content_col:

    # ═══════════════════════════════════════════════════════════════════════════
    # PAGE 0 — TAP TO OPEN
    # ═══════════════════════════════════════════════════════════════════════════
    if st.session_state.page == 0:
        st.markdown("""
        <style>
            .stApp { background: #2e1065 !important; }
        </style>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height: 22vh;'></div>", unsafe_allow_html=True)

        c1, c2, c3 = st.columns([1, 3, 1])
        with c2:
            st.markdown("""
            <div style="text-align: center; animation: pageEnter 0.8s ease;">
                <div style="font-size: 5rem; margin-bottom: 20px; animation: pulseGlow 2s infinite;">🎀</div>
                <h2 style="color: #e9d5ff; font-weight: 400; margin-bottom: 8px;">tap anywhere to open</h2>
                <p style="color: #a855f7; font-size: 0.9rem;">something special is waiting</p>
            </div>
            <style>
                @keyframes pulseGlow {
                    0%, 100% { transform: scale(1); opacity: 1; filter: drop-shadow(0 0 10px rgba(168,85,247,0.5)); }
                    50% { transform: scale(1.15); opacity: 0.85; filter: drop-shadow(0 0 25px rgba(168,85,247,0.8)); }
                }
            </style>
            """, unsafe_allow_html=True)

            # Large glowing tap button
            st.markdown("""
            <style>
            .tap-btn > button {
                background: transparent !important;
                border: 2px solid rgba(168, 85, 247, 0.4) !important;
                color: #e9d5ff !important;
                font-size: 2.5rem !important;
                height: 160px !important;
                border-radius: 50% !important;
                width: 160px !important;
                margin: 30px auto !important;
                display: block !important;
                box-shadow: 0 0 40px rgba(168, 85, 247, 0.3) !important;
                transition: all 0.3s ease !important;
            }
            .tap-btn > button:hover {
                box-shadow: 0 0 60px rgba(168, 85, 247, 0.6) !important;
                transform: scale(1.05) !important;
                background: rgba(168, 85, 247, 0.1) !important;
            }
            </style>
            """, unsafe_allow_html=True)

            if st.button("✨", key="tap_open"):
                st.session_state.page = 1
                st.rerun()

    # ═══════════════════════════════════════════════════════════════════════════
    # PAGE 1 — KEYPAD LOCK
    # ═══════════════════════════════════════════════════════════════════════════
    elif st.session_state.page == 1:
        st.markdown("""
        <style>
            .stApp { background: #2e1065 !important; }
        </style>
        """, unsafe_allow_html=True)

        st.markdown("<div style='height: 6vh;'></div>", unsafe_allow_html=True)

        c1, c2, c3 = st.columns([1, 3, 1])
        with c2:
            st.markdown("""
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: #e9d5ff; font-weight: 500; margin-bottom: 8px;">hey sayumi 🎀</h1>
                <p style="color: #a855f7; text-transform: lowercase; font-size: 0.95rem; letter-spacing: 1px;">enter the secret code</p>
            </div>
            """, unsafe_allow_html=True)

            # Dots display
            dots = ""
            shake_class = "shake" if st.session_state.code_error else ""
            for i in range(8):
                if i < len(st.session_state.code):
                    dots += "<span style='color: #ec4899; font-size: 36px; margin: 0 6px;'>●</span>"
                else:
                    dots += "<span style='color: rgba(233, 213, 255, 0.3); font-size: 36px; margin: 0 6px;'>○</span>"

            st.markdown(f"""
            <div style="text-align: center; margin-bottom: 40px;" class="{shake_class}">
                {dots}
            </div>
            """, unsafe_allow_html=True)

            # Reset shake flag
            if st.session_state.code_error:
                st.session_state.code_error = False

            # KEYPAD — native Streamlit buttons, NO iframes
            keys = [
                ['1', '2', '3'],
                ['4', '5', '6'],
                ['7', '8', '9'],
                ['', '0', '⌫']
            ]

            for row in keys:
                cols = st.columns(3)
                for i, key in enumerate(row):
                    with cols[i]:
                        if key == '':
                            st.empty()
                        else:
                            btn_label = "←" if key == '⌫' else key
                            st.markdown("<div class='keypad-btn'>", unsafe_allow_html=True)
                            if st.button(btn_label, key=f"kp_{key}_{row[0]}", use_container_width=True):
                                if key == '⌫':
                                    st.session_state.code = st.session_state.code[:-1]
                                else:
                                    if len(st.session_state.code) < 8:
                                        st.session_state.code += key

                                # Check code when 8 digits entered
                                if len(st.session_state.code) == 8:
                                    if st.session_state.code == "06082012":
                                        trigger_confetti()
                                        st.session_state.code = ""
                                        st.session_state.page = 2
                                    else:
                                        st.session_state.code = ""
                                        st.session_state.code_error = True
                                st.rerun()
                            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("""
            <div style="text-align: center; margin-top: 30px;">
                <p style="color: rgba(168, 85, 247, 0.6); font-size: 0.8rem;">hint: her bday 😉</p>
            </div>
            """, unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════════════════
    # PAGE 2 — HERO
    # ═══════════════════════════════════════════════════════════════════════════
    elif st.session_state.page == 2:
        st.markdown("<div style='height: 10vh;'></div>", unsafe_allow_html=True)

        c1, c2, c3 = st.columns([1, 4, 1])
        with c2:
            st.markdown("""
            <div class="page-container" style="text-align: center;">
                <p style="color: #a855f7; font-size: 0.9rem; letter-spacing: 2px; text-transform: lowercase; margin-bottom: 16px;">
                    a little something for you
                </p>
                <h1 class="gradient-text" style="font-size: 4.5rem; margin-bottom: 12px; line-height: 1.1;">
                    Sayumi
                </h1>
                <p style="color: #7c3aed; font-size: 1.1rem; margin-bottom: 30px;">
                    turning 14 · august 6th ✨
                </p>
                <div style="font-size: 2.2rem; letter-spacing: 8px; margin-bottom: 40px; animation: pageEnter 1s ease 0.3s both;">
                    🎂💗🎉🫶🥹
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<div class='pink-btn'>", unsafe_allow_html=True)
            if st.button("open 💗", use_container_width=True):
                st.session_state.page = 3
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════════════════
    # PAGE 3 — COUNTDOWN
    # ═══════════════════════════════════════════════════════════════════════════
    elif st.session_state.page == 3:
        st.markdown("<div style='height: 5vh;'></div>", unsafe_allow_html=True)

        c1, c2, c3 = st.columns([1, 4, 1])
        with c2:
            target = st.session_state.countdown_target
            now = datetime.now()
            is_birthday = now.date() == target.date()

            if is_birthday:
                st.markdown("""
                <div class="page-container" style="text-align: center; margin-bottom: 30px;">
                    <div style="background: linear-gradient(135deg, #ec4899, #a855f7); 
                                color: white; padding: 24px; border-radius: 20px; 
                                font-size: 1.8rem; font-weight: 700; box-shadow: 0 8px 32px rgba(236, 72, 153, 0.3);">
                        IT'S YOUR DAY!! 🎂
                    </div>
                </div>
                """, unsafe_allow_html=True)
                trigger_confetti()
            else:
                # Live countdown using JS in iframe (non-interactive display only)
                target_str = target.strftime("%Y-%m-%dT%H:%M:%S")
                st.markdown("<div class='page-container'>", unsafe_allow_html=True)

                countdown_iframe = f"""
                <div style="display: flex; gap: 12px; justify-content: center; margin-bottom: 30px;">
                    <div class="countdown-card">
                        <div id="cd-days" style="font-size: 2.2rem; font-weight: 700; color: #7c3aed;">00</div>
                        <div style="font-size: 0.7rem; color: #a855f7; text-transform: uppercase; letter-spacing: 1px;">Days</div>
                    </div>
                    <div class="countdown-card">
                        <div id="cd-hours" style="font-size: 2.2rem; font-weight: 700; color: #7c3aed;">00</div>
                        <div style="font-size: 0.7rem; color: #a855f7; text-transform: uppercase; letter-spacing: 1px;">Hours</div>
                    </div>
                    <div class="countdown-card">
                        <div id="cd-minutes" style="font-size: 2.2rem; font-weight: 700; color: #7c3aed;">00</div>
                        <div style="font-size: 0.7rem; color: #a855f7; text-transform: uppercase; letter-spacing: 1px;">Minutes</div>
                    </div>
                    <div class="countdown-card">
                        <div id="cd-seconds" style="font-size: 2.2rem; font-weight: 700; color: #7c3aed;">00</div>
                        <div style="font-size: 0.7rem; color: #a855f7; text-transform: uppercase; letter-spacing: 1px;">Seconds</div>
                    </div>
                </div>
                <script>
                    (function() {{
                        const target = new Date("{target_str}").getTime();
                        function update() {{
                            const now = new Date().getTime();
                            const diff = target - now;
                            if (diff <= 0) {{
                                document.getElementById("cd-days").innerText = "00";
                                document.getElementById("cd-hours").innerText = "00";
                                document.getElementById("cd-minutes").innerText = "00";
                                document.getElementById("cd-seconds").innerText = "00";
                                return;
                            }}
                            const d = Math.floor(diff / (1000*60*60*24));
                            const h = Math.floor((diff % (1000*60*60*24)) / (1000*60*60));
                            const m = Math.floor((diff % (1000*60*60)) / (1000*60));
                            const s = Math.floor((diff % (1000*60)) / 1000);
                            document.getElementById("cd-days").innerText = String(d).padStart(2,'0');
                            document.getElementById("cd-hours").innerText = String(h).padStart(2,'0');
                            document.getElementById("cd-minutes").innerText = String(m).padStart(2,'0');
                            document.getElementById("cd-seconds").innerText = String(s).padStart(2,'0');
                        }}
                        update();
                        setInterval(update, 1000);
                    }})();
                </script>
                """
                st.components.v1.html(countdown_iframe, height=140)
                st.markdown("</div>", unsafe_allow_html=True)

            # Buttons
            btn_cols = st.columns(2)
            with btn_cols[0]:
                st.markdown("<div class='pink-btn'>", unsafe_allow_html=True)
                if st.button("🎉 confetti", use_container_width=True):
                    trigger_confetti()
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
            with btn_cols[1]:
                st.markdown("<div class='secondary-btn'>", unsafe_allow_html=True)
                if st.button("💗 heart shower", use_container_width=True):
                    trigger_hearts()
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

            # Dev button
            st.markdown("<div style='text-align: center; margin-top: 20px;'>", unsafe_allow_html=True)
            st.markdown("<div class='dev-btn'>", unsafe_allow_html=True)
            if st.button("dev: reset to 10s", key="dev_countdown"):
                st.session_state.countdown_target = datetime.now() + timedelta(seconds=10)
                st.session_state.dev_mode = True
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════════════════
    # PAGE 4 — ROASTS
    # ═══════════════════════════════════════════════════════════════════════════
    elif st.session_state.page == 4:
        st.markdown("<div style='height: 6vh;'></div>", unsafe_allow_html=True)

        c1, c2, c3 = st.columns([1, 4, 1])
        with c2:
            roasts = [
                "😭 threatens to slap me literally every other day and has never said sorry once",
                "📝 wrote 4 whole pages for no reason at all and thinks thats totally normal",
                "💀 crashes out every single time geenuka gets mentioned. every. single. time.",
                "🖤 wears black like its her whole thing and honestly? fair. it works.",
                "🧠 was the quietest nerd in cambridge 6 and now wont stop talking or threatening me"
            ]

            idx = st.session_state.roast_idx

            st.markdown("""
            <div class="page-container" style="text-align: center; margin-bottom: 24px;">
                <p style="color: #a855f7; font-size: 0.9rem; text-transform: lowercase; letter-spacing: 1px;">
                    reasons ur actually the worst 😭
                </p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="card roast-anim" style="text-align: center; margin-bottom: 30px; min-height: 120px; display: flex; align-items: center; justify-content: center;">
                <p style="font-size: 1.15rem; color: #4c1d95; line-height: 1.5; margin: 0;">
                    {roasts[idx]}
                </p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<div class='pink-btn'>", unsafe_allow_html=True)
            if st.button("next roast 😂", use_container_width=True):
                st.session_state.roast_idx = (idx + 1) % len(roasts)
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

            # Dots indicator
            dots = ""
            for i in range(len(roasts)):
                dots += "<span style='color: #ec4899; font-size: 20px; margin: 0 4px;'>●</span>" if i == idx else "<span style='color: #ddd6fe; font-size: 20px; margin: 0 4px;'>●</span>"
            st.markdown(f"<div style='text-align: center; margin-top: 20px;'>{dots}</div>", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════════════════
    # PAGE 5 — PHOTO SLIDESHOW
    # ═══════════════════════════════════════════════════════════════════════════
    elif st.session_state.page == 5:
        st.markdown("<div style='height: 5vh;'></div>", unsafe_allow_html=True)

        c1, c2, c3 = st.columns([1, 4, 1])
        with c2:
            idx = st.session_state.photo_idx
            total_photos = 6  # 4 real + 2 placeholders

            st.markdown("""
            <div class="page-container" style="text-align: center; margin-bottom: 16px;">
                <p style="color: #a8557f; font-size: 0.9rem; text-transform: lowercase; letter-spacing: 1px;">
                    ur camera roll era 📸
                </p>
            </div>
            """, unsafe_allow_html=True)

            # Photo display
            if idx < 4:
                b64 = get_photo_base64(idx + 1)
                if b64:
                    st.markdown(f"""
                    <div class="photo-anim" style="text-align: center; margin-bottom: 16px;">
                        <img src="data:image/jpeg;base64,{b64}" 
                             style="width: 100%; max-width: 400px; aspect-ratio: 1; object-fit: cover; 
                                    border-radius: 20px; box-shadow: 0 12px 40px rgba(168, 85, 247, 0.2);"
                             alt="Sayumi photo {idx+1}">
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    emojis = ["📸", "🤳", "📷", "🎞️"]
                    st.markdown(f"""
                    <div class="photo-anim card" style="text-align: center; margin-bottom: 16px; aspect-ratio: 1; display: flex; align-items: center; justify-content: center; max-width: 400px; margin-left: auto; margin-right: auto;">
                        <div style="font-size: 4rem;">{emojis[idx]}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                placeholders = ["🎀", "✨"]
                st.markdown(f"""
                <div class="photo-anim card" style="text-align: center; margin-bottom: 16px; aspect-ratio: 1; display: flex; align-items: center; justify-content: center; max-width: 400px; margin-left: auto; margin-right: auto;">
                    <div style="font-size: 4rem;">{placeholders[idx-4]}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<p style='text-align: center; color: #a855f7; font-size: 0.85rem; margin-bottom: 20px;'>tap to go to next pic 📷</p>", unsafe_allow_html=True)

            st.markdown("<div class='pink-btn'>", unsafe_allow_html=True)
            if st.button("next pic 📷", use_container_width=True):
                st.session_state.photo_idx = (idx + 1) % total_photos
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

            # Dots
            dots = ""
            for i in range(total_photos):
                dots += "<span style='color: #ec4899; font-size: 18px; margin: 0 4px;'>●</span>" if i == idx else "<span style='color: #ddd6fe; font-size: 18px; margin: 0 4px;'>●</span>"
            st.markdown(f"<div style='text-align: center; margin-top: 20px;'>{dots}</div>", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════════════════
    # PAGE 6 — YES/NO GAME
    # ═══════════════════════════════════════════════════════════════════════════
    elif st.session_state.page == 6:
        st.markdown("<div style='height: 5vh;'></div>", unsafe_allow_html=True)

        c1, c2, c3 = st.columns([1, 4, 1])
        with c2:
            questions = [
                ("ur old now aren't u? 😂", "SHE ADMITTED IT 😂💗 welcome to old age"),
                ("should i get slapped rn? 🫳", "she said yes 💀 i accept my fate"),
                ("ur da best bsf right? 🥺", "correct!! 💗 that was the only right answer"),
                ("will u be more active this year? 📷", "she promised!! 💗 im holding u to that"),
                ("will u enjoy ur bday? 🎂", "good!! 🎂💗 as it should be!")
            ]

            q_idx = st.session_state.q_idx

            if q_idx < len(questions):
                q_text, yes_resp = questions[q_idx]

                st.markdown(f"""
                <div class="page-container card" style="text-align: center; margin-bottom: 30px;">
                    <p style="font-size: 1.2rem; color: #4c1d95; margin-bottom: 24px;">{q_text}</p>
                </div>
                """, unsafe_allow_html=True)

                # YES/NO buttons in a bordered box
                st.markdown("""
                <div style="border: 2px solid rgba(168, 85, 247, 0.2); border-radius: 20px; padding: 24px; margin-bottom: 20px;">
                """, unsafe_allow_html=True)

                escapes = st.session_state.no_escapes
                no_texts = ["NO", "no... 🫣", "noooo 😭", "please no", "stop", "💀"]
                no_text = no_texts[min(escapes, len(no_texts)-1)]
                no_scale = max(0.4, 1.0 - escapes * 0.12)

                yes_col, no_col = st.columns(2)

                with yes_col:
                    st.markdown("<div class='pink-btn'>", unsafe_allow_html=True)
                    if st.button("YES 💗", key=f"yes_{q_idx}", use_container_width=True):
                        st.session_state.yes_clicked = True
                        st.session_state.yes_msg = yes_resp
                        trigger_hearts()
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

                with no_col:
                    if escapes < 6:
                        st.markdown(f"""
                        <style>
                        .no-btn-{escapes} > button {{
                            background: rgba(255,255,255,0.5) !important;
                            color: #7c3aed !important;
                            transform: scale({no_scale}) !important;
                            transition: all 0.3s ease !important;
                        }}
                        </style>
                        """, unsafe_allow_html=True)
                        st.markdown(f"<div class='no-btn-{escapes} secondary-btn'>", unsafe_allow_html=True)
                        if st.button(no_text, key=f"no_{q_idx}_{escapes}", use_container_width=True):
                            st.session_state.no_escapes = escapes + 1
                            st.rerun()
                        st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<div style='text-align: center; color: #a855f7; font-size: 0.8rem; padding-top: 10px;'>💀</div>", unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)

                # Show YES response and auto-advance
                if st.session_state.yes_clicked:
                    st.markdown(f"""
                    <div style="text-align: center; margin-top: 20px; animation: pageEnter 0.5s ease;">
                        <p style="color: #ec4899; font-size: 1.1rem; font-weight: 600;">{st.session_state.yes_msg}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    time.sleep(2.5)
                    st.session_state.yes_clicked = False
                    st.session_state.yes_msg = ""
                    st.session_state.no_escapes = 0
                    st.session_state.q_idx = q_idx + 1
                    st.rerun()
            else:
                # All questions done
                st.markdown("""
                <div class="page-container card" style="text-align: center;">
                    <p style="font-size: 1.3rem; color: #4c1d95;">u survived the questions 😂💗</p>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
                st.markdown("<div class='pink-btn'>", unsafe_allow_html=True)
                if st.button("continue 💗", use_container_width=True):
                    st.session_state.q_idx = 0
                    st.session_state.no_escapes = 0
                    st.session_state.page = 7
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════════════════
    # PAGE 7 — BIRTHDAY MESSAGE
    # ═══════════════════════════════════════════════════════════════════════════
    elif st.session_state.page == 7:
        st.markdown("<div style='height: 3vh;'></div>", unsafe_allow_html=True)

        c1, c2, c3 = st.columns([1, 4, 1])
        with c2:
            st.markdown("""
            <div class="page-container card scroll-card" style="margin-bottom: 20px;">
                <div style="font-size: 3rem; color: #ddd6fe; line-height: 0.5; margin-bottom: 8px;">"</div>
                <div style="color: #7c3aed; line-height: 1.7; font-size: 1.05rem;">
                    <p style="margin-bottom: 16px;">
                        happy birthday sayumi 💗🎂 ur officially old now and i hope ur having the best time lmao. 
                        i still remember cambridge 6, the quiet nerd in the corner who wouldn't say a word to anyone, 
                        BUT NOT NOW OKK?? now she threatens to slap me every day and somehow thats become one of 
                        my fav things about her 😭
                    </p>
                    <p style="margin-bottom: 16px;">
                        ik ive been a bit quiet lately and im sorry for that, but i need u to know that never changed 
                        how much u mean to me. u wrote me 4 whole pages once for jz no reason and i still think about 
                        that, cuz thats jz who u are. u give so much without even thinking about it and i dont say this 
                        enough but im so glad to have u in my life. like actually glad, not jz saying it. uuve been there 
                        through so much and i dont take that for granted 🥹
                    </p>
                    <p style="margin-bottom: 16px;">
                        the kind of bsf that checks on u, roasts u, threatens to hit u, and somehow still makes u feel 
                        like the luckiest person in the room 😂🫶
                    </p>
                    <p style="margin-bottom: 16px;">
                        have the best birthday okay. wear black obviously. eat way too much cake. and please jz go talk 
                        to geenuka already ur going to give yourself a heart attack every time i say his name 😭💙
                    </p>
                    <p style="margin-bottom: 20px;">
                        cheers to u being a bit older, more unbothered and still living in the same era as me 🎂🫶🥹
                    </p>
                    <p style="color: #a855f7; font-style: italic; text-align: right;">
                        — ur bsf, always 💗
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<div class='pink-btn'>", unsafe_allow_html=True)
            if st.button("next page 💗", use_container_width=True):
                st.session_state.page = 8
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════════════════
    # PAGE 8 — FUN FACTS
    # ═══════════════════════════════════════════════════════════════════════════
    elif st.session_state.page == 8:
        st.markdown("<div style='height: 5vh;'></div>", unsafe_allow_html=True)

        c1, c2, c3 = st.columns([1, 4, 1])
        with c2:
            st.markdown("""
            <div class="page-container" style="text-align: center; margin-bottom: 24px;">
                <p style="color: #a855f7; font-size: 0.9rem; text-transform: lowercase; letter-spacing: 1px;">
                    some things about u 🥹
                </p>
            </div>
            """, unsafe_allow_html=True)

            facts = [
                ("🎆", "u came a long way", "from the quiet girl in cambridge 6 to the person who threatens to slap me daily. genuinely proud of this era."),
                ("📝", "u wrote me 4 pages. for no reason.", "that says everything about who u are. u care a lot even when u dont have to."),
                ("🖤", "the black fit era will never end", "and honestly? it shouldnt. it works.")
            ]

            for emoji, title, desc in facts:
                st.markdown(f"""
                <div class="card" style="margin-bottom: 16px; animation: pageEnter 0.5s ease;">
                    <div style="font-size: 1.8rem; margin-bottom: 8px;">{emoji}</div>
                    <h3 style="color: #4c1d95; margin-bottom: 6px; font-size: 1.1rem;">{title}</h3>
                    <p style="color: #7c3aed; font-size: 0.95rem; line-height: 1.5; margin: 0;">{desc}</p>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            st.markdown("<div class='pink-btn'>", unsafe_allow_html=True)
            if st.button("next page 🎙️", use_container_width=True):
                st.session_state.page = 9
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════════════════
    # PAGE 9 — HER SINGING
    # ═══════════════════════════════════════════════════════════════════════════
    elif st.session_state.page == 9:
        st.markdown("<div style='height: 5vh;'></div>", unsafe_allow_html=True)

        c1, c2, c3 = st.columns([1, 4, 1])
        with c2:
            st.markdown("""
            <div class="page-container" style="text-align: center; margin-bottom: 20px;">
                <p style="color: #a855f7; font-size: 0.9rem; text-transform: lowercase; letter-spacing: 1px;">
                    wait... is that her singing? 🎙️
                </p>
            </div>
            """, unsafe_allow_html=True)

            # Music player card
            st.markdown("""
            <div class="card" style="text-align: center; margin-bottom: 24px;">
                <div style="font-size: 2.5rem; margin-bottom: 8px;">🎵</div>
                <h3 style="color: #4c1d95; margin-bottom: 4px;">freak of the fall</h3>
                <p style="color: #a855f7; font-size: 0.9rem; margin-bottom: 20px;">featuring: sayumi live 🎙️</p>

                <!-- Animated music bars -->
                <div style="display: flex; justify-content: center; align-items: flex-end; height: 70px; gap: 4px; margin-bottom: 20px;">
                    <div class="music-bar" style="animation-delay: 0s; height: 30px;"></div>
                    <div class="music-bar" style="animation-delay: 0.15s; height: 50px;"></div>
                    <div class="music-bar" style="animation-delay: 0.3s; height: 40px;"></div>
                    <div class="music-bar" style="animation-delay: 0.45s; height: 60px;"></div>
                    <div class="music-bar" style="animation-delay: 0.6s; height: 35px;"></div>
                    <div class="music-bar" style="animation-delay: 0.75s; height: 55px;"></div>
                    <div class="music-bar" style="animation-delay: 0.9s; height: 45px;"></div>
                    <div class="music-bar" style="animation-delay: 1.05s; height: 50px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Native audio player
            audio_path = os.path.join(os.path.dirname(__file__), "sayumi_singing.ogg")
            if os.path.exists(audio_path):
                st.audio(audio_path, format="audio/ogg")
            else:
                st.markdown("""
                <div style="text-align: center; padding: 20px; color: #a855f7; background: rgba(255,255,255,0.5); border-radius: 12px;">
                    🎵 Audio file not found — place "sayumi_singing.ogg" in the same folder
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<p style='text-align: center; color: #a855f7; font-size: 0.85rem; margin-top: 16px;'>she actually sang this 😭💗</p>", unsafe_allow_html=True)

            st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
            st.markdown("<div class='pink-btn'>", unsafe_allow_html=True)
            if st.button("next page 🎂", use_container_width=True):
                st.session_state.page = 10
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # ═══════════════════════════════════════════════════════════════════════════
    # PAGE 10 — ENDING
    # ═══════════════════════════════════════════════════════════════════════════
    elif st.session_state.page == 10:
        st.markdown("<div style='height: 8vh;'></div>", unsafe_allow_html=True)

        c1, c2, c3 = st.columns([1, 4, 1])
        with c2:
            st.markdown("""
            <div class="page-container" style="text-align: center;">
                <h1 class="gradient-text" style="font-size: 3.5rem; margin-bottom: 20px; line-height: 1.2;">
                    Happy Birthday 🎂
                </h1>
                <p style="color: #7c3aed; font-size: 1.05rem; line-height: 1.7; margin-bottom: 40px;">
                    this only happens once a year. hope u make it count.<br>
                    wear black. eat cake. be unbothered.<br>
                    thats the whole plan. 💗
                </p>
            </div>
            """, unsafe_allow_html=True)

            btn_cols = st.columns(2)
            with btn_cols[0]:
                st.markdown("<div class='pink-btn'>", unsafe_allow_html=True)
                if st.button("one last confetti 🎉", use_container_width=True):
                    trigger_confetti()
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
            with btn_cols[1]:
                st.markdown("<div class='secondary-btn'>", unsafe_allow_html=True)
                if st.button("one last heart shower 💗", use_container_width=True):
                    trigger_hearts()
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("""
            <div style="text-align: center; margin-top: 50px; padding-bottom: 40px;">
                <p style="color: #a855f7; font-size: 0.85rem; opacity: 0.7;">
                    made with 💗 · for sayumi · august 6th 2026
                </p>
            </div>
            """, unsafe_allow_html=True)
