import re

from app.resume.ml_skill_extractor import (
    extract_ml_skills,
)

from app.resume.skill_normalizer import (
    normalize_skills,
)


# ============================================================
# FALLBACK SKILLS DATABASE
# ============================================================
#
# ESCO taxonomy is used for normalization.
# This list is kept as a fallback for technologies that may
# not be present in ESCO.
#

SKILLS_DATABASE = [

    # Programming Languages
    "python",
    "java",
    "c++",
    "c",
    "c#",
    "javascript",
    "typescript",
    "go",
    "kotlin",
    "swift",

    # Frontend
    "html",
    "css",
    "react",
    "react.js",
    "reactjs",
    "angular",
    "vue",
    "next.js",
    "nextjs",
    "tailwind css",

    # Backend
    "node.js",
    "nodejs",
    "fastapi",
    "django",
    "flask",
    "spring boot",
    "spring",
    "express.js",
    "express",
    "servlets",
    "jsp",

    # Databases
    "sql",
    "mysql",
    "postgresql",
    "postgres",
    "mongodb",
    "sqlite",
    "oracle",
    "redis",

    # Cloud
    "aws",
    "azure",
    "gcp",
    "google cloud",

    # DevOps / Tools
    "docker",
    "kubernetes",
    "git",
    "github",
    "gitlab",
    "jenkins",
    "linux",

    # AI / ML
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "natural language processing",
    "nlp",
    "computer vision",
    "tensorflow",
    "pytorch",
    "scikit-learn",
    "pandas",
    "numpy",
    "xgboost",
    "faiss",
    "transformers",

    # Testing
    "selenium",
    "playwright",
    "testing",
    "api testing",
    "unit testing",
    "integration testing",
    "postman",

    # APIs
    "rest api",
    "rest apis",
    "restful api",
    "restful apis",
    "graphql",

    # Security / Other
    "jwt",
    "oauth",
    "spring security",
]


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(text: str) -> str:
    """
    Normalize line endings and repeated whitespace.
    """

    if not text:
        return ""

    text = (
        text
        .replace("\r\n", "\n")
        .replace("\r", "\n")
    )

    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# SKILL REGEX
# ============================================================

def build_skill_pattern(
    skill: str
) -> re.Pattern:
    """
    Build a safe regex pattern for a skill.

    This prevents:
        c  -> matching css
        java -> matching javascript

    while still supporting:
        c++
        c#
        node.js
        next.js
    """

    escaped_skill = re.escape(
        skill
    )

    return re.compile(
        rf"(?<![A-Za-z0-9+#])"
        rf"{escaped_skill}"
        rf"(?![A-Za-z0-9+#])",
        re.IGNORECASE,
    )


# ============================================================
# EXTRACT RAW SKILLS
# ============================================================

def extract_skills(
    text: str
) -> list[str]:
    """
    Extract skills from the resume text.

    This is the raw extraction stage.
    """

    if not text:
        return []


    normalized_text = normalize_text(
        text
    )


    found_skills: list[str] = []


    # Longer skills first.
    sorted_skills = sorted(
        SKILLS_DATABASE,
        key=len,
        reverse=True,
    )


    for skill in sorted_skills:

        pattern = build_skill_pattern(
            skill
        )


        if pattern.search(
            normalized_text
        ):

            found_skills.append(
                skill
            )


    return found_skills


# ============================================================
# NORMALIZED SKILLS
# ============================================================

def extract_normalized_skills(
    text: str
) -> list[str]:
    """
    Extract skills using the trained DistilBERT model,
    then normalize them using the strict TalentHive
    skill vocabulary.
    """

    if not text or not text.strip():
        return []


    # --------------------------------------------------------
    # 1. AI MODEL EXTRACTION
    # --------------------------------------------------------

    raw_skills = extract_ml_skills(
        text
    )


    if not raw_skills:
        return []


    # --------------------------------------------------------
    # 2. TALENTHIVE NORMALIZATION
    # --------------------------------------------------------

    normalized_skills = (
        normalize_skills(
            raw_skills
        )
    )


    # --------------------------------------------------------
    # 3. FINAL DEDUPLICATION
    # --------------------------------------------------------

    result = []

    seen = set()


    for skill in normalized_skills:

        if not isinstance(
            skill,
            str
        ):
            continue


        skill = skill.strip()


        if not skill:
            continue


        key = skill.lower()


        if key in seen:
            continue


        seen.add(
            key
        )


        result.append(
            skill
        )


    return sorted(
        result,
        key=lambda value:
            value.lower()
    )



