import os
from typing import Optional, List

import google.generativeai as genai
import streamlit as st
from PIL import Image

st.set_page_config(page_title="Chart Explainer AI", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

if "theme" not in st.session_state:
    st.session_state["theme"] = "light"
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "upload_key" not in st.session_state:
    st.session_state["upload_key"] = 0
if "pending_image" not in st.session_state:
    st.session_state["pending_image"] = None

THEMES = {
    "light": {
        "bg": "#F8F6F1", "surface": "#FFFFFF", "surface2": "#F0EDE5", "border": "#E3DED3",
        "accent": "#B8751A", "text": "#1C1A16", "text_sub": "#6B6355", "text_muted": "#A8A090",
        "btn_bg": "#1C1A16", "btn_text": "#FFFFFF", "shadow_sm": "0 1px 3px rgba(0,0,0,0.06)",
        "shadow_md": "0 4px 16px rgba(0,0,0,0.08)", "theme_label": "Dark mode", "next_theme": "dark",
    },
    "dark": {
        "bg": "#111110", "surface": "#1A1917", "surface2": "#222120", "border": "#2E2C28",
        "accent": "#C9913A", "text": "#EDE9E0", "text_sub": "#7A7060", "text_muted": "#4A4840",
        "btn_bg": "#C9913A", "btn_text": "#111110", "shadow_sm": "0 1px 3px rgba(0,0,0,0.4)",
        "shadow_md": "0 4px 16px rgba(0,0,0,0.5)", "theme_label": "Light mode", "next_theme": "light",
    },
}
C = THEMES[st.session_state["theme"]]

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Serif+Display&display=swap');
:root { --bg: __bg__; --surface: __surface__; --surface2: __surface2__; --border: __border__; --accent: __accent__; --text: __text__; --text-sub: __text_sub__; --text-muted: __text_muted__; --btn-bg: __btn_bg__; --btn-text: __btn_text__; --shadow-sm: __shadow_sm__; --shadow-md: __shadow_md__; --radius: 14px; --radius-sm: 8px; }
html, body, .stApp { background: var(--bg) !important; color: var(--text) !important; font-family: 'DM Sans', sans-serif !important; }
.main .block-container { max-width: 720px !important; padding: 0 24px 36px !important; margin: 0 auto !important; }
[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"], footer { display: none !important; }
* { font-family: 'DM Sans', sans-serif !important; }
h1, .serif-title { font-family: 'DM Serif Display', serif !important; }
p, li, label, span { color: var(--text) !important; }
strong, b { color: var(--accent) !important; font-weight: 600 !important; }
.topbar { display: flex; align-items: center; justify-content: space-between; padding: 20px 0 16px; border-bottom: 1px solid var(--border); margin-bottom: 20px; }
.topbar-logo { font-family: 'DM Serif Display', serif !important; font-size: 1rem; letter-spacing: .02em; color: var(--text) !important; }
.landing-body { min-height: calc(100vh - 440px); display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 28px 0 32px; }
.landing-kicker { font-size: .95rem; color: var(--text-sub) !important; margin: 0 0 6px; text-align: center; }
.landing-headline { font-family: 'DM Serif Display', serif !important; font-size: 2.4rem; color: var(--text) !important; line-height: 1.15; margin: 0 0 8px; text-align: center; font-weight: 400 !important; }
.landing-sub { font-size: 1rem; color: var(--text-sub) !important; text-align: center; margin: 0 0 34px; }
.landing-card { background: var(--surface); border: 1px solid var(--border); border-radius: 18px; padding: 24px; box-shadow: var(--shadow-md); width: 100%; }
.label-small { font-size: .72rem; font-weight: 600; letter-spacing: .1em; text-transform: uppercase; color: var(--text-muted) !important; margin-bottom: 8px; }
.card-divider { height: 1px; background: var(--border); margin: 14px -24px; }
.char-hint { font-size: .75rem; color: var(--text-muted) !important; padding-top: 8px; }
[data-testid="stForm"] { background: transparent !important; border: 0 !important; padding: 0 !important; }
[data-testid="stForm"] > div { gap: 0 !important; }
[data-testid="stFileUploader"] { margin-bottom: 0 !important; }
[data-testid="stFileUploader"] > div:first-child { background: transparent !important; border: 0 !important; }
[data-testid="stFileUploaderDropzone"] { background: var(--surface) !important; border: 1.5px dashed var(--border) !important; border-radius: var(--radius) !important; padding: 28px 20px !important; min-height: 118px !important; transition: all .2s !important; }
[data-testid="stFileUploaderDropzone"]:hover { border-color: var(--accent) !important; }
[data-testid="stFileUploaderDropzoneInstructions"] p, [data-testid="stFileUploaderDropzoneInstructions"] small { color: var(--text-muted) !important; font-size: .8rem !important; }
[data-testid="stFileUploaderDropzone"] button { background: var(--surface2) !important; color: var(--text-sub) !important; border: 1px solid var(--border) !important; border-radius: 8px !important; font-size: .78rem !important; padding: 7px 14px !important; }
[data-testid="stFileUploaderDropzone"] button:hover { color: var(--accent) !important; border-color: var(--accent) !important; }
textarea { background: transparent !important; color: var(--text) !important; border: none !important; border-radius: 0 !important; font-size: .9rem !important; line-height: 1.6 !important; box-shadow: none !important; resize: none !important; }
textarea::placeholder { color: var(--text-muted) !important; }
[data-testid="stTextArea"] { margin-top: 0 !important; }
[data-testid="stTextArea"] > div { background: transparent !important; }
[data-testid="stTextArea"] textarea { min-height: 56px !important; padding: 2px 0 !important; }
[data-testid="stRadio"] > div { display: flex !important; background: var(--surface2) !important; border: 1px solid var(--border) !important; border-radius: 10px !important; padding: 3px !important; gap: 2px !important; margin: 0 auto 24px !important; max-width: 380px !important; }
[data-testid="stRadio"] label { flex: 1 !important; justify-content: center !important; padding: 9px 16px !important; border-radius: 8px !important; cursor: pointer !important; transition: all .2s !important; }
[data-testid="stRadio"] label:has(input:checked) { background: var(--surface) !important; box-shadow: var(--shadow-sm) !important; }
[data-testid="stRadio"] label p { color: var(--text-sub) !important; font-size: .85rem !important; font-weight: 500 !important; }
[data-testid="stRadio"] label:has(input:checked) p { color: var(--text) !important; }
.stButton > button, [data-testid="stFormSubmitButton"] > button { border-radius: var(--radius-sm) !important; font-weight: 500 !important; font-size: .875rem !important; transition: all .2s !important; min-height: 38px !important; white-space: nowrap !important; }
.stButton > button[kind="primary"], [data-testid="stFormSubmitButton"] > button { background: var(--btn-bg) !important; color: var(--btn-text) !important; border: none !important; box-shadow: var(--shadow-sm) !important; }
.stButton > button[kind="primary"]:hover, [data-testid="stFormSubmitButton"] > button:hover { opacity: .88 !important; transform: translateY(-1px) !important; box-shadow: var(--shadow-md) !important; }
.stButton > button[kind="secondary"] { background: transparent !important; color: var(--text-sub) !important; border: 1px solid var(--border) !important; }
.stButton > button[kind="secondary"]:hover { border-color: var(--accent) !important; color: var(--accent) !important; }
.stButton > button p, .stButton > button span, [data-testid="stFormSubmitButton"] p, [data-testid="stFormSubmitButton"] span { color: inherit !important; font-size: inherit !important; }
.preview-wrap img, [data-testid="stImage"] img { border: 1px solid var(--border) !important; border-radius: var(--radius) !important; background: var(--surface2) !important; }
[data-testid="stChatMessage"] { background: transparent !important; padding: 8px 0 !important; }
[data-testid="stChatMessageContent"] { background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: 14px !important; padding: 13px 16px !important; box-shadow: var(--shadow-sm) !important; }
[data-testid="stChatMessageContent"] p, [data-testid="stChatMessageContent"] li { color: var(--text) !important; font-size: .875rem !important; line-height: 1.75 !important; }
[data-testid="stChatInput"] textarea { background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: 14px !important; color: var(--text) !important; }
.stChatInputContainer { background: var(--bg) !important; border-top: 1px solid var(--border) !important; padding-top: 14px !important; }
.attach-card { background: var(--surface2); border: 1px solid var(--border); border-radius: 10px; padding: 10px 12px; margin: 12px 0 10px; }
.attach-card p { margin: 0 0 8px !important; font-size: .72rem !important; letter-spacing: .1em !important; text-transform: uppercase !important; color: var(--text-muted) !important; font-weight: 600 !important; }
.sample-row { display: flex; align-items: center; justify-content: center; gap: 8px; margin-top: 24px; flex-wrap: wrap; }
.sample-label { font-size: .75rem; color: var(--text-muted) !important; font-weight: 500; letter-spacing: .04em; }
.footer-note { text-align: center; font-size: .68rem; color: var(--text-muted) !important; letter-spacing: .1em; margin-top: 2rem; }
hr { border: none !important; border-top: 1px solid var(--border) !important; }
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 99px; }
@media(max-width: 600px) { .main .block-container { padding: 0 16px 32px !important; } .landing-headline { font-size: 2rem !important; } }
</style>
"""

for key, value in C.items():
    CSS = CSS.replace(f"__{key}__", value)
st.markdown(CSS, unsafe_allow_html=True)

@st.cache_resource
def get_model():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        st.error("GEMINI_API_KEY not found. Add it as a Streamlit secret or environment variable.")
        st.stop()
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.5-flash")

ANALYSIS_PROMPT = """You are an expert data analyst. Analyze this chart clearly and concisely.

**What it shows**
One sentence: what the chart is and what data it presents.

**Key Trend**
The main trend or pattern — be specific with values, percentages, or time periods if visible.

**Notable Detail**
One standout insight: an outlier, anomaly, or something a casual reader might miss.

**Takeaway**
What should a decision-maker do or conclude? Keep it practical and actionable.

Be specific. Avoid vague statements."""

COMPARISON_PROMPT = """You are an expert data analyst comparing two charts.

**Chart 1 Summary**
One sentence: what Chart 1 shows and its main finding.

**Chart 2 Summary**
One sentence: what Chart 2 shows and its main finding.

**Key Similarities**
What patterns, trends, or characteristics do both charts share?

**Key Differences**
The most important differences between the two charts — be specific.

**Comparative Insight**
What story do these two charts tell together that neither tells alone?

**Recommendation**
What conclusion or action should the reader take based on both charts?"""

def generate_response(message: str, image: Optional[Image.Image], history: List[dict], image2: Optional[Image.Image] = None) -> str:
    model = get_model()
    if image and image2:
        prompt = COMPARISON_PROMPT
        if message and message not in ("Compare these charts.", ""):
            prompt += f"\n\nAlso specifically address: {message}"
        return model.generate_content(["Chart 1:", image, "Chart 2:", image2, prompt]).text

    ctx_image = image
    if ctx_image is None:
        for msg in reversed(history):
            if msg.get("image"):
                ctx_image = msg["image"]
                break

    is_first = image is not None and not any(m["role"] == "assistant" for m in history)
    if is_first:
        prompt = ANALYSIS_PROMPT
        if message and message not in ("Analyze this chart.", ""):
            prompt += f"\n\nAlso specifically address: {message}"
        return model.generate_content([prompt, image]).text

    parts = ["You are an expert data analyst. Answer the user's question about this chart concisely and specifically, referencing visible values or patterns."]
    if ctx_image:
        parts.append(ctx_image)
    for msg in history:
        parts.append(f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}")
    parts.append(f"User: {message}")
    return model.generate_content(parts).text

def toggle_theme(key):
    if st.button(C["theme_label"], key=key, type="secondary", use_container_width=True):
        st.session_state["theme"] = C["next_theme"]
        st.rerun()

def render_topbar(show_new_chat=False):
    st.markdown('<div class="topbar"><span class="topbar-logo">Chart Explainer</span></div>', unsafe_allow_html=True)
    if show_new_chat:
        c1, c2 = st.columns([1, 1])
        with c1:
            if st.button("+ New chat", key="new_chat", type="secondary", use_container_width=True):
                st.session_state["messages"] = []
                st.session_state["pending_image"] = None
                st.session_state["upload_key"] += 1
                st.rerun()
        with c2:
            toggle_theme("toggle_chat")
    else:
        _, c = st.columns([5, 1])
        with c:
            toggle_theme("toggle_land")

def open_image(uploaded_file):
    if uploaded_file is None:
        return None
    img = Image.open(uploaded_file)
    return img.copy()

has_messages = bool(st.session_state["messages"])
render_topbar(show_new_chat=has_messages)

if not has_messages:
    st.markdown("""
<div class="landing-body">
    <p class="landing-kicker">Hello! Let's get started —</p>
    <h1 class="landing-headline">Upload a chart to analyze</h1>
    <p class="landing-sub">I'll explain what it means in plain language.</p>
</div>
""", unsafe_allow_html=True)

    mode = st.radio("mode", ["Single chart", "Compare two charts"], horizontal=True, label_visibility="collapsed")
    st.markdown('<div class="landing-card">', unsafe_allow_html=True)
    with st.form("start_form", clear_on_submit=True):
        if mode == "Single chart":
            uploaded = st.file_uploader("Drop or click to upload a chart", type=["png", "jpg", "jpeg", "webp"], label_visibility="collapsed", key="land_single")
            uploaded2 = None
            if uploaded:
                st.markdown('<div class="preview-wrap">', unsafe_allow_html=True)
                st.image(open_image(uploaded), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            placeholder = "Any specific question? Optional — leave blank for a full analysis"
        else:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown('<p class="label-small">Chart 1</p>', unsafe_allow_html=True)
                uploaded = st.file_uploader("Upload chart 1", type=["png", "jpg", "jpeg", "webp"], label_visibility="collapsed", key="land_cmp1")
                if uploaded:
                    st.image(open_image(uploaded), use_container_width=True)
            with col2:
                st.markdown('<p class="label-small">Chart 2</p>', unsafe_allow_html=True)
                uploaded2 = st.file_uploader("Upload chart 2", type=["png", "jpg", "jpeg", "webp"], label_visibility="collapsed", key="land_cmp2")
                if uploaded2:
                    st.image(open_image(uploaded2), use_container_width=True)
            placeholder = "Any specific question about the comparison? Optional"

        st.markdown('<div class="card-divider"></div>', unsafe_allow_html=True)
        msg_input = st.text_area("Message", placeholder=placeholder, height=68, label_visibility="collapsed")
        bottom_l, bottom_r = st.columns([3, 1])
        with bottom_l:
            st.markdown('<span class="char-hint">Press Ctrl + Enter to submit</span>', unsafe_allow_html=True)
        with bottom_r:
            submitted = st.form_submit_button("Compare →" if mode == "Compare two charts" else "Analyze →", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="sample-row"><span class="sample-label">Tip: try a bar, line, pie, scatter, or heatmap screenshot.</span></div>', unsafe_allow_html=True)

    if submitted:
        img1 = open_image(uploaded)
        img2 = open_image(uploaded2)
        if mode == "Compare two charts" and (not img1 or not img2):
            st.warning("Please upload both charts to compare.")
        elif mode == "Single chart" and not img1 and not msg_input.strip():
            st.warning("Please upload a chart or type a message to get started.")
        else:
            message = msg_input.strip() or ("Compare these charts." if mode == "Compare two charts" else "Analyze this chart.")
            st.session_state["messages"].append({"role": "user", "content": message, "image": img1, "image2": img2})
            with st.spinner("Analyzing…"):
                response = generate_response(message, img1, [], image2=img2)
            st.session_state["messages"].append({"role": "assistant", "content": response, "image": None, "image2": None})
            st.rerun()
else:
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            if msg.get("image") and msg.get("image2"):
                c1, c2 = st.columns(2)
                with c1:
                    st.image(msg["image"], use_container_width=True)
                with c2:
                    st.image(msg["image2"], use_container_width=True)
            elif msg.get("image"):
                st.image(msg["image"], width=300)
            st.markdown(msg["content"])

    st.markdown('<div class="attach-card"><p>📎 Attach a new chart optional</p>', unsafe_allow_html=True)
    attach_left, attach_right = st.columns([3, 2])
    with attach_left:
        new_file = st.file_uploader("Attach", type=["png", "jpg", "jpeg", "webp"], key=f"chat_upload_{st.session_state['upload_key']}", label_visibility="collapsed")
    if new_file:
        st.session_state["pending_image"] = open_image(new_file)
        with attach_right:
            st.image(st.session_state["pending_image"], width=90)
    else:
        st.session_state["pending_image"] = None
    st.markdown('</div>', unsafe_allow_html=True)

    if prompt := st.chat_input("Ask a follow-up question…"):
        current_img = st.session_state.get("pending_image")
        history = list(st.session_state["messages"])
        st.session_state["messages"].append({"role": "user", "content": prompt, "image": current_img, "image2": None})
        with st.chat_message("user"):
            if current_img:
                st.image(current_img, width=300)
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                response = generate_response(prompt, current_img, history)
            st.markdown(response)
        st.session_state["messages"].append({"role": "assistant", "content": response, "image": None, "image2": None})
        if current_img:
            st.session_state["pending_image"] = None
            st.session_state["upload_key"] += 1

st.markdown('<p class="footer-note">GEMINI 2.5 FLASH · STREAMLIT DEPLOY READY</p>', unsafe_allow_html=True)
