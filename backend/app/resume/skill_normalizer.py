import json
import re
from functools import lru_cache
from pathlib import Path


# ============================================================
# PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

SKILLS_FILE = (
    BASE_DIR
    / "data"
    / "taxonomy"
    / "talenthive_skills.json"
)


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_text(
    value: str
) -> str:
    """
    Normalize a skill string for comparison.
    """

    if not isinstance(
        value,
        str,
    ):
        return ""

    value = value.lower().strip()

    value = re.sub(
        r"\s+",
        " ",
        value,
    )

    return value


def compact_text(
    value: str
) -> str:
    """
    Convert variations such as:

        React.js -> reactjs
        ReactJS  -> reactjs
        Spring Boot -> springboot
    """

    return re.sub(
        r"[^a-z0-9+#]+",
        "",
        normalize_text(value),
    )


# ============================================================
# MANUAL ALIASES
# ============================================================

ALIASES = {

    # --------------------------------------------------------
    # Python
    # --------------------------------------------------------

    "python3": "Python",
    "python 3": "Python",

    # --------------------------------------------------------
    # React
    # --------------------------------------------------------

    "reactjs": "React",
    "react.js": "React",

    # --------------------------------------------------------
    # Node
    # --------------------------------------------------------

    "nodejs": "Node.js",
    "node.js": "Node.js",

    # --------------------------------------------------------
    # Next
    # --------------------------------------------------------

    "nextjs": "Next.js",
    "next.js": "Next.js",

    # --------------------------------------------------------
    # Angular
    # --------------------------------------------------------

    "angular.js": "Angular",

    # --------------------------------------------------------
    # PostgreSQL
    # --------------------------------------------------------

    "postgres": "PostgreSQL",

    "postgres sql": "PostgreSQL",

    # --------------------------------------------------------
    # Scikit
    # --------------------------------------------------------

    "sklearn": "Scikit-learn",

    "scikit learn": "Scikit-learn",

    "scikit-learn": "Scikit-learn",

    # --------------------------------------------------------
    # REST
    # --------------------------------------------------------

    "rest": "REST API",

    "rest api": "REST API",

    "rest apis": "REST API",

    "restful api": "REST API",

    "restful apis": "REST API",

    # --------------------------------------------------------
    # Machine Learning
    # --------------------------------------------------------

    "ml": "Machine Learning",

    "machinelearning": "Machine Learning",

    "machine learning": "Machine Learning",

    # --------------------------------------------------------
    # Deep Learning
    # --------------------------------------------------------

    "dl": "Deep Learning",

    "deeplearning": "Deep Learning",

    # --------------------------------------------------------
    # Natural Language Processing
    # --------------------------------------------------------

    "nlp": "NLP",

    # --------------------------------------------------------
    # Artificial Intelligence
    # --------------------------------------------------------

    "ai": "Artificial Intelligence",

    "artificial intelligence": "Artificial Intelligence",

    # --------------------------------------------------------
    # FastAPI
    # --------------------------------------------------------

    "fast api": "FastAPI",

    "fastapi": "FastAPI",

    # --------------------------------------------------------
    # Spring Boot
    # --------------------------------------------------------

    "springboot": "Spring Boot",

    "spring boot": "Spring Boot",

    # --------------------------------------------------------
    # JavaScript
    # --------------------------------------------------------

    "js": "JavaScript",

    "javascript": "JavaScript",

    # --------------------------------------------------------
    # TypeScript
    # --------------------------------------------------------

    "ts": "TypeScript",

    "typescript": "TypeScript",

    # --------------------------------------------------------
    # C#
    # --------------------------------------------------------

    "c sharp": "C#",

    "c#": "C#",

    # --------------------------------------------------------
    # C++
    # --------------------------------------------------------

    "cpp": "C++",

    "c++": "C++",

    # --------------------------------------------------------
    # SQL
    #
    # IMPORTANT:
    # SQL must stay SQL.
    # Do NOT map SQL -> SQL Server.
    # --------------------------------------------------------

    "sql": "SQL",

    # --------------------------------------------------------
    # MySQL
    # --------------------------------------------------------

    "mysql": "MySQL",

    # --------------------------------------------------------
    # Microsoft Excel
    # --------------------------------------------------------

    "ms excel": "Excel",

    "microsoft excel": "Excel",

    # --------------------------------------------------------
    # Power BI
    # --------------------------------------------------------

    "powerbi": "Power BI",

    "power bi": "Power BI",

    # --------------------------------------------------------
    # GitHub
    # --------------------------------------------------------

    "github": "GitHub",

    # --------------------------------------------------------
    # GitLab
    # --------------------------------------------------------

    "gitlab": "GitLab",

}