# ============================================================
# EXPERIENCE
# ============================================================

def extract_experience(
    text: str
) -> str | None:
    """
    Extract years of professional experience.
    """

    if not text:
        return None


    patterns = [

        r"(\d+(?:\.\d+)?)\+?\s*"
        r"(?:years|year|yrs|yr)"
        r"\s*(?:of)?\s*experience",

        r"experience\s*[:\-]?\s*"
        r"(\d+(?:\.\d+)?)\+?\s*"
        r"(?:years|year|yrs|yr)",

        r"(\d+(?:\.\d+)?)\+?\s*"
        r"years\s+(?:of\s+)?experience",

    ]


    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE,
        )


        if match:

            return match.group(1)


    if re.search(
        r"\bfresher\b|\brecent graduate\b",
        text,
        re.IGNORECASE,
    ):

        return "0"


    return None


# ============================================================
# EDUCATION
# ============================================================

def extract_education(
    text: str
) -> str | None:
    """
    Extract the EDUCATION section.

    Returns:
        degree + specialization
        institution
        CGPA
        percentage
        graduation year
    """

    if not text:
        return None


    text = (
        text
        .replace("\r\n", "\n")
        .replace("\r", "\n")
    )


    lines = [

        line.strip()

        for line in text.split("\n")

        if line.strip()

    ]


    # --------------------------------------------------------
    # Find EDUCATION heading
    # --------------------------------------------------------

    education_start = None


    for index, line in enumerate(
        lines
    ):

        normalized = (
            line.lower().strip()
        )


        if normalized in {
            "education",
            "educational qualification",
            "academic qualification",
            "academic qualifications",
        }:

            education_start = index + 1

            break


    if education_start is None:
        return None


    # --------------------------------------------------------
    # Stop at next major section
    # --------------------------------------------------------

    section_headings = {
        "experience",
        "work experience",
        "professional experience",
        "internship",
        "skills",
        "technical skills",
        "projects",
        "achievements",
        "achievements & experience",
        "certifications",
        "certifications & courses",
        "publications",
        "interests",
    }


    education_lines: list[str] = []


    for line in lines[
        education_start:
    ]:

        normalized = (
            line.lower().strip()
        )


        if normalized in section_headings:
            break


        education_lines.append(
            line
        )


    if not education_lines:
        return None


    education_text = "\n".join(
        education_lines
    )


    # ========================================================
    # DEGREE + SPECIALIZATION
    # ========================================================

    degree_match = re.search(
        r"\b("
        r"B\.?\s*E\.?"
        r"|B\.?\s*Tech"
        r"|M\.?\s*E\.?"
        r"|M\.?\s*Tech"
        r"|B\.?\s*Sc"
        r"|B\.?\s*C\.?\s*A\.?"
        r"|M\.?\s*C\.?\s*A\.?"
        r"|MBA"
        r")\b"
        r"(?:\s+in\s+|\s+of\s+)?"
        r"([A-Za-z &,\-]+)?",
        education_text,
        re.IGNORECASE,
    )


    degree_text = None


    if degree_match:

        degree_text = (
            degree_match
            .group(0)
            .strip()
        )


        degree_text = re.sub(
            r"\s+",
            " ",
            degree_text,
        )


    # ========================================================
    # INSTITUTION
    # ========================================================

    institution = None


    for line in education_lines:

        if re.search(
            r"(institute|institution|college|university|school)",
            line,
            re.IGNORECASE,
        ):

            institution = re.sub(
                r"\s*\|\s*.*$",
                "",
                line,
            ).strip()

            break


    # ========================================================
    # CGPA
    # ========================================================

    cgpa = None


    cgpa_match = re.search(
        r"(?:CGPA|C\.G\.P\.A\.?)"
        r"\s*[:\-]?\s*"
        r"(\d+(?:\.\d+)?)"
        r"(?:\s*/\s*(\d+(?:\.\d+)?))?",
        education_text,
        re.IGNORECASE,
    )


    if cgpa_match:

        cgpa_value = (
            cgpa_match.group(1)
        )

        cgpa_scale = (
            cgpa_match.group(2)
        )


        if cgpa_scale:

            cgpa = (
                f"{cgpa_value}/"
                f"{cgpa_scale}"
            )

        else:

            cgpa = (
                cgpa_value
            )


    # ========================================================
    # PERCENTAGE
    # ========================================================

    percentage = None


    percentage_match = re.search(
        r"(\d+(?:\.\d+)?)\s*%",
        education_text,
        re.IGNORECASE,
    )


    if percentage_match:

        percentage = (
            f"{percentage_match.group(1)}%"
        )


    # ========================================================
    # GRADUATION YEAR
    # ========================================================

    year = None


    year_match = re.search(
        r"\b(19|20)\d{2}\b",
        education_text,
    )


    if year_match:

        year = (
            year_match.group(0)
        )


    # ========================================================
    # FORMAT RESULT
    # ========================================================

    result: list[str] = []


    if degree_text:
        result.append(
            degree_text
        )


    if institution:
        result.append(
            institution
        )


    if cgpa:
        result.append(
            f"CGPA: {cgpa}"
        )


    if percentage:
        result.append(
            f"Percentage: {percentage}"
        )


    if year:
        result.append(
            f"Year: {year}"
        )


    if result:

        return " | ".join(
            result
        )


    return education_text


