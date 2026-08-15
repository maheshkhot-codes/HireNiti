import json
import random
import re
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "resume_extraction"
    / "raw"
    / "kaggle_resume_ner"
    / "train.json"
)

SKILLS_FILE = (
    BASE_DIR
    / "data"
    / "taxonomy"
    / "talenthive_skills.json"
)

OUTPUT_DIR = (
    BASE_DIR
    / "data"
    / "resume_extraction"
)

TRAIN_FILE = OUTPUT_DIR / "train.jsonl"
VALIDATION_FILE = OUTPUT_DIR / "validation.jsonl"
TEST_FILE = OUTPUT_DIR / "test.jsonl"


# ============================================================
# SETTINGS
# ============================================================

RANDOM_SEED = 42

TRAIN_RATIO = 0.80
VALIDATION_RATIO = 0.10

TEST_RATIO = (
    1.0
    - TRAIN_RATIO
    - VALIDATION_RATIO
)


# ============================================================
# TEXT NORMALIZATION
# ============================================================

def normalize_skill(
    value: str
) -> str:
    """
    Normalize a skill name for comparison.
    """

    value = value.lower().strip()

    value = re.sub(
        r"\s+",
        " ",
        value,
    )

    return value


def compact_skill(
    value: str
) -> str:
    """
    Remove spaces and punctuation for alias matching.

    Examples:
        React.js -> reactjs
        ReactJS  -> reactjs
    """

    return re.sub(
        r"[^a-z0-9+#]+",
        "",
        normalize_skill(value),
    )


# ============================================================
# LOAD TALENTHIVE SKILLS
# ============================================================

def load_talenthive_skills() -> dict[str, str]:
    """
    Load the explicit TalentHive skill vocabulary.

    talenthive_skills.json should contain a simple list:

    [
        "Python",
        "Java",
        "React",
        ...
    ]
    """

    if not SKILLS_FILE.exists():

        raise FileNotFoundError(
            f"TalentHive skill file not found:\n"
            f"{SKILLS_FILE}"
        )


    with SKILLS_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:

        data = json.load(
            file
        )


    if not isinstance(
        data,
        list,
    ):

        raise ValueError(
            "talenthive_skills.json "
            "must contain a JSON list."
        )


    exact_map: dict[str, str] = {}

    compact_map: dict[str, str] = {}


    for item in data:

        if not isinstance(
            item,
            str,
        ):
            continue


        canonical = item.strip()


        if not canonical:
            continue


        normalized = normalize_skill(
            canonical
        )


        exact_map[
            normalized
        ] = canonical


        compact = compact_skill(
            canonical
        )


        if compact:

            compact_map[
                compact
            ] = canonical


    # Store compact mappings with a prefix so they don't
    # collide with normal skill names.

    result = dict(
        exact_map
    )


    for key, value in compact_map.items():

        result[
            f"__COMPACT__{key}"
        ] = value


    return result


# ============================================================
# GET CANONICAL SKILL
# ============================================================

def get_canonical_skill(
    value: str,
    skill_map: dict[str, str],
) -> str | None:
    """
    Return the canonical TalentHive skill name.
    """

    normalized = normalize_skill(
        value
    )


    if not normalized:
        return None


    # --------------------------------------------------------
    # Exact match
    # --------------------------------------------------------

    exact = skill_map.get(
        normalized
    )


    if exact:
        return exact


    # --------------------------------------------------------
    # Compact match
    # --------------------------------------------------------

    compact = compact_skill(
        value
    )


    if compact:

        return skill_map.get(
            f"__COMPACT__{compact}"
        )


    return None


# ============================================================
# CONTEXTUAL C CHECK
# ============================================================

def is_contextual_c_skill(
    text: str,
    start: int,
    end: int,
) -> bool:
    """
    'C' is a valid programming language, but it is also
    extremely common as an ordinary single-character token.

    Keep C only when the surrounding resume context suggests
    that it refers to programming.
    """

    skill_text = text[
        start:end
    ].strip()


    # Any skill other than C is unaffected.

    if skill_text.lower() != "c":
        return True


    # --------------------------------------------------------
    # Get surrounding context
    # --------------------------------------------------------

    context_start = max(
        0,
        start - 150,
    )


    context_end = min(
        len(text),
        end + 150,
    )


    context = text[
        context_start:context_end
    ].lower()


    # --------------------------------------------------------
    # Strong programming signals
    # --------------------------------------------------------

    programming_signals = [

        "c programming",

        "c language",

        "programming in c",

        "c developer",

        "c development",

        "c/c++",

        "c / c++",

        "c, c++",

        "c and c++",

        "c & c++",

        "ansi c",

        "embedded c",

        "c compiler",

        "c programming language",

        "programming languages",

        "programming language",

    ]


    for signal in programming_signals:

        if signal in context:

            return True


    # --------------------------------------------------------
    # Technical skills section signals
    # --------------------------------------------------------

    technical_signals = [

        "technical skills",

        "technical skill",

        "skills:",

        "skills",

        "software skills",

        "technologies:",

        "technologies",

        "technology:",

        "programming:",

        "programming",

    ]


    for signal in technical_signals:

        if signal in context:

            return True


    # --------------------------------------------------------
    # Check for nearby C++.
    #
    # Example:
    #     C, C++, Java
    #
    # If C++ is very close, C is likely a language.
    # --------------------------------------------------------

    nearby = text[
        max(0, start - 30):
        min(len(text), end + 30)
    ].lower()


    if "c++" in nearby:

        return True


    # --------------------------------------------------------
    # Otherwise reject the single-character C.
    # --------------------------------------------------------

    return False


