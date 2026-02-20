import streamlit as st
import uuid
import os

from loader import load_documents
from chunker import chunk_text
from embedder import generate_embeddings
from vector_store import store_embeddings
from retriever import retrieve_context
from generator import generate_answer
from keyword_retriever import KeywordRetriever

# ---------- Streamlit Page Config ----------
st.set_page_config(
    page_title="RAG Knowledge Assistant",
    page_icon="📚",
    layout="wide"
)

st.title("📚 RAG Knowledge Assistant")

# ---------- Session State ----------
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

if "indexed_files" not in st.session_state:
    st.session_state.indexed_files = set()

if "keyword_retriever" not in st.session_state:
    st.session_state.keyword_retriever = None


# ---------- PDF Upload ----------
uploaded_file = st.sidebar.file_uploader(
    "Upload PDF",
    type=["pdf"]
)

if uploaded_file is not None:

    filename = uploaded_file.name
    filepath = os.path.join("data", filename)

    if filename not in st.session_state.indexed_files:

        os.makedirs("data", exist_ok=True)

        with open(filepath, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.sidebar.info("Indexing document...")

        docs = load_documents(filepath)
        chunks = chunk_text(docs)

        embeddings = generate_embeddings(chunks)
        store_embeddings(chunks, embeddings, filename)

        st.session_state.keyword_retriever = KeywordRetriever(chunks)

        st.session_state.indexed_files.add(filename)

        st.sidebar.success("Document indexed successfully!")

    else:
        st.sidebar.info("Document already indexed.")


# ---------- Select PDF ----------
pdf_files = os.listdir("data") if os.path.exists("data") else []

selected_pdf = None

if pdf_files:
    selected_pdf = st.sidebar.selectbox(
        "Select Document",
        pdf_files
    )


# ---------- Display Chat History ----------
for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):
        st.write(msg["content"])


# ---------- Chat Input ----------
if prompt := st.chat_input("Ask a question..."):

    if selected_pdf is None:
        st.warning("Please upload and select a document first.")
        st.stop()

    # Show user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.write(prompt)

    # Retrieve context
    result = retrieve_context(
        prompt,
        st.session_state.keyword_retriever,
        selected_pdf
    )

    if result is None:

        answer = "I could not find relevant information in the document."

    else:

        context = result["context"]

        answer = generate_answer(prompt, context)

    # Show assistant message
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })

    with st.chat_message("assistant"):
        st.write(answer)