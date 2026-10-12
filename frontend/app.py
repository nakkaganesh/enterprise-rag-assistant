import os

import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/")
ASK_URL = f"{API_URL}/ask"
UPLOAD_URL = f"{API_URL}/documents/upload"

st.set_page_config(
    page_title="Enterprise RAG | AI Workspace",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

for key, default in {
    "messages": [],
    "indexed_documents": [],
    "total_chunks": 0,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

st.markdown(
    """
<style>
:root { color-scheme: dark; }
.stApp { background: #0b1220; color: #e2e8f0; }
[data-testid="stSidebar"] { background: #111c30; border-right: 1px solid #26364d; }
[data-testid="stHeader"] { background: #0b1220; }
.block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1400px; }
.stApp h1, .stApp h2, .stApp h3 { color: #f8fafc; }
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label { color: #cbd5e1; }
.dashboard-subtitle { color: #94a3b8; margin-bottom: 1.5rem; }
.metric-card {
    background: #17243a; border: 1px solid #2b3c55;
    border-radius: 14px; padding: 20px; margin-bottom: 12px;
}
.metric-label { color: #94a3b8; font-size: 13px; }
.metric-value { color: #f8fafc; font-size: 28px; font-weight: 700; margin-top: 8px; }
.section-title { color: #f8fafc; font-size: 19px; font-weight: 650; margin-bottom: 14px; }
.info-panel {
    background: #17243a; border: 1px solid #2b3c55;
    border-radius: 12px; padding: 16px; color: #cbd5e1; margin-bottom: 14px;
}
.stButton > button[kind="primary"] {
    background: #2563eb; border: 1px solid #2563eb; border-radius: 9px;
    color: white;
}
.stButton > button[kind="primary"]:hover {
    background: #1d4ed8; border-color: #1d4ed8;
}
[data-testid="stChatMessage"] {
    background: #17243a !important;
    border: 1px solid #334155 !important;
    border-radius: 14px !important;
    padding: 14px !important;
}
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"],
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] * {
    color: #f1f5f9 !important;
}
/* Target the actual Streamlit chat input and its nested wrappers. */
[data-testid="stChatInput"],
[data-testid="stChatInput"] > div,
[data-testid="stChatInput"] [data-baseweb="textarea"],
[data-testid="stChatInput"] [data-baseweb="base-input"],
[data-testid="stChatInputTextArea"] {
    background: #17243a !important;
    background-color: #17243a !important;
    border-color: #475569 !important;
    color-scheme: dark;
}
[data-testid="stChatInput"] {
    border: 1px solid #475569 !important;
    border-radius: 12px !important;
}
[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] textarea:focus,
[data-testid="stChatInputTextArea"],
[data-testid="stChatInput"] [contenteditable="true"] {
    background: #17243a !important;
    background-color: #17243a !important;
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    caret-color: #ffffff !important;
    opacity: 1 !important;
}
[data-testid="stChatInput"] textarea::placeholder,
[data-testid="stChatInputTextArea"]::placeholder {
    color: #a7b6cc !important;
    -webkit-text-fill-color: #a7b6cc !important;
    opacity: 1 !important;
}
[data-testid="stChatInput"] button,
[data-testid="stChatInput"] button svg { color: #e2e8f0 !important; }
[data-testid="stExpander"] {
    background: #111c30 !important;
    border: 1px solid #334155 !important;
    border-radius: 10px !important;
}
[data-testid="stExpander"] summary,
[data-testid="stExpander"] [data-testid="stMarkdownContainer"] * {
    color: #e2e8f0 !important;
}
.stApp code { background: #24344c !important; color: #bfdbfe !important; }
[data-testid="stFileUploader"] section {
    background: #17243a !important; border-color: #475569 !important;
}
</style>
""",
    unsafe_allow_html=True,
)


def backend_available():
    """Check that the API responds, even if /health is not implemented."""
    try:
        response = requests.get(f"{API_URL}/health", timeout=3)
        if response.ok:
            return True
        if response.status_code == 404:
            return requests.get(f"{API_URL}/openapi.json", timeout=3).ok
        return False
    except requests.RequestException:
        return False


with st.sidebar:
    st.title("🧠 Enterprise RAG")
    st.caption("AI Knowledge Workspace")
    st.divider()
    st.subheader("Navigation")
    st.markdown("📊 Dashboard")
    st.markdown("📁 Knowledge Base")
    st.markdown("💬 AI Assistant")
    st.divider()
    st.subheader("Backend Connection")
    if backend_available():
        st.success("API reachable")
    else:
        st.error("API offline")
    st.caption(f"Backend: {API_URL}")
    st.divider()
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.caption("Enterprise RAG Assistant")

st.title("Enterprise RAG Dashboard")
st.markdown(
    '<div class="dashboard-subtitle">Manage documents, explore your knowledge base, '
    'and ask questions with source-grounded AI.</div>',
    unsafe_allow_html=True,
)

m1, m2, m3 = st.columns(3)
metrics = [
    ("Documents Uploaded This Session", len(st.session_state.indexed_documents)),
    ("Chunks Reported This Session", st.session_state.total_chunks),
    ("Questions Asked This Session", sum(m["role"] == "user" for m in st.session_state.messages)),
]
for column, (label, value) in zip((m1, m2, m3), metrics):
    with column:
        st.markdown(
            f'<div class="metric-card"><div class="metric-label">{label}</div>'
            f'<div class="metric-value">{value}</div></div>',
            unsafe_allow_html=True,
        )

st.divider()
left, right = st.columns([1, 1.6], gap="large")

with left:
    st.markdown('<div class="section-title">📁 Knowledge Base</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="info-panel">Upload PDF, DOCX, or TXT documents to make '
        'their contents searchable by the AI assistant.</div>',
        unsafe_allow_html=True,
    )
    uploaded_file = st.file_uploader("Choose a document", type=["pdf", "docx", "txt"])

    if st.button("⬆ Upload & Index", type="primary", use_container_width=True):
        if uploaded_file is None:
            st.warning("Please choose a document first.")
        else:
            try:
                with st.spinner("Uploading and indexing..."):
                    response = requests.post(
                        UPLOAD_URL,
                        files={"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)},
                        timeout=120,
                    )
                    response.raise_for_status()
                    result = response.json()
                filename = result.get("filename", uploaded_file.name)
                chunks = result.get("chunks", 0)
                st.session_state.indexed_documents.append(filename)
                if isinstance(chunks, int):
                    st.session_state.total_chunks += chunks
                st.success(f"{filename} indexed successfully!")
            except requests.HTTPError as exc:
                detail = exc.response.text[:500] if exc.response is not None else str(exc)
                st.error(f"Upload failed: {detail}")
            except requests.RequestException as exc:
                st.error(f"Upload failed: {exc}")
            except ValueError:
                st.error("Backend returned invalid JSON during upload.")

    st.divider()
    st.subheader("Session Uploads")
    if st.session_state.indexed_documents:
        for filename in st.session_state.indexed_documents:
            st.markdown(f"📄 {filename}")
    else:
        st.info("No documents uploaded in this session.")

with right:
    st.markdown('<div class="section-title">💬 AI Knowledge Assistant</div>', unsafe_allow_html=True)
    st.caption("Ask questions about indexed documents. Answers may include source citations.")
    chat_area = st.container(height=440)
    with chat_area:
        if not st.session_state.messages:
            st.info("Welcome! Upload a document and ask your first question.")
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if message["role"] == "assistant":
                    citations = message.get("citations", [])
                    if citations:
                        with st.expander(f"📚 Sources ({len(citations)})"):
                            for citation in citations:
                                details = [str(citation.get("source", "Unknown source"))]
                                if citation.get("page") is not None:
                                    details.append(f"Page {citation['page']}")
                                if citation.get("chunk_id") is not None:
                                    details.append(f"Chunk {citation['chunk_id']}")
                                st.write(" • ".join(details))

    question = st.chat_input("Ask a question about your documents...")
    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        try:
            with st.spinner("Searching knowledge base..."):
                response = requests.post(ASK_URL, json={"question": question}, timeout=60)
                response.raise_for_status()
                result = response.json()
            st.session_state.messages.append({
                "role": "assistant",
                "content": result.get("answer", "No answer returned."),
                "citations": result.get("citations", []),
            })
        except requests.HTTPError as exc:
            detail = exc.response.text[:500] if exc.response is not None else str(exc)
            st.session_state.messages.append({
                "role": "assistant", "content": f"Backend error: {detail}", "citations": []
            })
        except requests.RequestException as exc:
            st.session_state.messages.append({
                "role": "assistant", "content": f"Unable to contact the RAG backend: {exc}", "citations": []
            })
        except ValueError:
            st.session_state.messages.append({
                "role": "assistant", "content": "The backend returned invalid JSON.", "citations": []
            })
        st.rerun()