# ============================================================
# PROJECTS
# ============================================================

def extract_projects(
    text: str
) -> list[dict]:
    """
    Extract:

        project title
        technology stack

    Descriptions are ignored.
    """

    if not text:
        return []


    text = (
        text
        .replace("\r\n", "\n")
        .replace("\r", "\n")
    )


    # --------------------------------------------------------
    # Find PROJECTS section
    # --------------------------------------------------------

    start_match = re.search(
        r"(?im)^\s*"
        r"(?:projects?|academic projects?|"
        r"key projects?|personal projects?)"
        r"\s*:?\s*$",
        text,
    )


    if not start_match:
        return []


    remaining = text[
        start_match.end():
    ]


    # --------------------------------------------------------
    # Stop at next major section
    # --------------------------------------------------------

    end_match = re.search(
        r"(?im)^\s*"
        r"(?:education|experience|"
        r"work experience|"
        r"professional experience|"
        r"achievements(?:\s*&\s*experience)?|"
        r"certifications?|"
        r"technical skills|"
        r"skills|"
        r"internship|"
        r"publications?|"
        r"interests?)"
        r"\s*:?\s*$",
        remaining,
    )


    if end_match:

        projects_text = (
            remaining[
                :end_match.start()
            ]
        )

    else:

        projects_text = remaining


    # --------------------------------------------------------
    # Clean lines
    # --------------------------------------------------------

    lines = [

        line.strip()

        for line in projects_text.split("\n")

        if line.strip()

    ]


    projects: list[dict] = []


    current_project = None


    for line in lines:

        # ----------------------------------------------------
        # Technologies
        # ----------------------------------------------------

        tech_match = re.match(
            r"^technologies?\s*:\s*(.+)$",
            line,
            re.IGNORECASE,
        )


        if tech_match:

            if current_project is not None:

                tech_text = (
                    tech_match.group(1)
                )


                current_project[
                    "tech_stack"
                ] = [

                    tech.strip()

                    for tech in
                    tech_text.split(",")

                    if tech.strip()

                ]


            continue


        # ----------------------------------------------------
        # Ignore bullet descriptions
        # ----------------------------------------------------

        if re.match(
            r"^[●•▪◦\-]",
            line,
        ):

            continue


        # ----------------------------------------------------
        # Ignore standalone technology lines
        # ----------------------------------------------------

        if line.lower().startswith(
            (
                "technologies:",
                "technology:",
            )
        ):

            continue


        # ----------------------------------------------------
        # Project title
        # ----------------------------------------------------

        if len(line) <= 120:

            current_project = {
                "title": line,
                "tech_stack": [],
            }


            projects.append(
                current_project
            )


    return projects


# ============================================================
# MAIN RESUME ANALYZER
# ============================================================

def analyze_resume(
    text: str
) -> dict:
    """
    Main resume analysis function.

    Pipeline:

        Resume text
             ↓
        Raw skill extraction
             ↓
        ESCO skill normalization
             ↓
        Experience extraction
             ↓
        Education extraction
             ↓
        Project extraction
    """

    # --------------------------------------------------------
    # Skills
    # --------------------------------------------------------

    skills = extract_normalized_skills(
        text
    )


    # --------------------------------------------------------
    # Experience
    # --------------------------------------------------------

    experience = extract_experience(
        text
    )


    # --------------------------------------------------------
    # Education
    # --------------------------------------------------------

    education = extract_education(
        text
    )


    # --------------------------------------------------------
    # Projects
    # --------------------------------------------------------

    projects = extract_projects(
        text
    )


    return {
        "skills": skills,
        "experience": experience,
        "education": education,
        "projects": projects,
    }