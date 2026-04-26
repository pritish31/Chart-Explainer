import os
from typing import Optional, List

import google.generativeai as genai
import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Chart Explainer AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

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
        "bg": "#F8F6F1",
        "surface": "#FFFFFF",
        "surface2": "#F0EDE5",
        "border": "#E3DED3",
        "accent": "#B8751A",
        "text": "#1C1A16",
        "text_sub": "#6B6355",
        "text_muted": "#A8A090",
        "btn_bg": "#1C1A16",
        "btn_text": "#FFFFFF",
        "shadow_sm": "0 1px 3px rgba(0,0,0,0.06)",
        "shadow_md": "0 4px 16px rgba(0,0,0,0.08)",
        "theme_label": "◒  Dark mode",
        "next_theme": "dark",
    },
    "dark": {
        "bg": "#111110",
        "surface": "#1A1917",
        "surface2": "#222120",
        "border": "#2E2C28",
        "accent": "#C9913A",
        "text": "#EDE9E0",
        "text_sub": "#7A7060",
        "text_muted": "#4A4840",
        "btn_bg": "#C9913A",
        "btn_text": "#111110",
        "shadow_sm": "0 1px 3px rgba(0,0,0,0.4)",
        "shadow_md": "0 4px 16px rgba(0,0,0,0.5)",
        "theme_label": "☀  Light mode",
        "next_theme": "light",
    },
}
C = THEMES[st.session_state["theme"]]

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Serif+Display&display=swap');

:root {{
  --bg: {C['bg']}; --surface: {C['surface']}; --surface2: {C['surface2']};
  --border: {C['border']}; --accent: {C['accent']}; --text: {C['text']};
  --text-sub: {C['text_sub']}; --text-muted: {C['text_muted']};
  --btn-bg: {C['btn_bg']}; --btn-text: {C['btn_text']};
  --shadow-sm: {C['shadow_sm']}; --shadow-md: {C['shadow_md']};
}}

* {{ box-sizing: border-box; }}
html, body, .stApp {{
  background: var(--bg) !important;
  color: var(--text) !important;
  font-family: 'DM Sans', sans-serif !important;
}}
.stApp {{ min-height: 100vh; }}
[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"], footer {{ display: none !important; }}
.block-container {{
  max-width: 720px !important;
  padding: 0 24px 34px !important;
  margin: 0 auto !important;
}}
.main .block-container {{ max-width: 720px !important; }}
section.main > div {{ max-width: 720px !important; }}

h1, h2, h3, .topbar-logo, .landing-headline {{ font-family: 'DM Serif Display', serif !important; }}
p, span, label, div, button, textarea {{ font-family: 'DM Sans', sans-serif !important; }}
p, label, span {{ color: var(--text) !important; }}

.topbar-wrap {{
  height: 78px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--border);
  margin-bottom: 64px;
}}
.topbar-logo {{
  font-size: 1rem;
  font-weight: 600;
  letter-spacing: .02em;
  color: var(--text) !important;
  white-space: nowrap;
}}

.topbar-button [data-testid="stButton"] {{ margin: 0 !important; }}
.topbar-button button {{
  background: var(--surface2) !important;
  color: var(--text-sub) !important;
  border: 1px solid var(--border) !important;
  border-radius: 999px !important;
  padding: 6px 14px !important;
  min-height: 34px !important;
  font-size: .8rem !important;
  font-weight: 500 !important;
  box-shadow: none !important;
}}
.topbar-button button:hover {{ border-color: var(--accent) !important; color: var(--accent) !important; }}
.topbar-button button p {{ color: inherit !important; font-size: inherit !important; }}

.landing-copy {{ text-align: center; margin-bottom: 34px; }}
.landing-kicker {{ font-size: .95rem; color: var(--text-sub) !important; margin: 0 0 7px !important; }}
.landing-headline {{
  font-size: 2.4rem !important;
  font-weight: 400 !important;
  line-height: 1.15 !important;
  margin: 0 0 8px !important;
  color: var(--text) !important;
}}
.landing-sub {{ font-size: 1rem; color: var(--text-sub) !important; margin: 0 !important; }}

