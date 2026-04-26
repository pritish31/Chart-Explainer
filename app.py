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

# ── Theme ──────────────────────────────────────────────────────────────────────
if "theme" not in st.session_state:
    st.session_state["theme"] = "light"
is_dark = st.session_state["theme"] == "dark"

if is_dark:
    C = {
        "bg":           "#111110",
        "surface":      "#1A1917",
        "surface2":     "#222120",
        "border":       "#2E2C28",
        "accent":       "#C9913A",
        "text":         "#EDE9E0",
        "text_sub":     "#7A7060",
        "text_muted":   "#4A4840",
        "btn_bg":       "#C9913A",
        "btn_text":     "#111110",
        "shadow_sm":    "0 1px 3px rgba(0,0,0,0.4)",
        "shadow_md":    "0 4px 16px rgba(0,0,0,0.5)",
        "toggle_label": "Light mode",
        "next_theme":   "light",
    }
else:
    C = {
        "bg":           "#F8F6F1",
        "surface":      "#FFFFFF",
        "surface2":     "#F0EDE5",
        "border":       "#E3DED3",
        "accent":       "#B8751A",
        "text":         "#1C1A16",
        "text_sub":     "#6B6355",
        "text_muted":   "#A8A090",
        "btn_bg":       "#1C1A16",
        "btn_text":     "#FFFFFF",
        "shadow_sm":    "0 1px 3px rgba(0,0,0,0.06)",
        "shadow_md":    "0 4px 16px rgba(0,0,0,0.08)",
        "toggle_label": "Dark mode",
        "next_theme":   "dark",
    }


def inject_css(C):
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Serif+Display&display=swap');

html, body, .stApp {{
    background-color: {C['bg']} !important;
    color: {C['text']} !important;
    font-family: 'DM Sans', sans-serif !important;
}}
.main .block-container {{
    max-width: 720px !important;
    margin: 0 auto !important;
    padding: 2rem 24px 6rem !important;
}}
[data-testid="stDecoration"],
footer {{ display:none !important; }}

/* ── Typography ── */
h1 {{
    font-family:'DM Serif Display',serif !important;
    font-size:2.4rem !important;
    line-height:1.15 !important;
    color:{C['text']} !important;
    margin:0 0 8px !important;
}}
p,li {{
    font-family:'DM Sans',sans-serif !important;
    color:{C['text']} !important;
    font-size:0.9rem !important;
    line-height:1.6 !important;
}}
strong,b {{ color:{C['accent']} !important; font-weight:600 !important; }}

/* Scrollbar */
::-webkit-scrollbar {{ width:5px; height:5px; }}
::-webkit-scrollbar-track {{ background:transparent; }}
::-webkit-scrollbar-thumb {{ background:{C['border']}; border-radius:99px; }}
::-webkit-scrollbar-thumb:hover {{ background:{C['accent']}; opacity:0.5; }}

/* ── Mode radio → segmented tabs ── */
[data-testid="stRadio"] > div {{
    display:flex;
    background:{C['surface2']} !important;
    border:1px solid {C['border']} !important;
    border-radius:10px !important;
    padding:3px !important;
    gap:2px !important;
}}
[data-testid="stRadio"] label {{
    flex:1;
    text-align:center;
    padding:9px 16px !important;
    border-radius:8px !important;
    font-size:0.85rem !important;
    font-weight:500 !important;
    cursor:pointer !important;
    color:{C['text_sub']} !important;
    border:none !important;
    background:transparent !important;
    font-family:'DM Sans',sans-serif !important;
    transition:all 0.2s !important;
}}
[data-testid="stRadio"] label:has(input:checked) {{
    background:{C['surface']} !important;
    color:{C['text']} !important;
    box-shadow:{C['shadow_sm']} !important;
}}
[data-testid="stRadio"] label span {{ color:inherit !important; }}
[data-testid="stRadio"] [data-testid="stMarkdownContainer"] p {{
    color:inherit !important; font-size:inherit !important;
}}

