import streamlit as st
import requests
import uuid
import os

# ========================
# Backend URLs
# ========================

API_URL = "http://127.0.0.1:8000/ask-stream"
UPLOAD_URL = "http://127.0.0.1:8000/upload-pdf"


# ========================
# Page Config
# ========================

st.set_page_config(
    page_title="RAG Assistant",
    page_icon="📚",
    layout="wide"
)

st.title("📚 RAG Knowledge Assistant")


# ========================
# Session Initialization
# ========================

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_pdf" not in st.session_state:
    st.session_state.selected_pdf = None


# ========================
# Sidebar Upload
# ========================

st.sidebar.header("📂 Document Manager")

# Initialize uploaded files tracker
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = set()


uploaded_file = st.sidebar.file_uploader(
    "Upload PDF",
    type=["pdf"]
)

if uploaded_file:

    # Upload only if not already uploaded
    if uploaded_file.name not in st.session_state.uploaded_files:

        try:

            upload_response = requests.post(
                UPLOAD_URL,
                files={"file": (uploaded_file.name, uploaded_file.getvalue())}
            )

            if upload_response.status_code == 200:

                st.sidebar.success(f"{uploaded_file.name} uploaded & indexed")

                # Mark as uploaded
                st.session_state.uploaded_files.add(uploaded_file.name)

            else:

                st.sidebar.error(upload_response.text)

        except Exception as e:

            st.sidebar.error(f"Upload failed: {e}")



# ========================
# Sidebar PDF Selector
# ========================

pdf_files = []

if os.path.exists("data"):
    pdf_files = [f for f in os.listdir("data") if f.endswith(".pdf")]

if pdf_files:

    st.session_state.selected_pdf = st.sidebar.selectbox(
        "Select PDF",
        pdf_files,
        index=pdf_files.index(st.session_state.selected_pdf)
        if st.session_state.selected_pdf in pdf_files else 0
    )

else:

    st.sidebar.warning("Upload a PDF first")


# ========================
# Display Chat History
# ========================

for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):

        # CRITICAL FIX: use markdown instead of write
        st.markdown(msg["content"], unsafe_allow_html=True)


# ========================
# Chat Input
# ========================

prompt = st.chat_input("Ask a question...")

if prompt:

    if not st.session_state.selected_pdf:

        st.error("Please upload and select a PDF first")
        st.stop()


    # Show user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):
        st.markdown(prompt)


    payload = {
        "question": prompt,
        "session_id": st.session_state.session_id,
        "pdf_name": st.session_state.selected_pdf
    }


    with st.chat_message("assistant"):

        placeholder = st.empty()

        full_response = ""

        try:

            response = requests.post(
                API_URL,
                json=payload,
                stream=True,
                timeout=120
            )

            if response.status_code != 200:

                full_response = f"Backend error: {response.text}"

                placeholder.markdown(full_response)

            else:

                # Stream response properly
                for chunk in response.iter_content(chunk_size=512):

                    if chunk:

                        text = chunk.decode("utf-8")

                        full_response += text

                        # FIX: Proper markdown rendering
                        placeholder.markdown(
                            full_response,
                            unsafe_allow_html=True
                        )

        except Exception as e:

            full_response = f"Connection error: {e}"

            placeholder.markdown(full_response)


    # Save assistant response
    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response
    })
