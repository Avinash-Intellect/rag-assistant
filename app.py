from loader import load_documents
from chunker import chunk_text
from embedder import generate_embeddings
from vector_store import store_embeddings
from keyword_retriever import KeywordRetriever
from retriever import retrieve_context
from generator import generate_answer
from memory import ConversationMemory
from query_augmented import augment_query


def main():

    memory = ConversationMemory()

    print("📚 Placement RAG Assistant")
    print("Indexing documents...\n")

    # Load + chunk
    docs = load_documents("data")
    chunks = chunk_text(docs)

    # Embed + store
    embeddings = generate_embeddings(chunks)
    store_embeddings(chunks, embeddings)

    # Initialize keyword retriever
    keyword_retriever = KeywordRetriever(chunks)

    print("Ready! Type 'exit' to quit.\n")

    while True:

        question = input("Ask a question: ")

        if question.lower() == "exit":
            break

        # Get memory context
        memory_context = memory.get_context()

        # Augment query
        standalone_question = augment_query(question, memory_context)

        print("Standalone query:", standalone_question)

        result = retrieve_context(standalone_question, keyword_retriever)

        if result is None:
            print("I could not find relevant information.")
            continue

        context = result["context"]
        sources = result["sources"]

        answer = generate_answer(standalone_question, context)

        print("\nAnswer:\n", answer)

        print("\nSources:")
        for src in sources:
            print(f"[{src['index']}] {src['source']} (Page {src['page']})")

        # Store memory
        memory.add(question, answer)


if __name__ == "__main__":
    main()