/* ── Landing card (form) ── */
[data-testid="stForm"] {{
    background:{C['surface']} !important;
    border:1px solid {C['border']} !important;
    border-radius:18px !important;
    padding:24px !important;
    box-shadow:{C['shadow_md']} !important;
}}
[data-testid="stForm"] > div {{ gap:0 !important; }}

/* Textarea inside form */
[data-testid="stForm"] textarea {{
    background:transparent !important;
    border:none !important;
    border-top:1px solid {C['border']} !important;
    border-radius:0 !important;
    color:{C['text']} !important;
    font-family:'DM Sans',sans-serif !important;
    font-size:0.875rem !important;
    padding:14px 4px !important;
    resize:none !important;
    box-shadow:none !important;
}}
[data-testid="stForm"] textarea:focus {{
    border-top-color:{C['accent']} !important;
    box-shadow:none !important;
}}
[data-testid="stForm"] textarea::placeholder {{ color:{C['text_muted']} !important; }}

/* File uploader inside form */
[data-testid="stForm"] [data-testid="stFileUploader"] > div:first-child {{
    background:transparent !important; border:none !important;
}}
[data-testid="stForm"] [data-testid="stFileUploaderDropzone"] {{
    background:{C['surface']} !important;
    border:1.5px dashed {C['border']} !important;
    border-radius:14px !important;
    padding:28px 20px !important;
    text-align:center !important;
    transition:all 0.2s !important;
}}
[data-testid="stForm"] [data-testid="stFileUploaderDropzone"]:hover {{
    border-color:{C['accent']} !important;
}}
[data-testid="stForm"] [data-testid="stFileUploaderDropzoneInstructions"] p,
[data-testid="stForm"] [data-testid="stFileUploaderDropzoneInstructions"] small {{
    color:{C['text_muted']} !important; font-size:0.8rem !important;
}}
[data-testid="stForm"] [data-testid="stFileUploaderDropzone"] button {{
    background:{C['surface']} !important;
    color:{C['text_muted']} !important;
    border:1px solid {C['border']} !important;
    border-radius:4px !important;
    font-size:0.76rem !important;
}}
[data-testid="stForm"] [data-testid="stFileUploaderDropzone"] button:hover {{
    border-color:{C['accent']} !important;
    color:{C['accent']} !important;
}}

/* ── Buttons ── */
.stButton > button[kind="primary"] {{
    background-color:{C['btn_bg']} !important;
    color:{C['btn_text']} !important;
    border:none !important;
    border-radius:8px !important;
    font-family:'DM Sans',sans-serif !important;
    font-weight:600 !important;
    font-size:0.875rem !important;
    padding:11px 22px !important;
    transition:all 0.2s !important;
    box-shadow:{C['shadow_sm']} !important;
}}
.stButton > button[kind="primary"]:hover {{
    opacity:0.88 !important;
    transform:translateY(-1px) !important;
    box-shadow:{C['shadow_md']} !important;
}}
.stButton > button[kind="primary"] p,
.stButton > button[kind="primary"] span {{
    color:{C['btn_text']} !important; font-size:inherit !important;
}}
.stButton > button[kind="secondary"] {{
    background:transparent !important;
    color:{C['text_sub']} !important;
    border:1px solid {C['border']} !important;
    border-radius:8px !important;
    font-family:'DM Sans',sans-serif !important;
    font-size:0.8rem !important;
    padding:7px 14px !important;
    transition:all 0.2s !important;
}}
.stButton > button[kind="secondary"]:hover {{
    border-color:{C['accent']} !important;
    color:{C['accent']} !important;
}}
.stButton > button[kind="secondary"] p,
.stButton > button[kind="secondary"] span {{ color:inherit !important; font-size:inherit !important; }}

