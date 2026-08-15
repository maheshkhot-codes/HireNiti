from sentence_transformers import SentenceTransformer


# ---------------------------------------------------------
# Embedding model
# ---------------------------------------------------------

MODEL_NAME = "all-MiniLM-L6-v2"


# Load the model once when the application starts.
# We do not want to load it for every request.
model = SentenceTransformer(MODEL_NAME)


# ---------------------------------------------------------
# Generate embedding for one piece of text
# ---------------------------------------------------------

def generate_embedding(text: str) -> list[float]:

    if not text or not text.strip():
        return []

    embedding = model.encode(
        text,
        normalize_embeddings=True
    )

    return embedding.tolist()


# ---------------------------------------------------------
# Generate embeddings for multiple texts
# ---------------------------------------------------------

def generate_embeddings(
    texts: list[str]
) -> list[list[float]]:

    cleaned_texts = [
        text.strip()
        for text in texts
        if text and text.strip()
    ]

    if not cleaned_texts:
        return []

    embeddings = model.encode(
        cleaned_texts,
        normalize_embeddings=True
    )

    return embeddings.tolist()

def cosine_similarity(
    vector_a: list[float],
    vector_b: list[float]
) -> float:

    if not vector_a or not vector_b:
        return 0.0

    if len(vector_a) != len(vector_b):
        raise ValueError(
            "Vectors must have the same dimensions"
        )

    dot_product = sum(
        a * b
        for a, b in zip(
            vector_a,
            vector_b
        )
    )

    return float(dot_product)