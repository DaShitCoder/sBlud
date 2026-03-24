import streamlit as st
import requests
from firebase_auth_component import firebase_auth_button
import os

BASE_URL = os.environ.get("API_BASE_URL", "127.0.0.1:8000")
API_URL = f"https://{BASE_URL}/api/chat" if "onrender.com" in BASE_URL else f"http://{BASE_URL}/api/chat"
SOS_API_URL = f"https://{BASE_URL}/api/sos-chat" if "onrender.com" in BASE_URL else f"http://{BASE_URL}/api/sos-chat"

st.set_page_config(page_title="StressBud", page_icon="🌱", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    .stApp { font-family: 'Inter', sans-serif; }

    [data-testid="stAppDeployButton"] { display: none !important; }

    /* Hero */
    .hero-title {
        text-align: center;
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0.25rem;
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-subtitle {
        text-align: center;
        font-size: 1.1rem;
        color: #b0b0b0;
        margin-bottom: 2.5rem;
        font-weight: 400;
    }

    /* ── Sign-out pill injected next to the three-dot menu ── */
    /* We position it fixed, just to the LEFT of the three-dot (≈48px from right) */
    .signout-fixed-btn {
        position: fixed;
        top: 10px;
        right: 56px;          /* sits right next to the ⋮ button */
        z-index: 99999;
    }
    .signout-fixed-btn button {
        pointer-events: all !important;
        padding: 0.3rem 1rem !important;
        font-size: 0.76rem !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        border-radius: 20px !important;
        border: 1px solid rgba(255,255,255,0.18) !important;
        background: rgba(20,20,35,0.85) !important;
        color: #bbb !important;
        cursor: pointer !important;
        backdrop-filter: blur(10px) !important;
        white-space: nowrap !important;
        min-height: 0 !important;
        line-height: 1.6 !important;
        width: auto !important;
    }
    .signout-fixed-btn button:hover {
        border-color: rgba(255,255,255,0.35) !important;
        color: #fff !important;
        background: rgba(40,40,65,0.95) !important;
    }

    /* ── Footer action buttons (SOS + Syllabus) ── */
    .footer-actions {
        display: flex;
        justify-content: center;
        gap: 0.75rem;
        margin-top: 0.6rem;
        padding-bottom: 0.5rem;
    }

    /* SOS button styling */
    .sos-btn-wrap button {
        background: rgba(255,45,45,0.1) !important;
        border: 1px solid rgba(255,60,60,0.45) !important;
        color: #ff6b6b !important;
        border-radius: 22px !important;
        font-size: 0.82rem !important;
        font-weight: 700 !important;
        padding: 0.38rem 1.4rem !important;
        letter-spacing: 0.4px !important;
        transition: all 0.2s ease !important;
        animation: sos-glow 2s ease-in-out infinite !important;
        width: auto !important;
        min-width: 0 !important;
        min-height: 0 !important;
    }
    .sos-btn-wrap button:hover {
        background: rgba(255,45,45,0.22) !important;
        border-color: rgba(255,100,100,0.7) !important;
        box-shadow: 0 0 16px rgba(255,60,60,0.3) !important;
        animation: none !important;
    }
    @keyframes sos-glow {
        0%,100% { box-shadow: 0 0 5px rgba(255,60,60,0.18); }
        50%      { box-shadow: 0 0 14px rgba(255,60,60,0.42); }
    }

    /* Syllabus button styling */
    .syllabus-btn-wrap button {
        background: rgba(67,233,123,0.08) !important;
        border: 1px solid rgba(67,233,123,0.35) !important;
        color: #43e97b !important;
        border-radius: 22px !important;
        font-size: 0.82rem !important;
        font-weight: 700 !important;
        padding: 0.38rem 1.4rem !important;
        letter-spacing: 0.4px !important;
        transition: all 0.2s ease !important;
        width: auto !important;
        min-width: 0 !important;
        min-height: 0 !important;
    }
    .syllabus-btn-wrap button:hover {
        background: rgba(67,233,123,0.18) !important;
        border-color: rgba(67,233,123,0.6) !important;
        box-shadow: 0 0 14px rgba(67,233,123,0.25) !important;
    }

    /* Helpline banner */
    .helpline-banner {
        background: linear-gradient(145deg, #1a0000, #2d0a0a);
        border: 1px solid rgba(255,60,60,0.3);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
    }
    .helpline-banner h3 { color: #ff6b6b; font-size: 1.1rem; margin-bottom: 0.75rem; font-weight: 700; }
    .helpline-item { display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0; border-bottom: 1px solid rgba(255,255,255,0.05); font-size: 0.95rem; }
    .helpline-item:last-child { border-bottom: none; }
    .helpline-name { color: #e0e0e0; font-weight: 500; }
    .helpline-number { color: #ff9999; font-weight: 700; font-family: monospace; letter-spacing: 0.5px; }

    /* Back button */
    .back-btn button {
        background: transparent !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        color: #b0b0b0 !important;
        border-radius: 12px !important;
        padding: 0.5rem 1.25rem !important;
        font-weight: 500 !important;
        min-height: 0 !important;
    }
    .back-btn button:hover { border-color: rgba(255,255,255,0.3) !important; color: #fff !important; }

    .sos-header { text-align: center; font-size: 1.8rem; font-weight: 800; color: #ff6b6b; margin-bottom: 0.25rem; }
    .sos-subheader { text-align: center; font-size: 1rem; color: #999; margin-bottom: 1.5rem; }

    /* Mode header (syllabus) */
    .mode-header {
        text-align: center;
        font-size: 1.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #43e97b, #38f9d7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .mode-subheader {
        text-align: center;
        font-size: 1rem;
        color: #888;
        margin-bottom: 1.5rem;
    }

    .stChatMessage { border-radius: 16px !important; }
</style>
""", unsafe_allow_html=True)

# ─── Session State ────────────────────────────────────────────────────────────
if "mode" not in st.session_state:
    st.session_state.mode = "auth"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "sos_messages" not in st.session_state:
    st.session_state.sos_messages = []
if "sos_initialized" not in st.session_state:
    st.session_state.sos_initialized = False
if "syllabus_messages" not in st.session_state:
    st.session_state.syllabus_messages = []
if "syllabus_initialized" not in st.session_state:
    st.session_state.syllabus_initialized = False
if "user" not in st.session_state:
    st.session_state.user = None

# ─── Helper ───────────────────────────────────────────────────────────────────
def call_backend(endpoint, message):
    try:
        response = requests.post(endpoint, json={"message": message})
        if response.status_code == 200:
            return response.json().get("reply", "Something went wrong.")
        return f"Error: {response.status_code}"
    except Exception as e:
        return f"Error connecting to backend: {e}"

# ─── AUTH PAGE ────────────────────────────────────────────────────────────────
if st.session_state.mode == "auth":
    st.markdown('<div class="hero-title">🌱 StressBud</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Your companion for exam season : mentor, friend, therapist, advisor.</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h3 style='text-align:center'>Join StressBud</h3>", unsafe_allow_html=True)
        user_data = firebase_auth_button(key="login_button_auth")
        if user_data:
            st.session_state.user = user_data
            st.session_state.mode = "home"
            st.rerun()
        st.markdown("<div style='text-align:center;margin:1rem 0'>or</div>", unsafe_allow_html=True)
        if st.button("Join as Guest", use_container_width=True):
            st.session_state.user = {"displayName": "Guest"}
            st.session_state.mode = "home"
            st.rerun()

# ─── HOME / Chat Page ─────────────────────────────────────────────────────────
elif st.session_state.mode == "home":

    # Sign-out button — fixed, next to the three-dot menu in the header
    user_name = st.session_state.user.get('displayName', 'Guest') if st.session_state.user else "Guest"

    st.markdown('<div class="signout-fixed-btn">', unsafe_allow_html=True)
    if st.button(f"👋 {user_name}  ·  Sign Out", key="signout_btn"):
        st.session_state.user = None
        st.session_state.mode = "auth"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="hero-title">🌱 StressBud</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Let\'s chat. I\'m here for you.</div>', unsafe_allow_html=True)
    st.markdown("---")

    # Chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Chat with StressBud"):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        reply = call_backend(API_URL, prompt)
        with st.chat_message("assistant"):
            st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})

    # ── Footer: SOS + Syllabus buttons below the chat input ──
    col_sos, col_syllabus = st.columns(2)

    with col_sos:
        st.markdown('<div class="sos-btn-wrap">', unsafe_allow_html=True)
        if st.button("🚨 SOS", key="btn_sos", use_container_width=True):
            st.session_state.mode = "sos"
            st.session_state.sos_initialized = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_syllabus:
        st.markdown('<div class="syllabus-btn-wrap">', unsafe_allow_html=True)
        if st.button("📚 Syllabus", key="btn_syllabus", use_container_width=True):
            st.session_state.mode = "syllabus"
            st.session_state.syllabus_initialized = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ─── SOS Mode ────────────────────────────────────────────────────────────────
elif st.session_state.mode == "sos":

    st.markdown('<div class="back-btn">', unsafe_allow_html=True)
    if st.button("← Back to Home", key="btn_back"):
        st.session_state.mode = "home"
        st.session_state.sos_messages = []
        st.session_state.sos_initialized = False
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="sos-header">🚨 SOS — You\'re Safe Here</div>', unsafe_allow_html=True)
    st.markdown('<div class="sos-subheader">Take a breath. You\'re not alone. Let\'s talk.</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="helpline-banner">
        <h3>📞 Crisis Helplines (India)</h3>
        <div class="helpline-item">
            <span class="helpline-name">iCall (Mon-Sat, 9am-9pm)</span>
            <span class="helpline-number">9152987821</span>
        </div>
        <div class="helpline-item">
            <span class="helpline-name">Vandrevala Foundation (24/7)</span>
            <span class="helpline-number">1860-2662-345</span>
        </div>
        <div class="helpline-item">
            <span class="helpline-name">AASRA (24/7)</span>
            <span class="helpline-number">9820466626</span>
        </div>
        <div class="helpline-item">
            <span class="helpline-name">Snehi</span>
            <span class="helpline-number">044-24640050</span>
        </div>
        <div class="helpline-item">
            <span class="helpline-name">Emergency</span>
            <span class="helpline-number">112</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.sos_initialized:
        init_message = (
            "[SOS MODE ACTIVATED] The user has just pressed the emergency SOS button. "
            "They may be experiencing a crisis — depression, suicidal thoughts, or a panic attack. "
            "Please greet them warmly and gently. Ask them what's going on. Offer an immediate breathing exercise."
        )
        reply = call_backend(SOS_API_URL, init_message)
        st.session_state.sos_messages.append({"role": "assistant", "content": reply})
        st.session_state.sos_initialized = True

    for message in st.session_state.sos_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("I'm here. Talk to me..."):
        st.chat_message("user").markdown(prompt)
        st.session_state.sos_messages.append({"role": "user", "content": prompt})
        reply = call_backend(SOS_API_URL, prompt)
        with st.chat_message("assistant"):
            st.markdown(reply)
        st.session_state.sos_messages.append({"role": "assistant", "content": reply})

# ─── SYLLABUS Mode ────────────────────────────────────────────────────────────
elif st.session_state.mode == "syllabus":

    st.markdown('<div class="back-btn">', unsafe_allow_html=True)
    if st.button("← Back to Home", key="btn_back_syllabus"):
        st.session_state.mode = "home"
        st.session_state.syllabus_messages = []
        st.session_state.syllabus_initialized = False
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="mode-header">📚 Syllabus Help</div>', unsafe_allow_html=True)
    st.markdown('<div class="mode-subheader">Let\'s make a plan and tackle it together.</div>', unsafe_allow_html=True)

    # Auto greeting on first load
    if not st.session_state.syllabus_initialized:
        init_message = (
            "Syllabus mode. A student needs help with their exam preparation and pending syllabus. "
            "Greet them warmly and ask what subject or topic they're stuck on or need help planning."
        )
        reply = call_backend(API_URL, init_message)
        st.session_state.syllabus_messages.append({"role": "assistant", "content": reply})
        st.session_state.syllabus_initialized = True

    for message in st.session_state.syllabus_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Tell me what you need help with..."):
        st.chat_message("user").markdown(prompt)
        st.session_state.syllabus_messages.append({"role": "user", "content": prompt})
        reply = call_backend(API_URL, prompt)
        with st.chat_message("assistant"):
            st.markdown(reply)
        st.session_state.syllabus_messages.append({"role": "assistant", "content": reply})