.mode-block {{ max-width: 380px; margin: 0 auto 26px; }}
[data-testid="stRadio"] {{ max-width: 380px !important; margin: 0 auto 26px !important; }}
[data-testid="stRadio"] > div {{
  display: flex !important;
  flex-direction: row !important;
  background: var(--surface2) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  padding: 3px !important;
  gap: 2px !important;
}}
[data-testid="stRadio"] label {{
  flex: 1 !important;
  min-height: 40px !important;
  display: flex !important;
  justify-content: center !important;
  align-items: center !important;
  border-radius: 8px !important;
  padding: 0 16px !important;
  cursor: pointer !important;
}}
[data-testid="stRadio"] label > div:first-child {{ display: none !important; }}
[data-testid="stRadio"] input {{ display: none !important; }}
[data-testid="stRadio"] label:has(input:checked) {{
  background: var(--surface) !important;
  box-shadow: var(--shadow-sm) !important;
}}
[data-testid="stRadio"] label p {{
  font-size: .85rem !important;
  font-weight: 500 !important;
  color: var(--text-sub) !important;
  white-space: nowrap !important;
}}
[data-testid="stRadio"] label:has(input:checked) p {{ color: var(--text) !important; }}

.landing-card-start {{
  width: 100%;
  max-width: 580px;
  margin: 0 auto;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 18px;
  box-shadow: var(--shadow-md);
  overflow: hidden;
}}
.landing-card-start [data-testid="stForm"] {{
  background: transparent !important;
  border: 0 !important;
  padding: 0 !important;
}}
.landing-card-start [data-testid="stForm"] > div {{ gap: 0 !important; }}
.upload-section {{ padding: 24px 24px 16px; }}
.question-section {{ border-top: 1px solid var(--border); padding: 18px 24px 24px; }}
.label-small {{
  font-size: .72rem !important;
  font-weight: 600 !important;
  letter-spacing: .1em !important;
  text-transform: uppercase !important;
  color: var(--text-muted) !important;
  margin: 0 0 8px !important;
}}

[data-testid="stFileUploader"] {{ margin: 0 !important; }}
[data-testid="stFileUploader"] section {{
  background: var(--surface) !important;
  border: 1.5px dashed var(--border) !important;
  border-radius: 14px !important;
  min-height: 120px !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  padding: 22px 20px !important;
}}
[data-testid="stFileUploader"] section:hover {{ border-color: var(--accent) !important; }}
[data-testid="stFileUploader"] section > div {{
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  text-align: center !important;
}}
[data-testid="stFileUploaderDropzoneInstructions"] {{ display: flex !important; flex-direction: column !important; align-items: center !important; }}
[data-testid="stFileUploaderDropzoneInstructions"] svg {{ display: none !important; }}
[data-testid="stFileUploaderDropzoneInstructions"]::before {{
  content: '▮▮▮';
  color: color-mix(in srgb, var(--accent) 55%, white);
  font-size: 24px;
  letter-spacing: -6px;
  transform: rotate(180deg);
  margin-bottom: 6px;
}}
[data-testid="stFileUploaderDropzoneInstructions"] p {{
  font-size: .875rem !important;
  font-weight: 500 !important;
  color: var(--text-sub) !important;
  margin: 0 0 3px !important;
}}
[data-testid="stFileUploaderDropzoneInstructions"] small {{
  font-size: .75rem !important;
  color: var(--text-muted) !important;
}}
[data-testid="stFileUploader"] button {{ display: none !important; }}
[data-testid="stFileUploaderFile"] {{ background: var(--surface2) !important; border: 1px solid var(--border) !important; border-radius: 10px !important; }}

