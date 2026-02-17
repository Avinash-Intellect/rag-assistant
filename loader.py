import os
from pypdf import PdfReader
import fitz


# ----------------------------
# Text Cleaning Function
# ----------------------------
def clean_text(text):
    """
    Performs light cleaning:
    - Remove extra spaces
    - Remove repeated newlines
    """
    text = text.replace("\n", " ")
    text = " ".join(text.split())
    return text


# ----------------------------
# Document Loader Function
# ----------------------------
def load_documents(path):

    documents = []

    # Case 1: path is a folder
    if os.path.isdir(path):

        for filename in os.listdir(path):

            if filename.endswith(".pdf"):

                file_path = os.path.join(path, filename)

                documents.extend(load_single_pdf(file_path))

    # Case 2: path is a single file
    elif os.path.isfile(path):

        documents.extend(load_single_pdf(path))

    return documents


def load_single_pdf(file_path):

    documents = []

    pdf = fitz.open(file_path)

    for page_num in range(len(pdf)):

        page = pdf[page_num]

        text = page.get_text()

        documents.append({

            "text": text,

            "metadata": {
                "source": os.path.basename(file_path),
                "page": page_num + 1
            }

        })

    return documents
