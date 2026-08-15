from app.ml.pipeline.recommendation_scoring import (
    calculate_final_score,
    calculate_skill_match,
    calculate_experience_match,
    calculate_education_match,
)


# ============================================================
# JOB
# ============================================================

JOB_REQUIRED_SKILLS = (
    "Python, FastAPI, PostgreSQL, REST API, Docker"
)

JOB_EXPERIENCE_MIN = 2
JOB_EXPERIENCE_MAX = 4

JOB_EDUCATION = (
    "Bachelor of Engineering"
)


# ============================================================
# TEST CANDIDATES
# ============================================================

candidates = [

    {
        "name": "Candidate A",

        "semantic": 0.90,

        "skills":
            "Python, FastAPI, PostgreSQL, REST API, Docker",

        "experience": "3",

        "education":
            "Bachelor of Engineering",
    },

    {
        "name": "Candidate B",

        "semantic": 0.84,

        "skills":
            "Python, FastAPI, REST API",

        "experience": "2",

        "education":
            "Bachelor of Engineering",
    },

    {
        "name": "Candidate C",

        "semantic": 0.88,

        "skills":
            "Java, Spring Boot, MySQL",

        "experience": "4",

        "education":
            "Bachelor of Engineering",
    },

    {
        "name": "Candidate D",

        "semantic": 0.72,

        "skills":
            "Python, SQL",

        "experience": "1",

        "education":
            "Diploma",
    },
]


# ============================================================
# RANK
# ============================================================

ranked = []


for candidate in candidates:

    skill_score = calculate_skill_match(
        candidate["skills"],
        JOB_REQUIRED_SKILLS,
    )

    experience_score = (
        calculate_experience_match(
            candidate["experience"],
            JOB_EXPERIENCE_MIN,
            JOB_EXPERIENCE_MAX,
        )
    )

    education_score = (
        calculate_education_match(
            candidate["education"],
            JOB_EDUCATION,
        )
    )

    final_score = calculate_final_score(
        semantic_score=candidate["semantic"],
        skill_score=skill_score,
        experience_score=experience_score,
        education_score=education_score,
    )

    ranked.append(
        {
            "name":
                candidate["name"],

            "semantic_score":
                candidate["semantic"],

            "skill_score":
                skill_score,

            "experience_score":
                experience_score,

            "education_score":
                education_score,

            "final_score":
                final_score,
        }
    )


# ============================================================
# SORT
# ============================================================

ranked.sort(
    key=lambda item:
        item["final_score"],
    reverse=True,
)


# ============================================================
# PRINT
# ============================================================

print("=" * 70)
print("TalentHive Candidate Ranking Test")
print("=" * 70)

print()

for rank, candidate in enumerate(
    ranked,
    start=1,
):

    print(
        f"{rank}. {candidate['name']}"
    )

    print(
        f"   Semantic   : "
        f"{candidate['semantic_score']:.4f}"
    )

    print(
        f"   Skills     : "
        f"{candidate['skill_score']:.4f}"
    )

    print(
        f"   Experience : "
        f"{candidate['experience_score']:.4f}"
    )

    print(
        f"   Education  : "
        f"{candidate['education_score']:.4f}"
    )

    print(
        f"   FINAL      : "
        f"{candidate['final_score']:.4f}"
    )

    print()


print("=" * 70)
print("Ranking test complete.")
print("=" * 70)