[data-testid="stTextArea"] {{ margin: 0 !important; }}
[data-testid="stTextArea"] > div {{ background: transparent !important; }}
[data-testid="stTextArea"] textarea {{
  background: transparent !important;
  border: none !important;
  color: var(--text) !important;
  padding: 0 !important;
  font-size: .875rem !important;
  line-height: 1.6 !important;
  min-height: 54px !important;
  box-shadow: none !important;
  resize: none !important;
}}
[data-testid="stTextArea"] textarea::placeholder {{ color: var(--text-muted) !important; }}
[data-testid="stTextArea"] textarea:focus {{ box-shadow: none !important; outline: none !important; }}

.submit-row {{ margin-top: 8px; }}
.char-hint {{ font-size: .75rem !important; color: var(--text-muted) !important; padding-top: 8px; display: block; }}
[data-testid="stFormSubmitButton"] button {{
  background: var(--btn-bg) !important;
  color: var(--btn-text) !important;
  border: none !important;
  border-radius: 8px !important;
  min-height: 44px !important;
  padding: 11px 22px !important;
  font-size: .875rem !important;
  font-weight: 500 !important;
  box-shadow: var(--shadow-sm) !important;
}}
[data-testid="stFormSubmitButton"] button:hover {{ opacity: .88 !important; transform: translateY(-1px) !important; box-shadow: var(--shadow-md) !important; }}
[data-testid="stFormSubmitButton"] button p {{ color: inherit !important; font-size: inherit !important; }}

.preview-img img, [data-testid="stImage"] img {{
  border-radius: 14px !important;
  border: 1px solid var(--border) !important;
  background: var(--surface2) !important;
  max-height: 260px !important;
  object-fit: contain !important;
}}
.sample-row {{
  display: flex; align-items: center; justify-content: center; gap: 8px;
  margin: 24px auto 0; color: var(--text-muted) !important; font-size: .75rem;
}}
.sample-row img {{ width: 48px; height: 36px; object-fit: cover; border-radius: 6px; border: 1px solid var(--border); opacity: .75; }}

/* chat page */
.chat-top-spacing {{ margin-top: -42px; }}
[data-testid="stChatMessage"] {{ background: transparent !important; padding: 6px 0 !important; }}
[data-testid="stChatMessageContent"] {{
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: 14px !important;
  padding: 13px 16px !important;
  box-shadow: var(--shadow-sm) !important;
}}
[data-testid="stChatMessageContent"] p, [data-testid="stChatMessageContent"] li {{
  color: var(--text) !important;
  font-size: .875rem !important;
  line-height: 1.75 !important;
}}
.stChatInputContainer {{ background: var(--bg) !important; border-top: 1px solid var(--border) !important; padding-top: 14px !important; }}
[data-testid="stChatInput"] textarea {{
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: 14px !important;
  color: var(--text) !important;
}}
.attach-card {{
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 10px 12px;
  margin: 12px 0 10px;
}}
.attach-card p {{ margin: 0 0 8px !important; font-size: .72rem !important; letter-spacing: .1em !important; text-transform: uppercase !important; color: var(--text-muted) !important; font-weight: 600 !important; }}
.footer-note {{ display: none; }}

@media(max-width: 600px) {{
  .block-container {{ padding: 0 16px 28px !important; }}
  .topbar-wrap {{ margin-bottom: 44px; }}
  .landing-headline {{ font-size: 2rem !important; }}
}}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

@st.cache_resource
def get_model():
    api_key = None
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        pass
    api_key = api_key or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        st.error("GEMINI_API_KEY not found. Add it in Streamlit Cloud secrets.")
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

def open_image(uploaded_file):
    if uploaded_file is None:
        return None
    img = Image.open(uploaded_file)
    return img.copy()

def theme_button(key):
    if st.button(C["theme_label"], key=key, type="secondary", use_container_width=True):
        st.session_state["theme"] = C["next_theme"]
        st.rerun()

