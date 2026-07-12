from langchain_huggingface import HuggingFaceEmbeddings


def get_embedding_model():

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    return embeddings


# 👇 File chivarilo add cheyyi
if __name__ == "__main__":

    embedding_model = get_embedding_model()

    print("Embedding model loaded successfully!")