# ============================================================
# LOAD TALENTHIVE TAXONOMY
# ============================================================

@lru_cache(maxsize=1)
def load_skill_taxonomy() -> dict[str, str]:
    """
    Load the strict TalentHive skill vocabulary once.
    """

    if not SKILLS_FILE.exists():

        raise FileNotFoundError(
            "TalentHive skill taxonomy not found:\n"
            f"{SKILLS_FILE}"
        )


    with SKILLS_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:

        skills = json.load(
            file
        )


    if not isinstance(
        skills,
        list,
    ):

        raise ValueError(
            "talenthive_skills.json must contain "
            "a JSON list."
        )


    exact_map: dict[str, str] = {}

    compact_map: dict[str, str] = {}


    # --------------------------------------------------------
    # Load canonical names
    # --------------------------------------------------------

    for skill in skills:

        if not isinstance(
            skill,
            str,
        ):
            continue


        canonical = skill.strip()


        if not canonical:
            continue


        exact_key = normalize_text(
            canonical
        )

        exact_map[
            exact_key
        ] = canonical


        compact_key = compact_text(
            canonical
        )


        if compact_key:

            compact_map[
                compact_key
            ] = canonical


    # --------------------------------------------------------
    # Add explicit aliases
    # --------------------------------------------------------

    for alias, canonical in ALIASES.items():

        exact_map[
            normalize_text(alias)
        ] = canonical

        compact_key = compact_text(
            alias
        )

        if compact_key:

            compact_map[
                compact_key
            ] = canonical


    return {
        "exact": exact_map,
        "compact": compact_map,
    }


# ============================================================
# FIND CANONICAL SKILL
# ============================================================

def canonicalize_skill(
    skill: str,
) -> str | None:
    """
    Convert a model prediction into one of the approved
    TalentHive canonical skill names.
    """

    if not isinstance(
        skill,
        str,
    ):
        return None


    cleaned = skill.strip()


    if not cleaned:
        return None


    taxonomy = (
        load_skill_taxonomy()
    )


    exact_map = taxonomy[
        "exact"
    ]

    compact_map = taxonomy[
        "compact"
    ]


    # --------------------------------------------------------
    # 1. Explicit exact/alias mapping
    # --------------------------------------------------------

    exact_key = normalize_text(
        cleaned
    )


    if exact_key in exact_map:

        return exact_map[
            exact_key
        ]


    # --------------------------------------------------------
    # 2. Compact mapping
    # --------------------------------------------------------

    compact_key = compact_text(
        cleaned
    )


    if compact_key in compact_map:

        return compact_map[
            compact_key
        ]


    # --------------------------------------------------------
    # 3. No safe mapping
    #
    # Do NOT invent a canonical skill.
    # --------------------------------------------------------

    return None


# ============================================================
# NORMALIZE SKILLS
# ============================================================

def normalize_skills(
    skills: list[str],
) -> list[str]:
    """
    Normalize model-extracted skills into the strict
    TalentHive vocabulary.

    Unknown predictions are discarded rather than mapped
    to unrelated ESCO concepts.
    """

    if not skills:
        return []


    result: list[str] = []

    seen: set[str] = set()


    for skill in skills:

        canonical = (
            canonicalize_skill(
                skill
            )
        )


        if canonical is None:
            continue


        key = normalize_text(
            canonical
        )


        if key in seen:
            continue


        seen.add(
            key
        )


        result.append(
            canonical
        )


    return sorted(
        result,
        key=lambda value:
            value.lower()
    )