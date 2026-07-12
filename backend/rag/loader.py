from langchain_community.document_loaders import PyPDFLoader
from chunker import split_documents


def load_pdf(pdf_path):
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    return documents


if __name__ == "__main__":

    docs = load_pdf("knowledge_base/Amazon_Return_Policy.pdf")

    print(f"Pages Loaded: {len(docs)}")

    chunks = split_documents(docs)

    print(f"Chunks Created: {len(chunks)}")

    print("\nFirst Chunk:\n")

    print(chunks[0].page_content)