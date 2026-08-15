from functools import lru_cache

from sentence_transformers import SentenceTransformer


# ============================================================
# EMBEDDING MODEL
# ============================================================

MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """
    Load the embedding model only when it is actually needed.

    The @lru_cache decorator makes sure the model is loaded
    only once per application process.
    """

    return SentenceTransformer(
        MODEL_NAME
    )


# ============================================================
# GENERATE ONE EMBEDDING
# ============================================================

def generate_embedding(
    text: str
) -> list[float]:

    if not text or not text.strip():
        return []

    model = get_embedding_model()

    embedding = model.encode(
        text,
        normalize_embeddings=True
    )

    return embedding.tolist()


# ============================================================
# GENERATE MULTIPLE EMBEDDINGS
# ============================================================

def generate_embeddings(
    texts: list[str]
) -> list[list[float]]:

    cleaned_texts = [
        text.strip()
        for text in texts
        if isinstance(text, str)
        and text.strip()
    ]

    if not cleaned_texts:
        return []

    model = get_embedding_model()

    embeddings = model.encode(
        cleaned_texts,
        normalize_embeddings=True
    )

    return embeddings.tolist()


# ============================================================
# COSINE SIMILARITY
# ============================================================

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