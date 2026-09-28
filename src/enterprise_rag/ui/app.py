import requests
import streamlit as st

from enterprise_rag.core.config import API_URL

ASK_URL = f"{API_URL}/ask"
UPLOAD_URL = f"{API_URL}/documents/upload"


st.set_page_config(
    page_title="Enterprise RAG Assistant",
    page_icon="📚",
    layout="centered",
)


st.title("📚 Enterprise RAG Assistant")

st.caption(
    "Ask questions about your enterprise documents."
)

with st.sidebar:

    st.header("📁 Documents")

    uploaded_file = st.file_uploader(
        "Upload a document",
        type=["txt", "pdf", "docx"],
    )

    if st.button(
        "Upload & Index",
        use_container_width=True,
    ):

        if uploaded_file is None:

            st.warning(
                "Please choose a document first."
            )

        else:

            try:

                with st.spinner(
                    "Uploading and indexing..."
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
                    f"{result['filename']} "
                    f"uploaded and indexed successfully."
                )

                st.write(
                    f"Knowledge base chunks: "
                    f"{result['chunks']}"
                )

            except requests.RequestException as error:

                st.error(
                    f"Upload failed: {error}"
                )
# Store conversation history
if "messages" not in st.session_state:
    st.session_state.messages = []


# Display previous messages
for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        if message.get("citations"):

            with st.expander("Sources"):

                for citation in message["citations"]:

                    source = citation["source"]

                    chunk_id = citation.get(
                        "chunk_id"
                    )

                    page = citation.get(
                        "page"
                    )

                    text = source

                    if page is not None:
                        text += f" — Page {page}"

                    if chunk_id is not None:
                        text += f" — Chunk {chunk_id}"

                    st.write(text)


# Chat input
question = st.chat_input(
    "Ask about company policies..."
)


if question:

    # Save user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message("user"):
        st.markdown(question)

    # Call FastAPI
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

        answer = result["answer"]

        citations = result.get(
            "citations",
            []
        )

        # Display assistant response
        with st.chat_message("assistant"):

            st.markdown(answer)

            if citations:

                with st.expander("Sources"):

                    for citation in citations:

                        source = citation["source"]

                        page = citation.get("page")
                        chunk_id = citation.get(
                            "chunk_id"
                        )

                        text = source

                        if page is not None:
                            text += f" — Page {page}"

                        if chunk_id is not None:
                            text += (
                                f" — Chunk {chunk_id}"
                            )

                        st.write(text)

        # Save assistant message
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer,
                "citations": citations,
            }
        )

    except requests.RequestException:

        st.error(
            "Could not connect to the RAG API. "
            "Make sure the FastAPI server is running."
        )