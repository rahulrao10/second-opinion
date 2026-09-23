import streamlit as st
import tempfile
import os
from datetime import datetime

from ocr_engine import extract_text
from llm_engine import explain_document

st.set_page_config(
    page_title="Second Opinion",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# STYLE SYSTEM — dark blue / black / grey
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,500;8..60,600&family=IBM+Plex+Sans:wght@400;500;600&display=swap');

:root {
    --bg: #0C1116;
    --surface: #151B22;
    --surface-2: #1B222B;
    --ink: #E7EAEE;
    --ink-muted: #8B96A3;
    --accent: #5B9BFF;
    --accent-dim: #2E466E;
    --amber: #D99A5B;
    --line: #262E38;
    --sidebar-bg: #090D12;
}

html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; color: var(--ink); }
.stApp { background: var(--bg); }
#MainMenu, footer, header { visibility: hidden; }

/* ---- Sidebar ---- */
[data-testid="stSidebar"] {
    background: var(--sidebar-bg);
    border-right: 1px solid var(--line);
}
[data-testid="stSidebar"] * { color: var(--ink); }
[data-testid="stSidebar"] .so-wordmark {
    font-family: 'Source Serif 4', serif;
    font-weight: 600;
    font-size: 1.5rem;
    color: #FFFFFF;
    margin-bottom: 0.2rem;
}
[data-testid="stSidebar"] .so-wordmark span { color: var(--accent); font-style: italic; font-weight: 500; }
[data-testid="stSidebar"] .so-badge {
    display: inline-flex; align-items: center; gap: 0.4rem;
    background: var(--surface);
    border: 1px solid var(--line);
    padding: 0.25rem 0.65rem; border-radius: 999px;
    font-size: 0.72rem; margin-bottom: 1.6rem; color: var(--ink-muted);
}
[data-testid="stSidebar"] .so-badge::before {
    content: ""; width: 6px; height: 6px; border-radius: 50%;
    background: #4ADE80; display: inline-block;
}
[data-testid="stSidebar"] .so-section-label {
    font-size: 0.72rem; letter-spacing: 0.03em;
    color: var(--ink-muted); margin: 1.4rem 0 0.5rem 0;
    text-transform: uppercase;
}
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
    background: var(--surface);
    border: 1px dashed var(--line);
    border-radius: 8px;
}
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] small,
[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] span { color: var(--ink-muted) !important; }
[data-testid="stSidebar"] .stButton > button {
    background: var(--accent); color: #08111F; border: none;
    border-radius: 7px; font-weight: 600; width: 100%;
}
[data-testid="stSidebar"] .stButton > button:hover { background: #7CAEFF; color: #08111F; }
[data-testid="stSidebar"] [data-testid="stExpander"] {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 8px;
}

.so-doc-chip {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 8px;
    padding: 0.6rem 0.75rem;
    font-size: 0.82rem;
    margin-bottom: 0.5rem;
    line-height: 1.4;
}
.so-doc-chip .fname { font-weight: 500; color: #FFFFFF; }
.so-doc-chip .ftime { color: var(--ink-muted); font-size: 0.74rem; }

/* ---- Main chat column ---- */
.block-container {
    padding-top: 1.6rem;
    padding-bottom: 8rem;
    max-width: 780px;
    margin: 0 auto;
}

.so-hero { text-align: center; padding: 3rem 1rem 1.5rem 1rem; }
.so-hero-title {
    font-family: 'Source Serif 4', serif;
    font-size: 2rem; font-weight: 600;
    color: #FFFFFF; margin-bottom: 0.6rem;
}
.so-hero-sub {
    color: var(--ink-muted); font-size: 0.98rem;
    max-width: 480px; margin: 0 auto; line-height: 1.5;
}

.so-disclaimer {
    background: var(--surface);
    border-left: 3px solid var(--amber);
    padding: 0.7rem 1rem;
    font-size: 0.8rem;
    color: var(--ink);
    border-radius: 0 6px 6px 0;
    margin: 0 0 1.4rem 0;
    line-height: 1.5;
}

/* ---- Clickable suggestion chips (real buttons) ---- */
div[data-testid="column"] .stButton > button {
    background: var(--surface);
    color: var(--ink);
    border: 1px solid var(--line);
    border-radius: 999px;
    padding: 0.5rem 1rem;
    font-size: 0.83rem;
    font-weight: 400;
    width: 100%;
    white-space: normal;
}
div[data-testid="column"] .stButton > button:hover {
    border-color: var(--accent);
    color: #FFFFFF;
    background: var(--surface-2);
}

/* ---- Chat messages ---- */
[data-testid="stChatMessage"] { background: transparent; border: none; padding: 0.5rem 0; }
[data-testid="stChatMessageContent"] { font-size: 0.96rem; line-height: 1.6; color: var(--ink); }

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"] {
    background: var(--accent-dim);
    padding: 0.7rem 1rem;
    border-radius: 14px 14px 4px 14px;
    display: inline-block;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="stChatMessageContent"] {
    background: var(--surface);
    border: 1px solid var(--line);
    padding: 0.8rem 1.1rem;
    border-radius: 4px 14px 14px 14px;
}

/* ---- Chat input (pinned, no gradient bar) ---- */
[data-testid="stBottomBlockContainer"] {
    background: var(--bg);
    box-shadow: none;
    border-top: none;
}
[data-testid="stBottom"] { background: var(--bg); }
[data-testid="stChatInput"] {
    max-width: 780px;
    margin: 0 auto;
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: 14px;
}
[data-testid="stChatInput"] textarea { color: var(--ink) !important; }
[data-testid="stChatInputSubmitButton"] { color: var(--accent); }

.so-empty-doc {
    text-align: center;
    color: var(--ink-muted);
    padding: 2.5rem 1rem;
    font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# SESSION STATE
# =========================================================
if "extracted_text" not in st.session_state:
    st.session_state.extracted_text = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "doc_name" not in st.session_state:
    st.session_state.doc_name = None
if "doc_time" not in st.session_state:
    st.session_state.doc_time = None
if "pending_question" not in st.session_state:
    st.session_state.pending_question = None

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.markdown("""
    <div class="so-wordmark">Second <span>Opinion</span></div>
    <div class="so-badge">● Offline · private to this device</div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="so-section-label">Upload a document</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Upload", type=["pdf", "jpg", "jpeg", "png"], label_visibility="collapsed"
    )

    if uploaded_file is not None:
        suffix = os.path.splitext(uploaded_file.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_path = tmp_file.name

        if st.button("Read this document", use_container_width=True):
            with st.spinner("Reading…"):
                try:
                    text = extract_text(tmp_path)
                    st.session_state.extracted_text = text
                    st.session_state.doc_name = uploaded_file.name
                    st.session_state.doc_time = datetime.now().strftime("%I:%M %p")
                    st.session_state.chat_history = []
                    st.rerun()
                except Exception as e:
                    st.error(f"Couldn't read this file: {e}")
        os.unlink(tmp_path)

    if st.session_state.doc_name:
        st.markdown('<div class="so-section-label">Current document</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="so-doc-chip">
            <div class="fname">📄 {st.session_state.doc_name}</div>
            <div class="ftime">Loaded {st.session_state.doc_time}</div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("View extracted text"):
            st.text(st.session_state.extracted_text)

        if st.button("Clear & start over", use_container_width=True):
            st.session_state.extracted_text = None
            st.session_state.doc_name = None
            st.session_state.chat_history = []
            st.rerun()

    st.markdown('<div class="so-section-label">About</div>', unsafe_allow_html=True)
    st.caption("Everything — the document, the reading, the conversation — stays on this device. Nothing is uploaded anywhere.")

# =========================================================
# MAIN CHAT AREA
# =========================================================


def ask(question_text):
    st.session_state.pending_question = question_text


if not st.session_state.extracted_text:
    st.markdown("""
    <div class="so-hero">
        <div class="so-hero-title">What's on your report?</div>
        <div class="so-hero-sub">
            Upload a lab report or prescription from the sidebar, and ask about it in plain language — privately, offline, on your own device.
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div class="so-disclaimer">
        This explains what your report says — it does not diagnose or recommend treatment. Always confirm anything important with your doctor.
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="so-empty-doc">📄 &nbsp; Waiting for a document — use the sidebar to upload one.</div>', unsafe_allow_html=True)

else:
    st.markdown("""
    <div class="so-disclaimer">
        This explains what your report says — it does not diagnose or recommend treatment. Always confirm anything important with your doctor.
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.chat_history:
        st.markdown(f"""
        <div class="so-hero" style="padding-top:1rem; padding-bottom: 0.5rem;">
            <div class="so-hero-title" style="font-size:1.4rem;">Ready — ask about {st.session_state.doc_name}</div>
        </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.button("Summarize this report", on_click=ask, args=("Summarize this report",), use_container_width=True)
        with c2:
            st.button("What values are outside the normal range?", on_click=ask, args=("What values are outside the normal range?",), use_container_width=True)
        with c3:
            st.button("Explain this in very simple terms", on_click=ask, args=("Explain this in very simple terms",), use_container_width=True)

    for role, message in st.session_state.chat_history:
        with st.chat_message(role):
            st.write(message)

# Chat input — Streamlit automatically pins this to the bottom of the page
typed_question = st.chat_input(
    "Ask about your report…" if st.session_state.extracted_text else "Upload a document to start chatting",
    disabled=not st.session_state.extracted_text,
)

final_question = st.session_state.pending_question or typed_question
if st.session_state.pending_question:
    st.session_state.pending_question = None

if final_question:
    question_to_use = final_question.strip() or "Please explain this document in simple terms."
    st.session_state.chat_history.append(("user", question_to_use))

    with st.chat_message("user"):
        st.write(question_to_use)

    with st.chat_message("assistant"):
        with st.spinner("Reading your report and thinking…"):
            answer = explain_document(st.session_state.extracted_text, question_to_use)
        st.write(answer)

    st.session_state.chat_history.append(("assistant", answer))
    st.rerun()