/* Form submit button */
[data-testid="stFormSubmitButton"] > button {{
    background-color:{C['btn_bg']} !important;
    color:{C['btn_text']} !important;
    border:none !important;
    border-radius:8px !important;
    font-family:'DM Sans',sans-serif !important;
    font-weight:600 !important;
    font-size:0.875rem !important;
    padding:11px 22px !important;
    box-shadow:{C['shadow_sm']} !important;
}}
[data-testid="stFormSubmitButton"] > button p,
[data-testid="stFormSubmitButton"] > button span {{ color:{C['btn_text']} !important; }}
[data-testid="stFormSubmitButton"] > button:hover {{ opacity:0.88 !important; }}

/* ── Chat messages ── */
[data-testid="stChatMessage"] {{
    background:transparent !important;
    border:none !important;
    padding:6px 0 !important;
}}
[data-testid="stChatMessageContent"] p {{
    font-size:0.875rem !important;
    line-height:1.75 !important;
    color:{C['text']} !important;
}}

/* ── Chat input ── */
.stChatInputContainer {{
    background:{C['bg']} !important;
    border-top:1px solid {C['border']} !important;
    padding-top:14px !important;
}}
[data-testid="stChatInput"] textarea {{
    background:{C['surface']} !important;
    color:{C['text']} !important;
    border:1px solid {C['border']} !important;
    border-radius:14px !important;
    font-family:'DM Sans',sans-serif !important;
    font-size:0.875rem !important;
}}
[data-testid="stChatInput"] textarea:focus {{
    border-color:{C['accent']} !important;
    box-shadow:0 0 0 2px {C['accent']}22 !important;
}}
[data-testid="stChatInput"] textarea::placeholder {{ color:{C['text_muted']} !important; }}

/* ── Compact attach uploader (chat view) ── */
.attach-area [data-testid="stFileUploader"] > div:first-child {{
    background:transparent !important; border:none !important;
}}
.attach-area [data-testid="stFileUploaderDropzone"] {{
    background:{C['surface']} !important;
    border:1px dashed {C['border']} !important;
    border-radius:8px !important;
    padding:8px 14px !important;
}}
.attach-area [data-testid="stFileUploaderDropzoneInstructions"] p,
.attach-area [data-testid="stFileUploaderDropzoneInstructions"] small {{
    color:{C['text_muted']} !important; font-size:0.76rem !important;
}}
.attach-area [data-testid="stFileUploaderDropzone"] button {{
    background:{C['surface']} !important;
    color:{C['text_muted']} !important;
    border:1px solid {C['border']} !important;
    border-radius:4px !important;
    font-size:0.74rem !important;
}}
.attach-area [data-testid="stFileUploaderDropzone"] button:hover {{
    border-color:{C['accent']} !important;
    color:{C['accent']} !important;
}}

/* ── Misc ── */
hr {{ border:none !important; border-top:1px solid {C['border']} !important; margin:1.5rem 0 !important; }}
.stCaption p {{ color:{C['text_muted']} !important; font-size:0.74rem !important; }}
[data-testid="stImage"] img {{ border-radius:8px !important; border:1px solid {C['border']} !important; }}
.stSpinner > div > div {{ border-top-color:{C['accent']} !important; }}
</style>
""", unsafe_allow_html=True)


inject_css(C)


# ── Gemini ─────────────────────────────────────────────────────────────────────
@st.cache_resource
def get_model():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        st.error("GEMINI_API_KEY not found. Run: export GEMINI_API_KEY='your-key'")
        st.stop()
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.5-flash")


DOMAIN_RESTRICTION = """STRICT RULE: You are exclusively a chart and data visualization analysis assistant. If the user's message is unrelated to the chart, its data, or data analysis in general, do not answer it. Instead respond only with: "I'm designed specifically for chart and data visualization analysis and can only assist with related questions." Apply this rule before answering anything.

