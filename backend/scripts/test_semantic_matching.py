from app.ml.embeddings.embedder import generate_embedding


# ============================================================
# COSINE SIMILARITY
# ============================================================

def cosine_similarity(
    vector_a: list[float],
    vector_b: list[float],
) -> float:

    if not vector_a or not vector_b:
        return 0.0

    if len(vector_a) != len(vector_b):
        raise ValueError(
            "Embedding dimensions do not match."
        )

    # Embeddings are already normalized by the existing
    # embedder, so cosine similarity is simply the dot product.
    return sum(
        a * b
        for a, b in zip(
            vector_a,
            vector_b,
        )
    )


# ============================================================
# TEST CASES
# ============================================================

tests = [

    {
        "name": "Strong backend match",

        "resume": """
        Software Developer with experience in Python,
        FastAPI, REST APIs, PostgreSQL, Docker and AWS.
        Built scalable backend services and APIs.
        """,

        "job": """
        Backend Developer required with Python,
        FastAPI, REST API, PostgreSQL, Docker and AWS.
        Experience building backend web services.
        """,
    },

    {
        "name": "Related but different",

        "resume": """
        Java developer with Spring Boot, Hibernate,
        MySQL, REST APIs and Maven.
        """,

        "job": """
        Python backend engineer with FastAPI,
        PostgreSQL, Docker and AWS.
        """,
    },

    {
        "name": "Clearly unrelated",

        "resume": """
        Frontend developer specializing in React,
        TypeScript, HTML, CSS and Tailwind CSS.
        """,

        "job": """
        HVAC engineer responsible for mechanical systems,
        building maintenance and equipment design.
        """,
    },

]


# ============================================================
# RUN TESTS
# ============================================================

print("=" * 60)
print("TalentHive Semantic Matching Test")
print("=" * 60)


for test in tests:

    resume_embedding = (
        generate_embedding(
            test["resume"]
        )
    )

    job_embedding = (
        generate_embedding(
            test["job"]
        )
    )

    score = cosine_similarity(
        resume_embedding,
        job_embedding,
    )

    print(
        f"\n{test['name']}"
    )

    print(
        f"Semantic similarity: "
        f"{score:.4f}"
    )


print(
    "\n" + "=" * 60
)