def render_topbar(show_new_chat=False):
    left, right = st.columns([5, 2], vertical_alignment="center")
    with left:
        st.markdown('<div class="topbar-logo">Chart Explainer</div>', unsafe_allow_html=True)
    with right:
        if show_new_chat:
            b1, b2 = st.columns([1, 1])
            with b1:
                st.markdown('<div class="topbar-button">', unsafe_allow_html=True)
                if st.button("+ New chat", key="new_chat", type="secondary", use_container_width=True):
                    st.session_state["messages"] = []
                    st.session_state["pending_image"] = None
                    st.session_state["upload_key"] += 1
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            with b2:
                st.markdown('<div class="topbar-button">', unsafe_allow_html=True)
                theme_button("toggle_chat")
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="topbar-button">', unsafe_allow_html=True)
            theme_button("toggle_land")
            st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="topbar-wrap" style="height:0;margin-top:-1px;"></div>', unsafe_allow_html=True)

def sample_html():
    samples = [
        "bar_regional_sales.png",
        "line_revenue.png",
        "pie_market_share.png",
        "scatter_marketing.png",
        "heatmap_satisfaction.png",
    ]
    imgs = "".join([f'<img src="app/static/sample_charts/{s}" onerror="this.style.display=\'none\'">' for s in samples])
    return f'<div class="sample-row"><span style="color:var(--text-muted)!important;">Try a sample:</span>{imgs}</div>'

has_messages = bool(st.session_state["messages"])
render_topbar(show_new_chat=has_messages)

if not has_messages:
    st.markdown(
        """
<div class="landing-copy">
  <p class="landing-kicker">Hello! Let's get started —</p>
  <h1 class="landing-headline">Upload a chart to analyze</h1>
  <p class="landing-sub">I'll explain what it means in plain language.</p>
</div>
""",
        unsafe_allow_html=True,
    )

    mode = st.radio("mode", ["Single chart", "Compare two charts"], horizontal=True, label_visibility="collapsed")

    st.markdown('<div class="landing-card-start">', unsafe_allow_html=True)
    with st.form("start_form", clear_on_submit=True):
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        if mode == "Single chart":
            uploaded = st.file_uploader(
                "Drop or click to upload a chart",
                type=["png", "jpg", "jpeg", "webp"],
                label_visibility="collapsed",
                key="land_single",
            )
            uploaded2 = None
            if uploaded:
                st.markdown('<div class="preview-img">', unsafe_allow_html=True)
                st.image(open_image(uploaded), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            placeholder = "Any specific question? (optional — leave blank for a full analysis)"
        else:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown('<p class="label-small">Chart 1</p>', unsafe_allow_html=True)
                uploaded = st.file_uploader(
                    "Upload chart 1",
                    type=["png", "jpg", "jpeg", "webp"],
                    label_visibility="collapsed",
                    key="land_cmp1",
                )
                if uploaded:
                    st.image(open_image(uploaded), use_container_width=True)
            with col2:
                st.markdown('<p class="label-small">Chart 2</p>', unsafe_allow_html=True)
                uploaded2 = st.file_uploader(
                    "Upload chart 2",
                    type=["png", "jpg", "jpeg", "webp"],
                    label_visibility="collapsed",
                    key="land_cmp2",
                )
                if uploaded2:
                    st.image(open_image(uploaded2), use_container_width=True)
            placeholder = "Any specific question about the comparison? (optional)"
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="question-section">', unsafe_allow_html=True)
        msg_input = st.text_area("Message", placeholder=placeholder, height=60, label_visibility="collapsed")
        st.markdown('<div class="submit-row">', unsafe_allow_html=True)
        bottom_l, bottom_r = st.columns([3, 1])
        with bottom_l:
            st.markdown('<span class="char-hint">Press Enter to send</span>', unsafe_allow_html=True)
        with bottom_r:
            submitted = st.form_submit_button("Compare →" if mode == "Compare two charts" else "Analyze →", use_container_width=True)
        st.markdown('</div></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(sample_html(), unsafe_allow_html=True)

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
    st.markdown('<div class="chat-top-spacing"></div>', unsafe_allow_html=True)
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
        new_file = st.file_uploader(
            "Attach",
            type=["png", "jpg", "jpeg", "webp"],
            key=f"chat_upload_{st.session_state['upload_key']}",
            label_visibility="collapsed",
        )
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
