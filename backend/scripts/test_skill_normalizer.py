from app.resume.skill_normalizer import (
    normalize_skills,
)


skills = [
    "Python",
    "python 3",
    "React",
    "React.js",
    "ReactJS",
    "FastAPI",
    "fast api",
    "SQL",
]


result = normalize_skills(
    skills
)


print("Original:")
print(skills)

print("\nNormalized:")
print(result)