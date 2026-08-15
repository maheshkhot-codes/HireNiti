from functools import lru_cache
from pathlib import Path
import json
import re

import torch
from transformers import (
    AutoModelForTokenClassification,
    AutoTokenizer,
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_DIR = (
    BASE_DIR
    / "models"
    / "skill_extractor"
)

SKILLS_FILE = (
    BASE_DIR
    / "data"
    / "taxonomy"
    / "talenthive_skills.json"
)


# ============================================================
# SETTINGS
# ============================================================

MAX_MODEL_LENGTH = 512

MODEL_CONFIDENCE_THRESHOLD = 0.55

WINDOW_STRIDE = 384


# ============================================================
# LOAD TALENTHIVE SKILLS
# ============================================================

@lru_cache(maxsize=1)
def load_talent_hive_skills() -> list[str]:
    """
    Load the strict TalentHive skill vocabulary.
    """

    if not SKILLS_FILE.exists():

        raise FileNotFoundError(
            f"TalentHive skills file not found:\n"
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
            "talenthive_skills.json must contain a list."
        )


    result = []

    seen = set()


    for skill in skills:

        if not isinstance(
            skill,
            str,
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


    return result


# ============================================================
# NORMALIZE FOR REGEX
# ============================================================

def normalize_for_search(
    value: str
) -> str:
    """
    Normalize spaces without destroying symbols such as:
    C++, C#, .NET, Node.js.
    """

    value = value.replace(
        "\r\n",
        "\n",
    ).replace(
        "\r",
        "\n",
    )


    value = re.sub(
        r"[ \t]+",
        " ",
        value,
    )


    return value


# ============================================================
# ESCAPE REGEX SKILLS
# ============================================================

def build_skill_pattern(
    skill: str,
) -> re.Pattern:
    """
    Build a safe regex for exact skill matching.

    Prevents:
        c  matching css
        java matching javascript
        sql matching sqlite

    while supporting:
        C++
        C#
        Node.js
        .NET
    """

    escaped = re.escape(
        skill
    )


    # --------------------------------------------------------
    # Single-letter C needs special handling.
    # --------------------------------------------------------

    if skill.lower() == "c":

        return re.compile(
            r"(?<![A-Za-z0-9+#])"
            r"C"
            r"(?![A-Za-z0-9+#])",
            re.IGNORECASE,
        )


    return re.compile(
        rf"(?<![A-Za-z0-9+#])"
        rf"{escaped}"
        rf"(?![A-Za-z0-9+#])",
        re.IGNORECASE,
    )


# ============================================================
# VOCABULARY EXTRACTION
# ============================================================

def extract_vocabulary_skills(
    text: str,
) -> list[str]:
    """
    Extract exact TalentHive skills from the resume text.

    This is the high-recall safety layer. It only returns
    skills from the approved TalentHive vocabulary.
    """

    if not text or not text.strip():

        return []


    text = normalize_for_search(
        text
    )


    skills = load_talent_hive_skills()


    # Longer skills first.
    # This helps prefer:
    # "Machine Learning"
    # over:
    # "Learning"
    sorted_skills = sorted(
        skills,
        key=len,
        reverse=True,
    )


    matches = []


    for skill in sorted_skills:

        pattern = build_skill_pattern(
            skill
        )


        for match in pattern.finditer(
            text
        ):

            matches.append(
                {
                    "start":
                        match.start(),

                    "end":
                        match.end(),

                    "text":
                        match.group(0),

                    "canonical":
                        skill,
                }
            )


    # --------------------------------------------------------
    # Sort by start position.
    # Longer match wins when spans overlap.
    # --------------------------------------------------------

    matches.sort(
        key=lambda item: (
            item["start"],
            -(item["end"] - item["start"]),
        )
    )


    accepted = []

    occupied_ranges = []


    for match in matches:

        start = match["start"]
        end = match["end"]


        overlaps = False


        for occupied_start, occupied_end in (
            occupied_ranges
        ):

            if (
                start < occupied_end
                and end > occupied_start
            ):

                overlaps = True

                break


        if overlaps:
            continue


        accepted.append(
            match
        )


        occupied_ranges.append(
            (
                start,
                end,
            )
        )


    accepted.sort(
        key=lambda item:
            item["start"]
    )


    return [
        item["canonical"]
        for item in accepted
    ]


# ============================================================
# LOAD TRAINED MODEL
# ============================================================

@lru_cache(maxsize=1)
def load_skill_model():
    """
    Load the trained DistilBERT model once.

    The model stays in memory after the first request.
    """

    if not MODEL_DIR.exists():

        raise FileNotFoundError(
            f"Trained skill model not found:\n"
            f"{MODEL_DIR}"
        )


    tokenizer = (
        AutoTokenizer.from_pretrained(
            str(MODEL_DIR)
        )
    )


    model = (
        AutoModelForTokenClassification
        .from_pretrained(
            str(MODEL_DIR)
        )
    )


    model.eval()


    # --------------------------------------------------------
    # CPU inference
    # --------------------------------------------------------

    model.to(
        torch.device("cpu")
    )


    return tokenizer, model


# ============================================================
# MODEL PREDICTION FOR ONE WINDOW
# ============================================================

def extract_model_skills_from_window(
    text: str,
    tokenizer,
    model,
) -> list[str]:
    """
    Run the trained model on one text window.
    """

    if not text.strip():

        return []


    encoding = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=MAX_MODEL_LENGTH,
        return_offsets_mapping=True,
    )


    offsets = encoding.pop(
        "offset_mapping"
    )


    # --------------------------------------------------------
    # Model inference
    # --------------------------------------------------------

    with torch.no_grad():

        outputs = model(
            **encoding
        )


    probabilities = torch.softmax(
        outputs.logits,
        dim=-1,
    )


    predictions = torch.argmax(
        probabilities,
        dim=-1,
    )[0].tolist()


    confidences = torch.max(
        probabilities,
        dim=-1,
    )[0][0].tolist()


    # --------------------------------------------------------
    # Build text spans
    # --------------------------------------------------------

    skills = []

    current_start = None

    current_end = None


    for prediction, confidence, offset in zip(
        predictions,
        confidences,
        offsets[0].tolist(),
    ):

        start, end = offset


        # Special token
        if start == end:
            continue


        label = model.config.id2label.get(
            int(prediction),
            "O",
        )


        # ----------------------------------------------------
        # Ignore low-confidence predictions.
        # ----------------------------------------------------

        if confidence < MODEL_CONFIDENCE_THRESHOLD:

            if (
                current_start is not None
                and current_end is not None
            ):

                skill = text[
                    current_start:current_end
                ].strip()


                if skill:

                    skills.append(
                        skill
                    )


            current_start = None
            current_end = None

            continue


        # ----------------------------------------------------
        # B-SKILL
        # ----------------------------------------------------

        if label == "B-SKILL":

            if (
                current_start is not None
                and current_end is not None
            ):

                skill = text[
                    current_start:current_end
                ].strip()


                if skill:

                    skills.append(
                        skill
                    )


            current_start = start

            current_end = end


        # ----------------------------------------------------
        # I-SKILL
        # ----------------------------------------------------

        elif label == "I-SKILL":

            if current_start is not None:

                current_end = end


        # ----------------------------------------------------
        # Outside
        # ----------------------------------------------------

        else:

            if (
                current_start is not None
                and current_end is not None
            ):

                skill = text[
                    current_start:current_end
                ].strip()


                if skill:

                    skills.append(
                        skill
                    )


            current_start = None

            current_end = None


    # --------------------------------------------------------
    # Flush final skill
    # --------------------------------------------------------

    if (
        current_start is not None
        and current_end is not None
    ):

        skill = text[
            current_start:current_end
        ].strip()


        if skill:

            skills.append(
                skill
            )


    return skills


# ============================================================
# MODEL EXTRACTION
# ============================================================

def extract_model_skills(
    text: str,
) -> list[str]:
    """
    Extract contextual skills using the trained model.

    Long resumes are processed in overlapping windows so
    skills near the 512-token boundary are not lost.
    """

    if not text or not text.strip():

        return []


    tokenizer, model = (
        load_skill_model()
    )


    # --------------------------------------------------------
    # Determine token count
    # --------------------------------------------------------

    token_ids = tokenizer(
        text,
        add_special_tokens=True,
        truncation=False,
    )[
        "input_ids"
    ]


    if len(token_ids) <= MAX_MODEL_LENGTH:

        return extract_model_skills_from_window(
            text,
            tokenizer,
            model,
        )


    # --------------------------------------------------------
    # Sliding windows
    # --------------------------------------------------------

    all_skills = []


    words = text.split()


    if not words:

        return []


    # Estimate overlapping word windows for resumes.
    #
    # We intentionally keep windows reasonably small so
    # each section has enough contextual information.
    window_words = 280

    stride_words = 200


    start = 0


    while start < len(words):

        end = min(
            start + window_words,
            len(words),
        )


        window_text = " ".join(
            words[start:end]
        )


        window_skills = (
            extract_model_skills_from_window(
                window_text,
                tokenizer,
                model,
            )
        )


        all_skills.extend(
            window_skills
        )


        if end >= len(words):

            break


        start += stride_words


    return all_skills


# ============================================================
# CLEAN MODEL RESULTS
# ============================================================

def deduplicate_skills(
    skills: list[str],
) -> list[str]:
    """
    Remove duplicate predictions while preserving order.
    """

    result = []

    seen = set()


    for skill in skills:

        if not isinstance(
            skill,
            str,
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


    return result


# ============================================================
# PUBLIC API
# ============================================================

def extract_ml_skills(
    text: str,
) -> list[str]:
    """
    Hybrid TalentHive skill extraction.

    Stage 1:
        DistilBERT contextual extraction.

    Stage 2:
        Exact TalentHive vocabulary extraction.

    Stage 3:
        Merge and deduplicate.

    The exact vocabulary layer prevents the trained model
    from losing obvious skills such as Python, Java, SQL,
    React, MySQL, etc.
    """

    if not text or not text.strip():

        return []


    # --------------------------------------------------------
    # MODEL
    # --------------------------------------------------------

    model_skills = extract_model_skills(
        text
    )


    # --------------------------------------------------------
    # VOCABULARY
    # --------------------------------------------------------

    vocabulary_skills = (
        extract_vocabulary_skills(
            text
        )
    )


    # --------------------------------------------------------
    # MERGE
    # --------------------------------------------------------

    combined = []

    combined.extend(
        model_skills
    )

    combined.extend(
        vocabulary_skills
    )


    # --------------------------------------------------------
    # Deduplicate
    # --------------------------------------------------------

    return deduplicate_skills(
        combined
    )