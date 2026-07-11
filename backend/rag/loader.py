from langchain_community.document_loaders import PyPDFLoader


def load_pdf(pdf_path):
    """
    Loads a PDF and returns its pages as LangChain documents.
    """

    loader = PyPDFLoader(pdf_path)
    documents = loader.load()

    return documents