"""

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
        prompt = DOMAIN_RESTRICTION + COMPARISON_PROMPT
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
        prompt = DOMAIN_RESTRICTION + ANALYSIS_PROMPT
        if message and message not in ("Analyze this chart.", ""):
            prompt += f"\n\nAlso specifically address: {message}"
        return model.generate_content([prompt, image]).text

    # Conversational follow-up
    parts = [
        DOMAIN_RESTRICTION +
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

    # Topbar
    bar_l, bar_r = st.columns([8, 2])
    with bar_l:
        st.markdown(
            f"<p style='font-family:\"DM Serif Display\",serif;font-size:1rem;"
            f"letter-spacing:0.02em;color:{C['text']};padding:20px 0 16px;"
            f"border-bottom:1px solid {C['border']}'>"
            f"Chart Explainer</p>",
            unsafe_allow_html=True,
        )
    with bar_r:
        st.markdown(f"<div style='padding:14px 0 10px;border-bottom:1px solid {C['border']}'>&nbsp;</div>", unsafe_allow_html=True)
        if st.button(C["toggle_label"], key="toggle_land"):
            st.session_state["theme"] = C["next_theme"]
            st.rerun()

    st.markdown("<div style='height:10vh'></div>", unsafe_allow_html=True)

    # Center column
    _, center, _ = st.columns([1, 5, 1])
    with center:

        st.markdown(
            f"<p style='font-family:\"DM Sans\",sans-serif;font-size:0.95rem;"
            f"color:{C['text_sub']};margin:0 0 6px;text-align:center'>"
            f"Hello! Let&#39;s get started &mdash;</p>"
            f"<h1 style='text-align:center'>Upload a chart to analyze</h1>"
            f"<p style='font-size:1rem;color:{C['text_sub']};text-align:center;"
            f"margin:8px 0 36px'>I&#39;ll explain what it means in plain language.</p>",
            unsafe_allow_html=True,
        )

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
                placeholder = "Any specific question? (optional — leave blank for a full analysis)"

            else:
                uc1, uc2 = st.columns(2)
                with uc1:
                    st.markdown(
                        f"<p style='font-size:0.72rem;letter-spacing:0.1em;text-transform:uppercase;"
                        f"color:{C['text_muted']};margin-bottom:6px;font-weight:600'>Chart 1</p>",
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
                        f"color:{C['text_muted']};margin-bottom:6px;font-weight:600'>Chart 2</p>",
                        unsafe_allow_html=True,
                    )
                    uploaded2 = st.file_uploader(
                        "Chart 2", type=["png", "jpg", "jpeg", "webp"],
                        label_visibility="collapsed", key="land_cmp2",
                    )
                    if uploaded2:
                        st.image(Image.open(uploaded2), use_container_width=True)
                placeholder = "Any specific question about the comparison? (optional)"

            msg_input = st.text_area(
                "Message",
                placeholder=placeholder,
                height=80,
                label_visibility="collapsed",
            )

            hint_col, btn_col = st.columns([4, 1])
            with hint_col:
                st.markdown(
                    f"<p style='font-size:0.75rem;color:{C['text_muted']};padding-top:4px'>"
                    f"Press Enter to send</p>",
                    unsafe_allow_html=True,
                )
            with btn_col:
                btn_label = "Compare →" if mode == "Compare Two Charts" else "Analyze →"
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
            f"<p style='font-family:\"DM Serif Display\",serif;font-size:1rem;"
            f"letter-spacing:0.02em;color:{C['text']};margin:14px 0 0'>"
            f"Chart Explainer</p>",
            unsafe_allow_html=True,
        )
    with bar_r:
        rc1, rc2 = st.columns(2)
        with rc1:
            if st.button("+ New chat", key="new_chat"):
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
        f"color:{C['text_muted']};margin-bottom:6px;font-family:\"DM Sans\",sans-serif;"
        f"font-weight:600'>Attach a new chart (optional)</p>",
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
    f"letter-spacing:0.1em;font-family:\"DM Sans\",sans-serif;margin-top:2rem'>"
    f"GEMINI 2.5 FLASH &nbsp;&middot;&nbsp; FREE TIER: 1,500 REQUESTS / DAY</p>",
    unsafe_allow_html=True,
)
