import requests
import streamlit as st

# ===============================
# Backend URL
# ===============================

BACKEND_URL = "http://127.0.0.1:8000"

# ===============================
# Page Configuration
# ===============================

st.set_page_config(
    page_title="Knowledge Assistant",
    page_icon="⬡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===============================
# Full Custom CSS — Dark Editorial Theme
# ===============================

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

        :root {
            --bg:        #0F0F0F;
            --surface:   #161616;
            --surface2:  #1D1D1D;
            --border:    #2A2A2A;
            --border2:   #333333;
            --accent:    #D4A853;
            --accent2:   #E8C07A;
            --text:      #F0EBE1;
            --text2:     #A09880;
            --text3:     #665F52;
            --green:     #4CAF7D;
            --red:       #E05252;
            --blue:      #5B9BD5;
        }

        /* ---- Reset & Base ---- */
        html, body, [class*="css"] {
            font-family: 'DM Sans', sans-serif;
            background-color: var(--bg) !important;
            color: var(--text) !important;
        }

        .stApp {
            background-color: var(--bg) !important;
        }

        #MainMenu, footer, header { visibility: hidden; }

        .block-container {
            padding: 2rem 2.5rem 4rem !important;
            max-width: 1280px !important;
        }

        /* ---- KILL the grey flash / Streamlit re-run overlay ---- */
        .stApp > div,
        .stApp [data-testid="stAppViewContainer"],
        .stApp [data-testid="stAppViewBlockContainer"],
        .element-container,
        .stMarkdown,
        iframe {
            transition: none !important;
            animation: none !important;
        }
        /* Streamlit dims the whole app with opacity during re-runs — prevent it */
        .stApp[data-teststate="running"] .stAppViewContainer,
        .stApp[data-teststate="running"] {
            opacity: 1 !important;
        }
        /* Remove any fade/flash overlay Streamlit injects */
        [data-testid="stAppViewContainer"]::before,
        [data-testid="stAppViewContainer"]::after {
            display: none !important;
        }
        /* Suppress the greyish overlay Streamlit places during widget interaction */
        .stApp > .main > .block-container * {
            transition-property: none !important;
        }

        /* ---- Scrollbar ---- */
        ::-webkit-scrollbar { width: 5px; height: 5px; }
        ::-webkit-scrollbar-track { background: var(--surface); }
        ::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: var(--accent); }

        /* ---- Sidebar ---- */
        section[data-testid="stSidebar"] {
            background-color: var(--surface) !important;
            border-right: 1px solid var(--border) !important;
        }
        section[data-testid="stSidebar"] > div:first-child {
            padding: 1.5rem 1.2rem;
        }
        .sidebar-logo {
            font-family: 'DM Serif Display', serif;
            font-size: 22px;
            color: var(--accent);
            letter-spacing: -0.3px;
            line-height: 1.1;
            margin-bottom: 4px;
        }
        .sidebar-tagline {
            font-size: 11px;
            color: var(--text3);
            font-family: 'JetBrains Mono', monospace;
            letter-spacing: 1.2px;
            text-transform: uppercase;
            margin-bottom: 20px;
        }
        .sidebar-divider {
            border: none;
            border-top: 1px solid var(--border);
            margin: 16px 0;
        }
        .sidebar-section-label {
            font-size: 10px;
            letter-spacing: 1.8px;
            text-transform: uppercase;
            color: var(--text3);
            font-family: 'JetBrains Mono', monospace;
            margin-bottom: 10px;
            margin-top: 18px;
        }
        .sidebar-chip {
            display: inline-block;
            background: var(--surface2);
            border: 1px solid var(--border);
            border-radius: 6px;
            font-size: 12px;
            color: var(--text2);
            padding: 3px 9px;
            margin: 3px 3px 3px 0;
            font-family: 'JetBrains Mono', monospace;
        }
        .status-dot {
            display: inline-block;
            width: 8px; height: 8px;
            border-radius: 50%;
            margin-right: 7px;
            vertical-align: middle;
        }
        .status-ok { background: var(--green); box-shadow: 0 0 6px var(--green); }
        .status-err { background: var(--red); box-shadow: 0 0 6px var(--red); }
        .status-text {
            font-size: 12.5px;
            color: var(--text2);
            vertical-align: middle;
        }

        /* ---- Page Header ---- */
        .page-header {
            display: flex;
            align-items: flex-end;
            justify-content: space-between;
            margin-bottom: 36px;
            padding-bottom: 24px;
            border-bottom: 1px solid var(--border);
        }
        .page-title {
            font-family: 'DM Serif Display', serif;
            font-size: 48px;
            color: var(--text);
            line-height: 1;
            letter-spacing: -1.5px;
        }
        .page-title span {
            color: var(--accent);
            font-style: italic;
        }
        .page-date {
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            color: var(--text3);
            letter-spacing: 1px;
            text-align: right;
            line-height: 1.8;
        }

        /* ---- Stat Cards Row ---- */
        .stat-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 20px 22px;
            position: relative;
            overflow: hidden;
            transition: border-color 0.2s;
        }
        .stat-card:hover { border-color: var(--accent); }
        .stat-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 2px;
            background: linear-gradient(90deg, var(--accent), transparent);
        }
        .stat-icon {
            font-size: 22px;
            margin-bottom: 10px;
            display: block;
        }
        .stat-label {
            font-size: 10.5px;
            letter-spacing: 1.6px;
            text-transform: uppercase;
            color: var(--text3);
            font-family: 'JetBrains Mono', monospace;
            margin-bottom: 6px;
        }
        .stat-title {
            font-family: 'DM Serif Display', serif;
            font-size: 22px;
            color: var(--text);
            line-height: 1.1;
        }
        .stat-desc {
            font-size: 13px;
            color: var(--text2);
            margin-top: 6px;
            line-height: 1.5;
        }

        /* ---- Tabs ---- */
        .stTabs [data-baseweb="tab-list"] {
            background: var(--surface) !important;
            border-radius: 14px !important;
            padding: 5px !important;
            gap: 4px !important;
            border: 1px solid var(--border) !important;
            margin-bottom: 28px !important;
        }
        .stTabs [data-baseweb="tab"] {
            background: transparent !important;
            border-radius: 10px !important;
            color: var(--text2) !important;
            padding: 10px 20px !important;
            font-size: 13.5px !important;
            font-family: 'DM Sans', sans-serif !important;
            font-weight: 500 !important;
            border: none !important;
            transition: all 0.2s !important;
        }
        .stTabs [data-baseweb="tab"]:hover {
            color: var(--text) !important;
            background: var(--surface2) !important;
        }
        .stTabs [aria-selected="true"] {
            background: var(--accent) !important;
            color: #0F0F0F !important;
            font-weight: 600 !important;
        }

        /* ---- Section Panel ---- */
        .panel {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 28px 30px;
            margin-bottom: 20px;
        }
        .panel-title {
            font-family: 'DM Serif Display', serif;
            font-size: 26px;
            color: var(--text);
            margin-bottom: 6px;
            letter-spacing: -0.5px;
        }
        .panel-subtitle {
            font-size: 14px;
            color: var(--text2);
            margin-bottom: 22px;
            line-height: 1.5;
        }
        .divider-line {
            border: none;
            border-top: 1px solid var(--border);
            margin: 20px 0;
        }

        /* ---- Inputs ---- */
        .stTextArea textarea,
        .stTextInput input,
        .stNumberInput input {
            background-color: var(--surface2) !important;
            border: 1px solid var(--border2) !important;
            border-radius: 12px !important;
            color: var(--text) !important;
            font-family: 'DM Sans', sans-serif !important;
            font-size: 14px !important;
            caret-color: var(--accent) !important;
            transition: border-color 0.2s !important;
        }
        .stTextArea textarea:focus,
        .stTextInput input:focus,
        .stNumberInput input:focus {
            border-color: var(--accent) !important;
            box-shadow: 0 0 0 2px rgba(212, 168, 83, 0.12) !important;
        }
        .stTextArea textarea::placeholder,
        .stTextInput input::placeholder {
            color: var(--text3) !important;
        }
        label {
            color: var(--text2) !important;
            font-size: 13px !important;
            font-weight: 500 !important;
        }

        /* ---- Multiselect ---- */
        div[data-baseweb="select"] > div {
            background-color: var(--surface2) !important;
            border: 1px solid var(--border2) !important;
            border-radius: 12px !important;
            color: var(--text) !important;
        }
        div[data-baseweb="select"] span {
            color: var(--text) !important;
        }
        /* Selected tags in multiselect — yellow background needs black text */
        div[data-baseweb="tag"] {
            background-color: var(--accent) !important;
            color: #0D0D0D !important;
        }
        div[data-baseweb="tag"] span {
            color: #0D0D0D !important;
        }
        div[data-baseweb="tag"] [data-testid="stMultiSelectDeleteButton"],
        div[data-baseweb="tag"] svg {
            color: #0D0D0D !important;
            fill: #0D0D0D !important;
        }

        /* ---- File Uploader ---- */
        .stFileUploader {
            background: var(--surface2) !important;
            border: 1.5px dashed var(--border2) !important;
            border-radius: 16px !important;
            padding: 10px !important;
            transition: border-color 0.2s !important;
        }
        .stFileUploader:hover {
            border-color: var(--accent) !important;
        }
        [data-testid="stFileUploaderDropzoneInstructions"] {
            color: var(--text2) !important;
        }

        /* ---- Number Input ---- */
        .stNumberInput [data-baseweb="input"] {
            background: var(--surface2) !important;
            border: 1px solid var(--border2) !important;
            border-radius: 12px !important;
        }
        .stNumberInput button {
            background: var(--border2) !important;
            color: var(--text) !important;
            border: none !important;
        }

        /* ---- Primary Button ---- */
        .stButton > button[kind="primary"],
        .stButton > button {
            background: var(--accent) !important;
            color: #0D0D0D !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 0.7rem 1.4rem !important;
            font-weight: 600 !important;
            font-size: 14px !important;
            font-family: 'DM Sans', sans-serif !important;
            letter-spacing: 0.2px !important;
            transition: background 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease !important;
            width: 100% !important;
        }
        .stButton > button:hover {
            background: var(--accent2) !important;
            color: #0D0D0D !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 6px 20px rgba(212, 168, 83, 0.28) !important;
        }
        .stButton > button:active {
            transform: translateY(0) !important;
            color: #0D0D0D !important;
        }
        .stButton > button:focus,
        .stButton > button:focus-visible {
            color: #0D0D0D !important;
            outline: none !important;
        }
        /* Ensure button text (p tag inside button) is always black */
        .stButton > button p,
        .stButton > button span,
        .stButton > button div {
            color: #0D0D0D !important;
        }
        .stFormSubmitButton > button {
            background: var(--green) !important;
            color: #0D0D0D !important;
            border: none !important;
            border-radius: 12px !important;
            padding: 0.7rem 1.4rem !important;
            font-weight: 600 !important;
            font-size: 14px !important;
            transition: background 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease !important;
            width: 100% !important;
        }
        .stFormSubmitButton > button:hover {
            background: #5fd98f !important;
            color: #0D0D0D !important;
            box-shadow: 0 6px 20px rgba(76,175,125,0.25) !important;
            transform: translateY(-1px) !important;
        }
        .stFormSubmitButton > button p,
        .stFormSubmitButton > button span,
        .stFormSubmitButton > button div {
            color: #0D0D0D !important;
        }

        /* ---- Alerts ---- */
        div[data-testid="stAlert"] {
            background-color: var(--surface2) !important;
            border-radius: 12px !important;
            border: 1px solid var(--border2) !important;
        }
        div[data-testid="stAlert"][class*="success"] {
            border-left: 3px solid var(--green) !important;
        }
        div[data-testid="stAlert"][class*="error"] {
            border-left: 3px solid var(--red) !important;
        }
        div[data-testid="stAlert"][class*="warning"] {
            border-left: 3px solid var(--accent) !important;
        }
        div[data-testid="stAlert"][class*="info"] {
            border-left: 3px solid var(--blue) !important;
        }

        /* ---- Expander ---- */
        .streamlit-expanderHeader,
        [data-testid="stExpander"] summary {
            background: var(--surface2) !important;
            border-radius: 10px !important;
            color: var(--text2) !important;
            border: 1px solid var(--border) !important;
            font-size: 13.5px !important;
        }
        [data-testid="stExpander"] div[data-testid="stExpanderDetails"] {
            background: var(--surface2) !important;
            border: 1px solid var(--border) !important;
            border-top: none !important;
            border-radius: 0 0 10px 10px !important;
            padding: 12px 16px !important;
        }

        /* ---- Spinner ---- */
        [data-testid="stSpinner"] {
            color: var(--accent) !important;
        }

        /* ---- Checkbox ---- */
        .stCheckbox label {
            color: var(--text2) !important;
            font-size: 13.5px !important;
        }

        /* ---- Custom Cards ---- */
        .answer-card {
            background: var(--surface2);
            border: 1px solid var(--border2);
            border-left: 4px solid var(--accent);
            border-radius: 16px;
            padding: 24px 26px;
            margin-top: 20px;
            line-height: 1.75;
            font-size: 15px;
            color: var(--text);
        }
        .answer-card .answer-label {
            font-family: 'JetBrains Mono', monospace;
            font-size: 10px;
            letter-spacing: 2px;
            text-transform: uppercase;
            color: var(--accent);
            margin-bottom: 12px;
        }

        .source-row {
            display: flex;
            align-items: center;
            gap: 10px;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 10px 14px;
            margin-bottom: 7px;
            font-size: 13px;
            color: var(--text2);
        }
        .source-num {
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            color: var(--accent);
            background: rgba(212,168,83,0.1);
            padding: 2px 8px;
            border-radius: 6px;
        }
        .source-file {
            font-weight: 500;
            color: var(--text);
        }
        .source-section {
            font-family: 'JetBrains Mono', monospace;
            font-size: 11.5px;
            color: var(--text3);
            margin-left: auto;
        }

        .eval-card {
            background: var(--surface2);
            border: 1px solid var(--border2);
            border-radius: 16px;
            padding: 22px 24px;
            margin-bottom: 16px;
        }
        .eval-card .q-header {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 14px;
        }
        .eval-badge {
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            background: rgba(212,168,83,0.15);
            color: var(--accent);
            padding: 4px 10px;
            border-radius: 20px;
        }
        .eval-q-text {
            font-weight: 600;
            font-size: 15px;
            color: var(--text);
        }
        .eval-answer-block {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 14px 16px;
            font-size: 13.5px;
            color: var(--text2);
            white-space: pre-wrap;
            margin: 10px 0;
            line-height: 1.6;
        }
        .eval-feedback {
            background: linear-gradient(135deg, rgba(212,168,83,0.06), rgba(212,168,83,0.02));
            border: 1px solid rgba(212,168,83,0.2);
            border-radius: 12px;
            padding: 14px 16px;
            font-size: 14px;
            color: var(--text);
            white-space: pre-wrap;
            line-height: 1.7;
            margin-top: 10px;
        }
        .eval-feedback-label {
            font-family: 'JetBrains Mono', monospace;
            font-size: 9.5px;
            letter-spacing: 2px;
            text-transform: uppercase;
            color: var(--accent);
            margin-bottom: 8px;
        }

        .doc-row {
            display: flex;
            align-items: center;
            background: var(--surface2);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 13px 16px;
            margin-bottom: 8px;
            gap: 12px;
            transition: border-color 0.2s;
        }
        .doc-row:hover { border-color: var(--border2); }
        .doc-icon {
            font-size: 18px;
            flex-shrink: 0;
        }
        .doc-name {
            font-size: 14px;
            font-weight: 500;
            color: var(--text);
            flex: 1;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .upload-success-box {
            background: rgba(76,175,125,0.08);
            border: 1px solid rgba(76,175,125,0.25);
            border-radius: 14px;
            padding: 16px 20px;
            margin-top: 16px;
        }
        .upload-success-label {
            font-family: 'JetBrains Mono', monospace;
            font-size: 10px;
            letter-spacing: 2px;
            text-transform: uppercase;
            color: var(--green);
            margin-bottom: 8px;
        }
        .upload-meta {
            font-size: 13.5px;
            color: var(--text2);
            line-height: 2;
        }
        .upload-meta b { color: var(--text); }

        .q-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 14px;
            padding: 16px 18px;
            margin-bottom: 6px;
        }
        .q-number {
            font-family: 'JetBrains Mono', monospace;
            font-size: 10px;
            letter-spacing: 2px;
            text-transform: uppercase;
            color: var(--accent);
            margin-bottom: 7px;
        }
        .q-text {
            font-size: 15px;
            color: var(--text);
            font-weight: 500;
            line-height: 1.5;
        }

        .info-banner {
            background: rgba(91,155,213,0.08);
            border: 1px solid rgba(91,155,213,0.2);
            border-radius: 12px;
            padding: 12px 16px;
            font-size: 13px;
            color: var(--text2);
            line-height: 1.5;
        }

        .danger-zone {
            background: rgba(224,82,82,0.06);
            border: 1px solid rgba(224,82,82,0.18);
            border-radius: 14px;
            padding: 16px 18px;
            margin-top: 10px;
        }
        .danger-zone .danger-label {
            font-family: 'JetBrains Mono', monospace;
            font-size: 9.5px;
            letter-spacing: 2px;
            text-transform: uppercase;
            color: var(--red);
            margin-bottom: 8px;
        }

        /* Spinner override for dark */
        div[data-testid="stSpinner"] p {
            color: var(--text2) !important;
            font-size: 13.5px !important;
        }

        /* Form submit area */
        [data-testid="stForm"] {
            border: none !important;
            padding: 0 !important;
        }

        /* Headings in content */
        h1, h2, h3 {
            font-family: 'DM Serif Display', serif !important;
            color: var(--text) !important;
        }
        h3 {
            font-size: 20px !important;
            letter-spacing: -0.3px !important;
        }
        p {
            color: var(--text2);
            line-height: 1.65;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# ===============================
# Helper API Functions
# ===============================

def get_api(endpoint: str):
    response = requests.get(f"{BACKEND_URL}{endpoint}", timeout=900)
    response.raise_for_status()
    return response.json()


def post_api(endpoint: str, payload: dict):
    response = requests.post(f"{BACKEND_URL}{endpoint}", json=payload, timeout=900)
    response.raise_for_status()
    return response.json()


def delete_api(endpoint: str):
    response = requests.delete(f"{BACKEND_URL}{endpoint}", timeout=900)
    response.raise_for_status()
    return response.json()


def upload_file_to_backend(uploaded_file):
    files = {
        "file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)
    }
    response = requests.post(f"{BACKEND_URL}/upload", files=files, timeout=1200)
    response.raise_for_status()
    return response.json()


def check_system_status():
    try:
        health = get_api("/health")
        backend_status = health.get("backend", "unknown")
        ollama_status = health.get("ollama", {}).get("status", "unknown")
        if backend_status == "running" and ollama_status == "running":
            return True, "All systems operational"
        return False, "Service not fully ready"
    except Exception:
        return False, "Service unreachable"


def load_document_names():
    """
    Loads available document names from backend.
    Used for document selection in Ask, Explain, and Review tabs.
    """
    try:
        result = get_api("/documents")
        return result.get("documents", [])
    except Exception:
        return []


def render_sources(sources):
    if not sources:
        return
    html = ""
    for i, s in enumerate(sources, 1):
        fname = s.get("file_name", "Unknown file")
        cidx = s.get("chunk_index", "-")
        ext = fname.rsplit(".", 1)[-1].upper() if "." in fname else "DOC"
        html += f"""
        <div class="source-row">
            <span class="source-num">#{i:02d}</span>
            <span class="source-file">{fname}</span>
            <span class="source-section">{ext} · §{cidx}</span>
        </div>
        """
    with st.expander("Sources used", expanded=False):
        st.markdown(html, unsafe_allow_html=True)


def show_answer(title_label: str, content: str):
    st.markdown(
        f"""
        <div class="answer-card">
            <div class="answer-label">{title_label}</div>
            <div style="white-space: pre-wrap; line-height: 1.75;">{content}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ===============================
# Sidebar
# ===============================

with st.sidebar:
    st.markdown(
        """
        <div class="sidebar-logo">Knowledge<br>Assistant</div>
        <div class="sidebar-tagline">Company Helpdesk · AI</div>
        """,
        unsafe_allow_html=True
    )

    status_ok, status_message = check_system_status()
    dot_class = "status-ok" if status_ok else "status-err"
    st.markdown(
        f"""
        <span class="status-dot {dot_class}"></span>
        <span class="status-text">{status_message}</span>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-section-label">Quick Actions</div>', unsafe_allow_html=True)

    if st.button("↻  Refresh Library"):
        st.session_state["refresh_docs"] = True
        st.session_state["document_list"] = load_document_names()

    st.markdown('<div class="sidebar-section-label">Supported Formats</div>', unsafe_allow_html=True)
    st.markdown(
        '<span class="sidebar-chip">PDF</span>'
        '<span class="sidebar-chip">DOCX</span>'
        '<span class="sidebar-chip">TXT</span>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="sidebar-section-label">Best For</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div style="font-size:13px; color: var(--text2); line-height:1.7;">
            Policies · Onboarding Docs<br>
            Process Guides · Manuals<br>
            Project Documents
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<hr class="sidebar-divider">', unsafe_allow_html=True)

    with st.expander("⚠ Danger Zone"):
        st.markdown(
            '<div class="danger-zone">'
            '<div class="danger-label">Irreversible Action</div>'
            'This permanently removes all indexed document knowledge from the system.',
            unsafe_allow_html=True
        )
        confirm_clear = st.checkbox("I understand this cannot be undone")
        if confirm_clear:
            if st.button("Clear All Documents"):
                try:
                    result = delete_api("/clear")
                    st.success(result.get("message", "Cleared."))
                    st.session_state["document_list"] = []
                    st.session_state["review_questions"] = []
                    st.session_state["review_evaluation_results"] = None
                    st.session_state["review_selected_documents"] = []
                except Exception as e:
                    st.error(f"Failed: {e}")
        st.markdown("</div>", unsafe_allow_html=True)

# ===============================
# Page Header
# ===============================

import datetime
today = datetime.date.today().strftime("%d %b %Y")

st.markdown(
    f"""
    <div class="page-header">
        <div>
            <div class="page-title">Company <span>Knowledge</span><br>Assistant</div>
        </div>
        
    </div>
    """,
    unsafe_allow_html=True
)

# ===============================
# Feature Stat Cards
# ===============================

c1, c2, c3, c4 = st.columns(4)

cards = [
    ("📤", "UPLOAD", "Ingest Documents", "Add PDFs, Word docs, or text files for the assistant to learn from."),
    ("💬", "ASK", "Query Knowledge", "Ask natural-language questions — get answers drawn directly from selected docs."),
    ("🧾", "EXPLAIN", "Summarize & Simplify", "Turn selected documents into clear, structured explanations in seconds."),
    ("✅", "REVIEW", "Test Understanding", "Auto-generate question forms and get AI-evaluated feedback on answers."),
]

for col, (icon, label, title, desc) in zip([c1, c2, c3, c4], cards):
    with col:
        st.markdown(
            f"""
            <div class="stat-card">
                <span class="stat-icon">{icon}</span>
                <div class="stat-label">{label}</div>
                <div class="stat-title">{title}</div>
                <div class="stat-desc">{desc}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

st.markdown("<br>", unsafe_allow_html=True)

# ===============================
# Main Tabs
# ===============================

tab_upload, tab_ask, tab_explain, tab_review, tab_docs = st.tabs([
    "📤  Upload",
    "💬  Ask",
    "🧾  Explain",
    "✅  Review",
    "📁  Library",
])

# ===============================
# Upload Tab
# ===============================

with tab_upload:
    st.markdown(
        """
        <div class="panel">
            <div class="panel-title">Upload Document</div>
            <div class="panel-subtitle">
                Add a company document so the assistant can index its content and answer questions from it.
                Supported formats: PDF, DOCX, TXT.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    uploaded_file = st.file_uploader(
        "Drop your document here or click to browse",
        type=["pdf", "docx", "txt"],
        help="PDF, DOCX, and TXT files are supported. Large files may take longer to index."
    )

    st.markdown("<br>", unsafe_allow_html=True)
    col_a, col_b = st.columns([1, 2])

    with col_a:
        upload_clicked = st.button("Upload & Process Document")

    with col_b:
        st.markdown(
            '<div class="info-banner">⏳ Large files may take a moment. '
            'Keep this page open while the document is being indexed.</div>',
            unsafe_allow_html=True
        )

    if upload_clicked:
        if uploaded_file is None:
            st.warning("Please select a document before uploading.")
        else:
            try:
                with st.spinner("Reading and indexing document…"):
                    result = upload_file_to_backend(uploaded_file)

                fname = result.get("file_name", uploaded_file.name)
                chunks = result.get("chunks_created", "Completed")

                st.markdown(
                    f"""
                    <div class="upload-success-box">
                        <div class="upload-success-label">✓ Processed Successfully</div>
                        <div class="upload-meta">
                            <b>File:</b> {fname}<br>
                            <b>Knowledge sections indexed:</b> {chunks}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.session_state["refresh_docs"] = True
                st.session_state["document_list"] = load_document_names()

            except Exception as e:
                st.error(f"Upload failed: {e}")

# ===============================
# Ask Tab
# ===============================

with tab_ask:
    st.markdown(
        """
        <div class="panel">
            <div class="panel-title">Ask the Assistant</div>
            <div class="panel-subtitle">
                Type any question related to selected uploaded documents.
                The assistant will search only the selected knowledge source and return a precise, grounded answer.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    available_documents = load_document_names()

    selected_ask_documents = st.multiselect(
        "Select document(s) to search",
        options=available_documents,
        default=[],
        help="Choose one or more documents. The assistant will answer only from selected documents."
    )

    if not available_documents:
        st.info("No documents available. Please upload a document first.")
    elif not selected_ask_documents:
        st.info("Select at least one document before asking a question.")

    user_question = st.text_area(
        "Your question",
        placeholder="e.g. What is the leave policy for new employees? / Summarize the onboarding steps.",
        height=130
    )

    ask_clicked = st.button("Get Answer")

    if ask_clicked:
        if not selected_ask_documents:
            st.warning("Please select at least one document.")
        elif not user_question.strip():
            st.warning("Please enter a question before submitting.")
        else:
            try:
                with st.spinner("Searching selected document(s)…"):
                    result = post_api(
                        "/ask",
                        {
                            "question": user_question,
                            "selected_file_names": selected_ask_documents
                        }
                    )

                answer = result.get("answer", "No answer returned.")
                show_answer("ASSISTANT RESPONSE", answer)
                render_sources(result.get("sources", []))

            except Exception as e:
                st.error(f"Could not generate answer: {e}")

# ===============================
# Explain Tab
# ===============================

with tab_explain:
    st.markdown(
        """
        <div class="panel">
            <div class="panel-title">Explain Documents</div>
            <div class="panel-subtitle">
                Generate a clear, structured explanation from selected indexed documents.
                Ideal for quickly understanding long or complex company materials.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    available_documents = load_document_names()

    selected_explain_documents = st.multiselect(
        "Select document(s) to explain",
        options=available_documents,
        default=[],
        help="Choose one or more documents. Explanation will be generated only from selected documents."
    )

    if not available_documents:
        st.info("No documents available. Please upload a document first.")
    elif not selected_explain_documents:
        st.info("Select at least one document to generate explanation.")

    col_a, col_b = st.columns([1, 2])

    with col_a:
        explain_clicked = st.button("Generate Explanation")

    with col_b:
        st.markdown(
            '<div class="info-banner">📄 Explanation will be generated only from selected document(s).</div>',
            unsafe_allow_html=True
        )

    if explain_clicked:
        if not selected_explain_documents:
            st.warning("Please select at least one document.")
        else:
            try:
                with st.spinner("Generating explanation from selected document(s)…"):
                    result = post_api(
                        "/explain-selected",
                        {
                            "selected_file_names": selected_explain_documents
                        }
                    )

                explanation = result.get("explanation", "No explanation returned.")
                show_answer("DOCUMENT EXPLANATION", explanation)

            except Exception as e:
                st.error(f"Could not generate explanation: {e}")

# ===============================
# Review Tab
# ===============================

with tab_review:
    st.markdown(
        """
        <div class="panel">
            <div class="panel-title">Review Questions</div>
            <div class="panel-subtitle">
                Auto-generate a question form from selected uploaded documents.
                Answer all questions and submit for AI-powered evaluation with feedback.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    available_documents = load_document_names()

    selected_review_documents = st.multiselect(
        "Select document(s) for review",
        options=available_documents,
        default=[],
        help="Questions and evaluation will use only selected documents."
    )

    if not available_documents:
        st.info("No documents available. Please upload a document first.")
    elif not selected_review_documents:
        st.info("Select at least one document before generating review questions.")

    col_n, col_btn, col_tip = st.columns([1, 1, 2])

    with col_n:
        number_of_questions = st.number_input(
            "Number of questions",
            min_value=1, max_value=30, value=5, step=1
        )

    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        generate_clicked = st.button("Generate Review Form")

    with col_tip:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            '<div class="info-banner">✍️ Questions and evaluation will be based only on selected document(s).</div>',
            unsafe_allow_html=True
        )

    if generate_clicked:
        if not selected_review_documents:
            st.warning("Please select at least one document.")
        else:
            try:
                with st.spinner("Generating review questions from selected document(s)…"):
                    result = post_api(
                        "/generate-review-questions",
                        {
                            "number_of_questions": int(number_of_questions),
                            "selected_file_names": selected_review_documents
                        }
                    )

                questions = result.get("questions", [])

                if isinstance(questions, str):
                    st.warning(questions)
                    questions = []

                if not questions:
                    st.warning("No questions generated. Ensure selected documents are indexed.")
                else:
                    st.session_state["review_questions"] = questions
                    st.session_state["review_evaluation_results"] = None
                    st.session_state["review_selected_documents"] = selected_review_documents

                    st.session_state["review_form_version"] = (
                        st.session_state.get("review_form_version", 0) + 1
                    )

                    st.success(f"{len(questions)} review question(s) ready.")

            except Exception as e:
                st.error(f"Could not generate questions: {e}")

    review_questions = st.session_state.get("review_questions", [])

    if review_questions:
        review_form_version = st.session_state.get("review_form_version", 0)

        st.markdown('<hr class="divider-line">', unsafe_allow_html=True)
        st.markdown(
            '<div style="font-family:\'JetBrains Mono\',monospace; font-size:10.5px; '
            'letter-spacing:2px; text-transform:uppercase; color:var(--accent); margin-bottom:18px;">'
            f'Review Form · {len(review_questions)} Questions</div>',
            unsafe_allow_html=True
        )

        selected_docs_for_form = st.session_state.get("review_selected_documents", [])

        if selected_docs_for_form:
            selected_docs_text = ", ".join(selected_docs_for_form)
            st.markdown(
                f"""
                <div class="info-banner">
                    Review based on selected document(s): {selected_docs_text}
                </div>
                """,
                unsafe_allow_html=True
            )

        with st.form("review_question_form"):
            review_answers = []

            for index, question in enumerate(review_questions, start=1):
                st.markdown(
                    f"""
                    <div class="q-card">
                        <div class="q-number">Question {index:02d} of {len(review_questions)}</div>
                        <div class="q-text">{question}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                answer = st.text_area(
                    label=f"Answer {index}",
                    placeholder="Write your answer here…",
                    height=110,
                    key=f"review_answer_{review_form_version}_{index}"
                )

                review_answers.append(
                    {
                        "question": question,
                        "user_answer": answer
                    }
                )

                st.markdown("<br>", unsafe_allow_html=True)

            submitted = st.form_submit_button("Submit All Answers for Evaluation")

        if submitted:
            try:
                with st.spinner("Evaluating your answers using selected document(s)…"):
                    result = post_api(
                        "/evaluate-review-form",
                        {
                            "review_answers": review_answers,
                            "selected_file_names": st.session_state.get("review_selected_documents", [])
                        }
                    )

                st.session_state["review_evaluation_results"] = result.get("results", [])
                st.success("Evaluation complete.")

            except Exception as e:
                st.error(f"Evaluation failed: {e}")

    evaluation_results = st.session_state.get("review_evaluation_results")

    if evaluation_results:
        st.markdown('<hr class="divider-line">', unsafe_allow_html=True)
        st.markdown(
            '<div style="font-family:\'JetBrains Mono\',monospace; font-size:10.5px; '
            'letter-spacing:2px; text-transform:uppercase; color:var(--green); margin-bottom:18px;">'
            'Evaluation Results</div>',
            unsafe_allow_html=True
        )

        for item in evaluation_results:
            qnum = item.get("question_number", "-")
            question = item.get("question", "")
            user_answer = item.get("user_answer", "") or "No answer provided."
            evaluation = item.get("evaluation", "")
            sources = item.get("sources", [])

            st.markdown(
                f"""
                <div class="eval-card">
                    <div class="q-header">
                        <span class="eval-badge">Q{qnum:02d}</span>
                        <span class="eval-q-text">{question}</span>
                    </div>
                    <div style="font-family:'JetBrains Mono',monospace; font-size:9.5px;
                        letter-spacing:2px; text-transform:uppercase; color:var(--text3);
                        margin-bottom:6px;">Your Answer</div>
                    <div class="eval-answer-block">{user_answer}</div>
                    <div class="eval-feedback-label">AI Feedback</div>
                    <div class="eval-feedback">{evaluation}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

            if sources:
                render_sources(sources)

# ===============================
# Document Library Tab
# ===============================

with tab_docs:
    st.markdown(
        """
        <div class="panel">
            <div class="panel-title">Document Library</div>
            <div class="panel-subtitle">
                View and manage all documents currently available to the assistant.
                Remove individual files or use the sidebar to clear everything.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    load_docs_clicked = st.button("Load Documents")

    if load_docs_clicked or st.session_state.get("refresh_docs"):
        try:
            result = get_api("/documents")
            documents = result.get("documents", [])
            total = result.get("total_documents", 0)
            st.session_state["document_list"] = documents
            st.session_state["refresh_docs"] = False

            if total == 0:
                st.info("No documents uploaded yet. Go to the Upload tab to add files.")
            else:
                st.success(f"{total} document(s) indexed and ready.")
        except Exception as e:
            st.error(f"Could not load documents: {e}")

    documents = st.session_state.get("document_list", [])

    if documents:
        st.markdown('<hr class="divider-line">', unsafe_allow_html=True)
        st.markdown(
            f'<div style="font-family:\'JetBrains Mono\',monospace; font-size:10.5px; '
            f'letter-spacing:2px; text-transform:uppercase; color:var(--text3); margin-bottom:14px;">'
            f'{len(documents)} Document(s) Available</div>',
            unsafe_allow_html=True
        )

        for doc in documents:
            ext = doc.rsplit(".", 1)[-1].upper() if "." in doc else "DOC"
            icon = "📕" if ext == "PDF" else "📘" if ext == "DOCX" else "📄"

            col_doc, col_btn = st.columns([5, 1])

            with col_doc:
                st.markdown(
                    f"""
                    <div class="doc-row">
                        <span class="doc-icon">{icon}</span>
                        <span class="doc-name">{doc}</span>
                        <span class="source-section">{ext}</span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with col_btn:
                if st.button("Remove", key=f"remove_{doc}"):
                    try:
                        with st.spinner(f"Removing {doc}…"):
                            result = post_api("/delete-document", {"file_name": doc})
                        st.success(result.get("message", "Removed."))
                        updated = [d for d in documents if d != doc]
                        st.session_state["document_list"] = updated
                        st.session_state["refresh_docs"] = True
                        st.rerun()
                    except Exception as e:
                        st.error(f"Could not remove: {e}")

    else:
        st.markdown(
            """
            <div style="text-align:center; padding: 48px 0;">
                <div style="font-size:36px; margin-bottom:12px;">📭</div>
                <div style="font-family:'DM Serif Display',serif; font-size:20px;
                    color:var(--text2); margin-bottom:8px;">Library is empty</div>
                <div style="font-size:13px; color:var(--text3);">
                    Click <b style="color:var(--text2);">Load Documents</b> to refresh,
                    or upload files in the Upload tab.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )