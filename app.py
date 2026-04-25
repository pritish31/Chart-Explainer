import streamlit as st
import google.generativeai as genai
import os
from PIL import Image
from typing import Optional, List

st.set_page_config(
    page_title="Chart Explainer AI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Theme ──────────────────────────────────────────────────────────────────────
if "theme" not in st.session_state:
    st.session_state["theme"] = "dark"
is_dark = st.session_state["theme"] == "dark"

if is_dark:
    C = {
        "bg":             "#0d0d0d",
        "surface":        "#171717",
        "surface2":       "#202020",
        "border":         "#2c2c2c",
        "accent":         "#c9a84c",
        "accent_dim":     "#6b5520",
        "text":           "#edeae3",
        "text_sub":       "#7a7060",
        "text_muted":     "#4a4035",
        "btn_bg":         "#c9a84c",
        "btn_text":       "#0d0d0d",
        "btn_hover":      "#dab95e",
        "chip_bg":        "#1a1a1a",
        "chip_border":    "#2c2c2c",
        "chip_text":      "#7a7060",
        "shadow":         "0 8px 48px rgba(0,0,0,0.9)",
        "toggle_label":   "Day",
        "next_theme":     "light",
        "top_bar":        "linear-gradient(90deg,#c9a84c,#7a6330 50%,transparent)",
    }
else:
    C = {
        "bg":             "#f5f3ee",
        "surface":        "#ffffff",
        "surface2":       "#edeae2",
        "border":         "#dedad0",
        "accent":         "#7c3a00",
        "accent_dim":     "#c9a84c",
        "text":           "#1a1a1a",
        "text_sub":       "#6b6355",
        "text_muted":     "#9a9080",
        "btn_bg":         "#1a1a1a",
        "btn_text":       "#ffffff",
        "btn_hover":      "#333333",
        "chip_bg":        "#ffffff",
        "chip_border":    "#dedad0",
        "chip_text":      "#6b6355",
        "shadow":         "0 4px 24px rgba(0,0,0,0.10)",
        "toggle_label":   "Night",
        "next_theme":     "dark",
        "top_bar":        "linear-gradient(90deg,#7c3a00,#c9a84c 50%,transparent)",
    }


def inject_css(C):
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Inter:wght@300;400;500;600&display=swap');

html, body, .stApp {{
    background-color: {C['bg']} !important;
    color: {C['text']} !important;
    font-family: 'Inter', sans-serif !important;
}}
.main .block-container {{
    max-width: 820px !important;
    margin: 0 auto !important;
    padding: 2rem 2rem 6rem !important;
}}
[data-testid="stDecoration"],
footer {{ display:none !important; }}

/* top accent bar */
.top-bar {{
    position:fixed;top:0;left:0;right:0;height:2px;
    background:{C['top_bar']};z-index:9999;pointer-events:none;
}}

/* ── Typography ── */
h1 {{
    font-family:'Cinzel',serif !important;font-weight:700 !important;
    letter-spacing:0.06em !important;font-size:2rem !important;
    color:{C['text']} !important;margin:0 !important;line-height:1.25 !important;
}}
p,li {{
    font-family:'Inter',sans-serif !important;
    color:{C['text']} !important;font-size:0.9rem !important;line-height:1.8 !important;
}}
strong,b {{ color:{C['accent']} !important;font-weight:600 !important; }}

/* ── App-bar (chat page) ── */
.app-bar {{
    display:flex;align-items:center;justify-content:space-between;
    padding:14px 0 10px;
    border-bottom:1px solid {C['border']};
    margin-bottom:1.5rem;
}}
.app-bar-logo {{
    font-family:'Cinzel',serif;font-size:0.9rem;
    letter-spacing:0.18em;text-transform:uppercase;color:{C['text']};
}}

/* ── Landing input card ── */
[data-testid="stForm"] {{
    background:{C['surface']} !important;
    border:1px solid {C['border']} !important;
    border-radius:16px !important;
    padding:20px 24px !important;
}}
[data-testid="stForm"] > div {{ gap:0 !important; }}

/* text area inside form ── remove default border, transparent bg */
[data-testid="stForm"] textarea {{
    background:transparent !important;
    border:none !important;
    border-top:1px solid {C['border']} !important;
    border-radius:0 !important;
    color:{C['text']} !important;
    font-family:'Inter',sans-serif !important;
    font-size:0.95rem !important;
    padding:14px 4px !important;
    resize:none !important;
    box-shadow:none !important;
}}
[data-testid="stForm"] textarea:focus {{
    border-top-color:{C['accent']} !important;
    box-shadow:none !important;
}}
[data-testid="stForm"] textarea::placeholder {{ color:{C['text_muted']} !important; }}

/* file uploader inside form ── minimal */
[data-testid="stForm"] [data-testid="stFileUploader"] > div:first-child {{
    background:transparent !important;border:none !important;
}}
[data-testid="stForm"] [data-testid="stFileUploaderDropzone"] {{
    background:{C['surface2']} !important;border:1px dashed {C['border']} !important;
    border-radius:8px !important;padding:10px 16px !important;
}}
[data-testid="stForm"] [data-testid="stFileUploaderDropzoneInstructions"] p,
[data-testid="stForm"] [data-testid="stFileUploaderDropzoneInstructions"] small {{
    color:{C['text_muted']} !important;font-size:0.8rem !important;
}}
[data-testid="stForm"] [data-testid="stFileUploaderDropzone"] button {{
    background:{C['surface']} !important;color:{C['text_muted']} !important;
    border:1px solid {C['border']} !important;border-radius:4px !important;
    font-size:0.76rem !important;
}}
[data-testid="stForm"] [data-testid="stFileUploaderDropzone"] button:hover {{
    border-color:{C['accent']} !important;color:{C['accent']} !important;
}}

/* ── Buttons ── */
.stButton > button[kind="primary"] {{
    background-color:{C['btn_bg']} !important;color:{C['btn_text']} !important;
    border:none !important;border-radius:8px !important;
    font-family:'Inter',sans-serif !important;font-weight:600 !important;
    font-size:0.82rem !important;letter-spacing:0.08em !important;
    padding:12px 22px !important;transition:all 0.2s !important;
}}
.stButton > button[kind="primary"]:hover {{
    background-color:{C['btn_hover']} !important;transform:translateY(-1px) !important;
}}
.stButton > button[kind="primary"] p,
.stButton > button[kind="primary"] span {{
    color:{C['btn_text']} !important;font-size:inherit !important;
}}
.stButton > button[kind="secondary"] {{
    background:transparent !important;color:{C['text_sub']} !important;
    border:1px solid {C['border']} !important;border-radius:8px !important;
    font-family:'Inter',sans-serif !important;font-size:0.78rem !important;
    letter-spacing:0.06em !important;padding:8px 16px !important;transition:all 0.2s !important;
}}
.stButton > button[kind="secondary"]:hover {{
    border-color:{C['accent']} !important;color:{C['accent']} !important;
}}
.stButton > button[kind="secondary"] p,
.stButton > button[kind="secondary"] span {{ color:inherit !important;font-size:inherit !important; }}

/* submit button inside form */
[data-testid="stForm"] .stButton > button {{
    border-radius:8px !important;
}}
[data-testid="stFormSubmitButton"] > button {{
    background-color:{C['btn_bg']} !important;color:{C['btn_text']} !important;
    border:none !important;border-radius:8px !important;
    font-family:'Inter',sans-serif !important;font-weight:600 !important;
    font-size:0.82rem !important;padding:12px 22px !important;
}}
[data-testid="stFormSubmitButton"] > button p,
[data-testid="stFormSubmitButton"] > button span {{ color:{C['btn_text']} !important; }}
[data-testid="stFormSubmitButton"] > button:hover {{
    background-color:{C['btn_hover']} !important;
}}

/* ── Suggestion chips ── */
.chip-btn > button {{
    background:{C['chip_bg']} !important;color:{C['chip_text']} !important;
    border:1px solid {C['chip_border']} !important;border-radius:24px !important;
    font-size:0.78rem !important;padding:8px 16px !important;letter-spacing:0.03em !important;
    transition:all 0.2s !important;
}}
.chip-btn > button:hover {{
    border-color:{C['accent']} !important;color:{C['accent']} !important;background:{C['surface']} !important;
}}
.chip-btn > button p,.chip-btn > button span {{ color:inherit !important;font-size:inherit !important; }}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {{
    background:transparent !important;border:none !important;padding:6px 0 !important;
}}
[data-testid="stChatMessageContent"] p {{
    font-size:0.9rem !important;line-height:1.8 !important;color:{C['text']} !important;
}}

/* ── Chat input (bottom) ── */
.stChatInputContainer {{
    background:{C['bg']} !important;border-top:1px solid {C['border']} !important;
    padding-top:12px !important;
}}
[data-testid="stChatInput"] textarea {{
    background:{C['surface']} !important;color:{C['text']} !important;
    border:1px solid {C['border']} !important;border-radius:12px !important;
    font-family:'Inter',sans-serif !important;font-size:0.9rem !important;
}}
[data-testid="stChatInput"] textarea:focus {{
    border-color:{C['accent']} !important;
    box-shadow:0 0 0 2px {C['accent_dim']}33 !important;
}}
[data-testid="stChatInput"] textarea::placeholder {{ color:{C['text_muted']} !important; }}

/* ── Compact attach uploader (chat view) ── */
.attach-area [data-testid="stFileUploader"] > div:first-child {{
    background:transparent !important;border:none !important;
}}
.attach-area [data-testid="stFileUploaderDropzone"] {{
    background:{C['surface']} !important;border:1px dashed {C['border']} !important;
    border-radius:8px !important;padding:8px 14px !important;
}}
.attach-area [data-testid="stFileUploaderDropzoneInstructions"] p,
.attach-area [data-testid="stFileUploaderDropzoneInstructions"] small {{
    color:{C['text_muted']} !important;font-size:0.76rem !important;
}}
.attach-area [data-testid="stFileUploaderDropzone"] button {{
    background:{C['surface']} !important;color:{C['text_muted']} !important;
    border:1px solid {C['border']} !important;border-radius:4px !important;font-size:0.74rem !important;
}}
.attach-area [data-testid="stFileUploaderDropzone"] button:hover {{
    border-color:{C['accent']} !important;color:{C['accent']} !important;
}}

/* ── Mode radio (segmented control look) ── */
[data-testid="stRadio"] > div {{
    display:flex;gap:8px;
}}
[data-testid="stRadio"] label {{
    background:{C['surface']} !important;
    border:1px solid {C['border']} !important;
    border-radius:8px !important;
    padding:8px 20px !important;
    font-family:'Inter',sans-serif !important;
    font-size:0.8rem !important;
    letter-spacing:0.06em !important;
    color:{C['text_sub']} !important;
    cursor:pointer !important;
    transition:all 0.2s !important;
}}
[data-testid="stRadio"] label:has(input:checked) {{
    background:{C['btn_bg']} !important;
    border-color:{C['btn_bg']} !important;
    color:{C['btn_text']} !important;
}}
[data-testid="stRadio"] label span {{ color:inherit !important; }}
[data-testid="stRadio"] [data-testid="stMarkdownContainer"] p {{
    color:inherit !important;font-size:inherit !important;
}}

/* ── Misc ── */
hr {{ border:none !important;border-top:1px solid {C['border']} !important;margin:1.5rem 0 !important; }}
.stCaption p {{ color:{C['text_muted']} !important;font-size:0.74rem !important; }}
[data-testid="stImage"] img {{ border-radius:8px !important;border:1px solid {C['border']} !important; }}
.stSpinner > div > div {{ border-top-color:{C['accent']} !important; }}
::-webkit-scrollbar {{ width:5px;height:5px; }}
::-webkit-scrollbar-track {{ background:{C['bg']}; }}
::-webkit-scrollbar-thumb {{ background:{C['border']};border-radius:3px; }}
::-webkit-scrollbar-thumb:hover {{ background:{C['accent_dim']}; }}
</style>
""", unsafe_allow_html=True)


inject_css(C)
st.markdown('<div class="top-bar"></div>', unsafe_allow_html=True)


# ── Gemini ─────────────────────────────────────────────────────────────────────
@st.cache_resource
def get_model():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        st.error("GEMINI_API_KEY not found. Run: export GEMINI_API_KEY='your-key'")
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


def generate_response(
    message: str,
    image: Optional[Image.Image],
    history: List[dict],
    image2: Optional[Image.Image] = None,
) -> str:
    model = get_model()

    # ── Compare mode (two images) ──
    if image and image2:
        prompt = COMPARISON_PROMPT
        if message and message not in ("Compare these charts.", ""):
            prompt += f"\n\nAlso specifically address: {message}"
        return model.generate_content(["Chart 1:", image, "Chart 2:", image2, prompt]).text

    # Find context image from history if none provided
    ctx_image = image
    if ctx_image is None:
        for msg in reversed(history):
            if msg.get("image"):
                ctx_image = msg["image"]
                break

    # First analysis of a new single image → structured format
    is_first = image is not None and not any(m["role"] == "assistant" for m in history)
    if is_first:
        prompt = ANALYSIS_PROMPT
        if message and message not in ("Analyze this chart.", ""):
            prompt += f"\n\nAlso specifically address: {message}"
        return model.generate_content([prompt, image]).text

    # Conversational follow-up
    parts = [
        "You are an expert data analyst. Answer the user's questions about this chart concisely "
        "and specifically, referencing values or patterns visible in the chart."
    ]
    if ctx_image:
        parts.append(ctx_image)
    for msg in history:
        parts.append(f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}")
    parts.append(f"User: {message}")
    return model.generate_content(parts).text


# ── State ──────────────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "upload_key" not in st.session_state:
    st.session_state["upload_key"] = 0
if "pending_image" not in st.session_state:
    st.session_state["pending_image"] = None

has_messages = bool(st.session_state["messages"])


# ══════════════════════════════════════════════════════════════════════════════
#  LANDING PAGE
# ══════════════════════════════════════════════════════════════════════════════
if not has_messages:

    # Theme toggle top-right
    _, toggle_col = st.columns([10, 1])
    with toggle_col:
        if st.button(C["toggle_label"], key="toggle_land"):
            st.session_state["theme"] = C["next_theme"]
            st.rerun()

    # Vertical spacer
    st.markdown("<div style='height:14vh'></div>", unsafe_allow_html=True)

    # Center column
    _, center, _ = st.columns([1, 5, 1])
    with center:

        # Greeting
        st.markdown(
            f"<p style='font-family:Inter,sans-serif;font-size:1.05rem;color:{C['text_sub']};"
            f"margin:0 0 6px 2px'>Hi there,</p>"
            f"<h1>Where should we start?</h1>",
            unsafe_allow_html=True,
        )
        st.markdown("<div style='height:1.75rem'></div>", unsafe_allow_html=True)

        # ── Mode selector ──────────────────────────────────────────────────
        mode = st.radio(
            "mode",
            ["Single Chart", "Compare Two Charts"],
            horizontal=True,
            label_visibility="collapsed",
        )
        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

        # ── Input card (form) ──────────────────────────────────────────────
        with st.form("start_form", clear_on_submit=True):

            if mode == "Single Chart":
                uploaded = st.file_uploader(
                    "Attach a chart",
                    type=["png", "jpg", "jpeg", "webp"],
                    label_visibility="collapsed",
                    key="land_single",
                )
                uploaded2 = None
                if uploaded:
                    st.image(Image.open(uploaded), width=140)
                placeholder = "Ask about your chart, or describe what to analyze…"

            else:
                uc1, uc2 = st.columns(2)
                with uc1:
                    st.markdown(
                        f"<p style='font-size:0.72rem;letter-spacing:0.1em;text-transform:uppercase;"
                        f"color:{C['text_muted']};margin-bottom:6px'>Chart 1</p>",
                        unsafe_allow_html=True,
                    )
                    uploaded = st.file_uploader(
                        "Chart 1", type=["png", "jpg", "jpeg", "webp"],
                        label_visibility="collapsed", key="land_cmp1",
                    )
                    if uploaded:
                        st.image(Image.open(uploaded), use_container_width=True)
                with uc2:
                    st.markdown(
                        f"<p style='font-size:0.72rem;letter-spacing:0.1em;text-transform:uppercase;"
                        f"color:{C['text_muted']};margin-bottom:6px'>Chart 2</p>",
                        unsafe_allow_html=True,
                    )
                    uploaded2 = st.file_uploader(
                        "Chart 2", type=["png", "jpg", "jpeg", "webp"],
                        label_visibility="collapsed", key="land_cmp2",
                    )
                    if uploaded2:
                        st.image(Image.open(uploaded2), use_container_width=True)
                placeholder = "Ask a specific question about the comparison, or leave blank for a full analysis…"

            msg_input = st.text_area(
                "Message",
                placeholder=placeholder,
                height=80,
                label_visibility="collapsed",
            )

            _, btn_col = st.columns([4, 1])
            with btn_col:
                btn_label = "Compare →" if mode == "Compare Two Charts" else "Send →"
                submitted = st.form_submit_button(btn_label, use_container_width=True)

        if submitted:
            img1 = Image.open(uploaded) if uploaded else None
            img2 = Image.open(uploaded2) if uploaded2 else None

            if mode == "Compare Two Charts" and (not img1 or not img2):
                st.warning("Please upload both charts to compare.")
            elif mode == "Single Chart" and not img1 and not msg_input.strip():
                st.warning("Upload a chart or type a message to get started.")
            else:
                message = msg_input.strip() or (
                    "Compare these charts." if mode == "Compare Two Charts" else "Analyze this chart."
                )
                st.session_state["messages"].append(
                    {"role": "user", "content": message, "image": img1, "image2": img2}
                )
                with st.spinner("Analyzing…"):
                    response = generate_response(message, img1, [], image2=img2)
                st.session_state["messages"].append(
                    {"role": "assistant", "content": response, "image": None, "image2": None}
                )
                st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
#  CHAT PAGE
# ══════════════════════════════════════════════════════════════════════════════
else:

    # App bar
    bar_l, bar_r = st.columns([5, 2])
    with bar_l:
        st.markdown(
            f"<p style='font-family:Cinzel,serif;font-size:0.9rem;letter-spacing:0.18em;"
            f"text-transform:uppercase;color:{C['text']};margin:14px 0 0'>Chart Explainer AI</p>",
            unsafe_allow_html=True,
        )
    with bar_r:
        rc1, rc2 = st.columns(2)
        with rc1:
            if st.button("+ New Chat", key="new_chat"):
                st.session_state["messages"] = []
                st.session_state["pending_image"] = None
                st.session_state["upload_key"] += 1
                st.rerun()
        with rc2:
            if st.button(C["toggle_label"], key="toggle_chat"):
                st.session_state["theme"] = C["next_theme"]
                st.rerun()

    st.markdown(
        f"<div style='border-top:1px solid {C['border']};margin:0.5rem 0 1.5rem'></div>",
        unsafe_allow_html=True,
    )

    # ── Conversation history ───────────────────────────────────────────────
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            if msg.get("image") and msg.get("image2"):
                ic1, ic2 = st.columns(2)
                with ic1:
                    st.image(msg["image"], use_container_width=True)
                with ic2:
                    st.image(msg["image2"], use_container_width=True)
            elif msg.get("image"):
                st.image(msg["image"], width=300)
            st.markdown(msg["content"])

    # ── Attach new chart (compact, above chat input) ───────────────────────
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='font-size:0.72rem;letter-spacing:0.1em;text-transform:uppercase;"
        f"color:{C['text_muted']};margin-bottom:6px;font-family:Inter,sans-serif'>"
        f"📎  Attach a new chart (optional)</p>",
        unsafe_allow_html=True,
    )
    st.markdown('<div class="attach-area">', unsafe_allow_html=True)
    attach_left, attach_right = st.columns([3, 2])
    with attach_left:
        new_file = st.file_uploader(
            "Attach",
            type=["png", "jpg", "jpeg", "webp"],
            key=f"chat_upload_{st.session_state['upload_key']}",
            label_visibility="collapsed",
        )
    if new_file:
        st.session_state["pending_image"] = Image.open(new_file)
        with attach_right:
            st.image(st.session_state["pending_image"], width=90)
    elif not new_file:
        st.session_state["pending_image"] = None
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Chat input ─────────────────────────────────────────────────────────
    if prompt := st.chat_input("Ask a follow-up question…"):
        current_img = st.session_state.get("pending_image")
        history = list(st.session_state["messages"])

        st.session_state["messages"].append(
            {"role": "user", "content": prompt, "image": current_img}
        )

        with st.chat_message("user"):
            if current_img:
                st.image(current_img, width=300)
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                response = generate_response(prompt, current_img, history)
            st.markdown(response)

        st.session_state["messages"].append(
            {"role": "assistant", "content": response, "image": None}
        )

        if current_img:
            st.session_state["pending_image"] = None
            st.session_state["upload_key"] += 1


# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown(
    f"<p style='text-align:center;font-size:0.68rem;color:{C['text_muted']};"
    f"letter-spacing:0.1em;font-family:Inter,sans-serif;margin-top:2rem'>"
    f"GEMINI 2.5 FLASH  ·  FREE TIER: 1,500 REQUESTS / DAY</p>",
    unsafe_allow_html=True,
)