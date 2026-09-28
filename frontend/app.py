import requests
import streamlit as st


API_URL = "http://api:8000"

st.set_page_config(
    page_title="Enterprise RAG Assistant",
    page_icon="🤖",
    layout="centered",
)

st.title("Enterprise RAG Assistant")
st.caption("Ask questions grounded in your enterprise documents.")

question = st.text_input(
    "Ask a question",
    placeholder="e.g. How many paid annual leave days do employees receive?",
)

if st.button("Ask", type="primary") and question:

    try:
        response = requests.post(
            f"{API_URL}/ask",
            json={"question": question},
            timeout=60,
        )

        response.raise_for_status()
        result = response.json()

        st.subheader("Answer")
        st.write(result["answer"])

        st.subheader("Citations")

        citations = result.get("citations", [])

        if not citations:
            st.write("No supporting citations.")

        else:
            for citation in citations:
                source = citation["source"]
                chunk_id = citation.get("chunk_id")
                page = citation.get("page")

                citation_text = source

                if page is not None:
                    citation_text += f" — page {page}"

                if chunk_id is not None:
                    citation_text += f" — chunk {chunk_id}"

                st.write(f"- {citation_text}")

    except requests.RequestException as exc:
        st.error(f"Unable to contact RAG API: {exc}")