# ============================================================
# CONVERT ONE RESUME
# ============================================================

def convert_record(
    record: dict,
    skill_map: dict[str, str],
) -> dict | None:
    """
    Convert one source resume into our clean format.
    """

    if not isinstance(
        record,
        dict,
    ):
        return None


    text = record.get(
        "text",
        "",
    )


    if not isinstance(
        text,
        str,
    ):
        return None


    if not text.strip():
        return None


    annotations = record.get(
        "annotations",
        [],
    )


    if not isinstance(
        annotations,
        list,
    ):
        return None


    entities = []


    # ========================================================
    # PROCESS ANNOTATIONS
    # ========================================================

    for annotation in annotations:

        # Expected source format:
        #
        # [start, end, label]

        if not isinstance(
            annotation,
            list,
        ):
            continue


        if len(annotation) != 3:
            continue


        start = annotation[0]

        end = annotation[1]

        label = annotation[2]


        # ----------------------------------------------------
        # Validate values
        # ----------------------------------------------------

        if not isinstance(
            start,
            int,
        ):
            continue


        if not isinstance(
            end,
            int,
        ):
            continue


        if not isinstance(
            label,
            str,
        ):
            continue


        # ----------------------------------------------------
        # Keep only SKILL
        # ----------------------------------------------------

        if label.upper() != "SKILL":
            continue


        # ----------------------------------------------------
        # Validate span
        # ----------------------------------------------------

        if start < 0:
            continue


        if end <= start:
            continue


        if end > len(text):
            continue


        # ----------------------------------------------------
        # Extract annotated text
        # ----------------------------------------------------

        skill_text = text[
            start:end
        ].strip()


        if not skill_text:
            continue


        # ====================================================
        # SPECIAL C HANDLING
        # ====================================================

        if not is_contextual_c_skill(
            text,
            start,
            end,
        ):
            continue


        # ====================================================
        # TALENTHIVE VOCABULARY FILTER
        # ====================================================

        canonical = get_canonical_skill(
            skill_text,
            skill_map,
        )


        # Not one of our approved skills.

        if canonical is None:
            continue


        # ----------------------------------------------------
        # Keep entity
        # ----------------------------------------------------

        entities.append(
            {
                "start": start,
                "end": end,
                "text": skill_text,
                "label": "SKILL",
                "canonical": canonical,
            }
        )


    # --------------------------------------------------------
    # No valid skills
    # --------------------------------------------------------

    if not entities:
        return None


    # ========================================================
    # SORT
    # ========================================================

    entities.sort(
        key=lambda item: (
            item["start"],
            item["end"],
        )
    )


    # ========================================================
    # REMOVE OVERLAPPING ENTITIES
    # ========================================================

    cleaned = []

    last_end = -1


    for entity in entities:

        if entity["start"] < last_end:
            continue


        cleaned.append(
            entity
        )


        last_end = entity[
            "end"
        ]


    if not cleaned:
        return None


    # ========================================================
    # REMOVE INTERNAL CANONICAL FIELD
    # ========================================================

    final_entities = []


    for item in cleaned:

        final_entities.append(
            {
                "start": item["start"],
                "end": item["end"],
                "text": item["text"],
                "label": "SKILL",
            }
        )


    return {
        "text": text,
        "entities": final_entities,
    }


# ============================================================
# UTF-8 SAFETY
# ============================================================

def make_utf8_safe(
    value,
):
    """
    Replace invalid Unicode surrogate characters that can
    appear in some resume records.
    """

    if isinstance(
        value,
        str,
    ):

        return (
            value
            .encode(
                "utf-8",
                "replace",
            )
            .decode(
                "utf-8",
            )
        )


    if isinstance(
        value,
        dict,
    ):

        return {
            key: make_utf8_safe(
                item
            )
            for key, item
            in value.items()
        }


    if isinstance(
        value,
        list,
    ):

        return [
            make_utf8_safe(
                item
            )
            for item in value
        ]


    return value


# ============================================================
# WRITE JSONL
# ============================================================

