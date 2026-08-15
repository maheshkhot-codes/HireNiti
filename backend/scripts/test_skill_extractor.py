import json
from pathlib import Path

import torch
from transformers import (
    AutoModelForTokenClassification,
    AutoTokenizer,
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

MODEL_DIR = (
    BASE_DIR
    / "models"
    / "skill_extractor"
)


# ============================================================
# MODEL
# ============================================================

print("=" * 60)
print("TalentHive Skill Extractor Test")
print("=" * 60)


print(
    f"\nLoading model from:\n{MODEL_DIR}"
)


tokenizer = AutoTokenizer.from_pretrained(
    str(MODEL_DIR)
)


model = (
    AutoModelForTokenClassification
    .from_pretrained(
        str(MODEL_DIR)
    )
)


model.eval()


# ============================================================
# EXTRACT SKILLS
# ============================================================

def extract_skills(
    text: str
) -> list[str]:

    encoding = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=512,
        return_offsets_mapping=True,
    )


    offset_mapping = (
        encoding.pop(
            "offset_mapping"
        )
    )


    with torch.no_grad():

        outputs = model(
            **encoding
        )


    predictions = torch.argmax(
        outputs.logits,
        dim=-1
    )[0].tolist()


    input_ids = (
        encoding["input_ids"][0]
        .tolist()
    )


    tokens = tokenizer.convert_ids_to_tokens(
        input_ids
    )


    skills = []

    current_skill = ""


    for index, (
        token,
        prediction,
        offset,
    ) in enumerate(
        zip(
            tokens,
            predictions,
            offset_mapping[0].tolist(),
        )
    ):

        start, end = offset


        if start == end:
            continue


        label = model.config.id2label.get(
            prediction,
            "O"
        )


        if label == "B-SKILL":

            if current_skill:

                skills.append(
                    current_skill.strip()
                )


            current_skill = text[
                start:end
            ]


        elif label == "I-SKILL":

            if current_skill:

                current_skill += (
                    text[
                        start:end
                    ]
                )


        else:

            if current_skill:

                skills.append(
                    current_skill.strip()
                )

                current_skill = ""


    if current_skill:

        skills.append(
            current_skill.strip()
        )


    # --------------------------------------------------------
    # Clean and deduplicate
    # --------------------------------------------------------

    result = []

    seen = set()


    for skill in skills:

        skill = skill.strip()


        if not skill:
            continue


        key = skill.lower()


        if key in seen:
            continue


        seen.add(key)

        result.append(
            skill
        )


    return result


# ============================================================
# TEST RESUME
# ============================================================

resume_text = """
Mahesh Khot

Technical Skills:
Core Java, Python, SQL, HTML, CSS, JavaScript,
Spring Boot, React.js, MySQL, Git, GitHub,
Playwright, FastAPI, REST APIs, Machine Learning.

Projects:

WealthWise – Mutual Fund & SIP Tracking Platform

Technologies:
Core Java, React.js, Spring Boot, MySQL, REST APIs.

AI Recruitment System

Technologies:
Python, React.js, FastAPI, Supabase, FAISS,
XGBoost, REST APIs.
"""


# ============================================================
# RUN
# ============================================================

skills = extract_skills(
    resume_text
)


print("\nExtracted skills:")

if not skills:

    print(
        "No skills detected."
    )

else:

    for index, skill in enumerate(
        skills,
        start=1
    ):

        print(
            f"{index}. {skill}"
        )


print(
    "\nTotal skills:",
    len(skills)
)


print(
    "\n" + "=" * 60
)