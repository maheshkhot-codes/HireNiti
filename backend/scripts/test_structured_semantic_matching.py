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

    return sum(
        a * b
        for a, b in zip(
            vector_a,
            vector_b,
        )
    )


# ============================================================
# STRUCTURED TEXT BUILDER
# ============================================================

def build_resume_text(
    skills: str,
    experience: str,
    education: str,
    projects: str = "",
) -> str:

    return f"""
Candidate Skills:
{skills}

Professional Experience:
{experience}

Education:
{education}

Projects:
{projects}
""".strip()


def build_job_text(
    title: str,
    description: str,
    required_skills: str,
    preferred_skills: str = "",
    experience: str = "",
    education: str = "",
) -> str:

    return f"""
Job Title:
{title}

Job Description:
{description}

Required Skills:
{required_skills}

Preferred Skills:
{preferred_skills}

Required Experience:
{experience}

Education:
{education}
""".strip()


# ============================================================
# TEST DATA
# ============================================================

resume = build_resume_text(
    skills="""
    Python, FastAPI, REST API, PostgreSQL,
    Docker, AWS
    """,

    experience="""
    2 years of experience developing backend APIs
    and scalable web services using Python.
    """,

    education="""
    Bachelor of Engineering
    """,

    projects="""
    AI recruitment platform using FastAPI,
    PostgreSQL, embeddings and REST APIs.
    """,
)


strong_job = build_job_text(
    title="Python Backend Developer",

    description="""
    Build scalable backend services and REST APIs
    for a cloud-based application.
    """,

    required_skills="""
    Python, FastAPI, PostgreSQL, REST API, Docker
    """,

    preferred_skills="AWS",

    experience="1-3 years",

    education="Bachelor's degree",
)


different_job = build_job_text(
    title="Java Backend Developer",

    description="""
    Develop enterprise applications using Java
    and the Spring Boot ecosystem.
    """,

    required_skills="""
    Java, Spring Boot, Hibernate, Maven, MySQL
    """,

    preferred_skills="AWS",

    experience="2-4 years",

    education="Bachelor's degree",
)


unrelated_job = build_job_text(
    title="HVAC Engineer",

    description="""
    Design and maintain heating, ventilation and
    air-conditioning systems for commercial buildings.
    """,

    required_skills="""
    HVAC, AutoCAD, mechanical systems
    """,

    preferred_skills="Primavera",

    experience="2-5 years",

    education="Mechanical Engineering",
)


# ============================================================
# GENERATE EMBEDDINGS
# ============================================================

resume_vector = generate_embedding(
    resume
)

strong_vector = generate_embedding(
    strong_job
)

different_vector = generate_embedding(
    different_job
)

unrelated_vector = generate_embedding(
    unrelated_job
)


# ============================================================
# RESULTS
# ============================================================

print("=" * 60)
print("TalentHive Structured Semantic Matching Test")
print("=" * 60)


scores = {
    "Strong backend match":
        cosine_similarity(
            resume_vector,
            strong_vector,
        ),

    "Related but different":
        cosine_similarity(
            resume_vector,
            different_vector,
        ),

    "Clearly unrelated":
        cosine_similarity(
            resume_vector,
            unrelated_vector,
        ),
}


for name, score in scores.items():

    print(
        f"{name}: {score:.4f}"
    )


print(
    "\nExpected ordering:"
)

print(
    "Strong backend match > Related > Unrelated"
)

print(
    "\n" + "=" * 60
)