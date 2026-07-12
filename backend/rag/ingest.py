from loader import load_pdf
from chunker import split_documents
from embedder import get_embedding_model
from vector_store import create_vector_store


def ingest_documents():

    print("Loading PDF...")

    documents = load_pdf("knowledge_base/Amazon_Return_Policy.pdf")

    print(f"Loaded {len(documents)} pages.")

    print("Splitting into chunks...")

    chunks = split_documents(documents)

    print(f"Created {len(chunks)} chunks.")

    print("Loading embedding model...")

    embedding_model = get_embedding_model()

    print("Creating ChromaDB...")

    create_vector_store(chunks, embedding_model)

    print("Knowledge Base Created Successfully!")


if __name__ == "__main__":
    ingest_documents()