def write_jsonl(
    path: Path,
    records: list[dict],
) -> None:

    with path.open(
        "w",
        encoding="utf-8",
        errors="replace",
    ) as file:

        for record in records:

            safe_record = (
                make_utf8_safe(
                    record
                )
            )


            file.write(
                json.dumps(
                    safe_record,
                    ensure_ascii=False,
                )
                + "\n"
            )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)

    print(
        "TalentHive Final Resume Skill Dataset"
    )

    print("=" * 60)


    # ========================================================
    # CHECK INPUT FILES
    # ========================================================

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            "Resume dataset not found:\n"
            f"{INPUT_FILE}"
        )


    if not SKILLS_FILE.exists():

        raise FileNotFoundError(
            "TalentHive skill vocabulary not found:\n"
            f"{SKILLS_FILE}"
        )


    # ========================================================
    # LOAD SKILL VOCABULARY
    # ========================================================

    skill_map = (
        load_talenthive_skills()
    )


    canonical_count = sum(
        1
        for key in skill_map
        if not key.startswith(
            "__COMPACT__"
        )
    )


    print(
        f"\nTalentHive skills: "
        f"{canonical_count}"
    )


    # ========================================================
    # LOAD RESUMES
    # ========================================================

    with INPUT_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:

        raw_data = json.load(
            file
        )


    if not isinstance(
        raw_data,
        list,
    ):

        raise ValueError(
            "train.json must contain a list."
        )


    print(
        f"Raw resumes: "
        f"{len(raw_data)}"
    )


    # ========================================================
    # CONVERT
    # ========================================================

    converted = []

    raw_skill_annotations = 0

    kept_skill_annotations = 0


    for record in raw_data:

        if not isinstance(
            record,
            dict,
        ):
            continue


        annotations = record.get(
            "annotations",
            [],
        )


        # ----------------------------------------------------
        # Count raw SKILL annotations
        # ----------------------------------------------------

        if isinstance(
            annotations,
            list,
        ):

            for annotation in annotations:

                if (
                    isinstance(
                        annotation,
                        list,
                    )
                    and len(annotation) == 3
                    and isinstance(
                        annotation[2],
                        str,
                    )
                    and annotation[2].upper()
                    == "SKILL"
                ):

                    raw_skill_annotations += 1


        # ----------------------------------------------------
        # Convert
        # ----------------------------------------------------

        result = convert_record(
            record,
            skill_map,
        )


        if result:

            converted.append(
                result
            )


            kept_skill_annotations += len(
                result[
                    "entities"
                ]
            )


    # ========================================================
    # RESULTS
    # ========================================================

    print(
        "\nRaw SKILL annotations: "
        f"{raw_skill_annotations}"
    )


    print(
        "TalentHive SKILL annotations kept: "
        f"{kept_skill_annotations}"
    )


    print(
        "Usable resumes: "
        f"{len(converted)}"
    )


    # ========================================================
    # MINIMUM DATA CHECK
    # ========================================================

    if len(converted) < 100:

        raise ValueError(
            "The final filter produced fewer than "
            "100 usable resumes. "
            "Review talenthive_skills.json."
        )


    # ========================================================
    # SHUFFLE
    # ========================================================

    random.seed(
        RANDOM_SEED
    )

    random.shuffle(
        converted
    )


    # ========================================================
    # SPLIT
    # ========================================================

    total = len(
        converted
    )


    train_end = int(
        total *
        TRAIN_RATIO
    )


    validation_end = (
        train_end
        + int(
            total *
            VALIDATION_RATIO
        )
    )


    train_data = converted[
        :train_end
    ]


    validation_data = converted[
        train_end:
        validation_end
    ]


    test_data = converted[
        validation_end:
    ]


    # ========================================================
    # CREATE OUTPUT DIRECTORY
    # ========================================================

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


    # ========================================================
    # WRITE FILES
    # ========================================================

    write_jsonl(
        TRAIN_FILE,
        train_data,
    )


    write_jsonl(
        VALIDATION_FILE,
        validation_data,
    )


    write_jsonl(
        TEST_FILE,
        test_data,
    )


    # ========================================================
    # FINAL SUMMARY
    # ========================================================

    print(
        "\nDataset split:"
    )


    print(
        f"Train      : "
        f"{len(train_data)}"
    )


    print(
        f"Validation : "
        f"{len(validation_data)}"
    )


    print(
        f"Test       : "
        f"{len(test_data)}"
    )


    print(
        "\nFiles created:"
    )


    print(
        TRAIN_FILE
    )


    print(
        VALIDATION_FILE
    )


    print(
        TEST_FILE
    )


    print(
        "\n" + "=" * 60
    )


    print(
        "Final dataset preparation complete."
    )


    print(
        "=" * 60
    )


if __name__ == "__main__":
    main()