from app.ml.embeddings.embedder import (
    generate_embedding,
    cosine_similarity
)


resume_text = """
Python developer with experience in FastAPI,
REST APIs, SQL, React and machine learning.
"""


matching_job = """
Junior Python Developer.
Required:
Python, FastAPI, REST API, SQL and React.
Machine learning is preferred.
"""


different_job = """
Graphic Designer required.
Experience with Photoshop, Illustrator,
branding and visual design.
"""


resume_vector = generate_embedding(
    resume_text
)

matching_job_vector = generate_embedding(
    matching_job
)

different_job_vector = generate_embedding(
    different_job
)


matching_score = cosine_similarity(
    resume_vector,
    matching_job_vector
)

different_score = cosine_similarity(
    resume_vector,
    different_job_vector
)


print(
    "Similarity with matching job:",
    matching_score
)

print(
    "Similarity with different job:",
    different_score
)