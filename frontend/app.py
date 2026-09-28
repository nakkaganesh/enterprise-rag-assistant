import os

import requests
import streamlit as st


API_URL = os.getenv(
    "API_URL",
    "http://localhost:8000",
)

ASK_URL = f"{API_URL}/ask"
UPLOAD_URL = f"{API_URL}/documents/upload"


st.set_page_config(
    page_title="Enterprise RAG Assistant",
    page_icon="📚",
    layout="centered",
)


st.title("📚 Enterprise RAG Assistant")

st.caption(
    "Upload your documents and ask questions grounded in their content."
)


# -----------------------------
# Document Upload
# -----------------------------

st.subheader("📄 Upload Documents")

uploaded_file = st.file_uploader(
    "Upload a PDF, DOCX, or TXT document",
    type=["pdf", "docx", "txt"],
)

if st.button(
    "Upload & Index",
    type="primary",
    use_container_width=True,
):

    if uploaded_file is None:

        st.warning(
            "Please choose a document first."
        )

    else:

        try:

            with st.spinner(
                "Uploading and indexing document..."
            ):

                response = requests.post(
                    UPLOAD_URL,
                    files={
                        "file": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            uploaded_file.type,
                        )
                    },
                    timeout=120,
                )

                response.raise_for_status()

                result = response.json()

            st.success(
                f"✅ {result['filename']} uploaded "
                "and indexed successfully."
            )

            st.info(
                f"Knowledge base chunks: "
                f"{result['chunks']}"
            )

        except requests.RequestException as exc:

            st.error(
                f"Upload failed: {exc}"
            )


st.divider()


# -----------------------------
# Question Answering
# -----------------------------

st.subheader("💬 Ask Questions")

question = st.text_input(
    "Ask a question",
    placeholder=(
        "e.g. What does this document say "
        "about remote work?"
    ),
)


if st.button(
    "Ask",
    type="primary",
    use_container_width=True,
) and question:

    try:

        with st.spinner(
            "Searching documents..."
        ):

            response = requests.post(
                ASK_URL,
                json={
                    "question": question
                },
                timeout=60,
            )

            response.raise_for_status()

            result = response.json()

        st.subheader("Answer")

        st.write(
            result["answer"]
        )

        citations = result.get(
            "citations",
            [],
        )

        st.subheader("Sources")

        if not citations:

            st.write(
                "No supporting citations."
            )

        else:

            for citation in citations:

                source = citation["source"]

                page = citation.get(
                    "page"
                )

                chunk_id = citation.get(
                    "chunk_id"
                )

                citation_text = source

                if page is not None:

                    citation_text += (
                        f" — Page {page}"
                    )

                if chunk_id is not None:

                    citation_text += (
                        f" — Chunk {chunk_id}"
                    )

                st.write(
                    f"• {citation_text}"
                )

    except requests.RequestException as exc:

        st.error(
            f"Unable to contact RAG API: {exc}"
        )