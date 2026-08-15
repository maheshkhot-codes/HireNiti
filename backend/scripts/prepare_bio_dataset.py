import json
from pathlib import Path

from transformers import AutoTokenizer


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = (
    BASE_DIR
    / "data"
    / "resume_extraction"
)


TRAIN_INPUT = DATA_DIR / "train.jsonl"
VALIDATION_INPUT = DATA_DIR / "validation.jsonl"
TEST_INPUT = DATA_DIR / "test.jsonl"

TRAIN_OUTPUT = DATA_DIR / "train_bio.jsonl"
VALIDATION_OUTPUT = DATA_DIR / "validation_bio.jsonl"
TEST_OUTPUT = DATA_DIR / "test_bio.jsonl"


# ============================================================
# MODEL
# ============================================================

# We use a small BERT model first because your environment
# currently has CPU-only PyTorch.

MODEL_NAME = "distilbert-base-uncased"


# ============================================================
# LABELS
# ============================================================

LABEL2ID = {
    "O": 0,
    "B-SKILL": 1,
    "I-SKILL": 2,
}

ID2LABEL = {
    0: "O",
    1: "B-SKILL",
    2: "I-SKILL",
}


# ============================================================
# LOAD TOKENIZER
# ============================================================

print("=" * 60)
print("TalentHive BIO Dataset Preparation")
print("=" * 60)

print(
    f"\nLoading tokenizer: {MODEL_NAME}"
)

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME,
    use_fast=True,
)


# ============================================================
# LOAD JSONL
# ============================================================

def load_jsonl(
    path: Path
) -> list[dict]:

    records = []

    with path.open(
        "r",
        encoding="utf-8"
    ) as file:

        for line in file:

            line = line.strip()

            if not line:
                continue

            records.append(
                json.loads(line)
            )

    return records


# ============================================================
# CONVERT ONE RECORD
# ============================================================

def convert_record(
    record: dict
) -> dict | None:

    text = record.get(
        "text",
        ""
    )

    entities = record.get(
        "entities",
        []
    )

    if not text:
        return None

    if not entities:
        return None


    # --------------------------------------------------------
    # Tokenize while keeping character offsets
    # --------------------------------------------------------

    encoding = tokenizer(
        text,
        truncation=True,
        max_length=512,
        return_offsets_mapping=True,
    )


    input_ids = encoding[
        "input_ids"
    ]

    attention_mask = encoding[
        "attention_mask"
    ]

    offsets = encoding[
        "offset_mapping"
    ]


    labels = [
        LABEL2ID["O"]
        for _ in input_ids
    ]


    # --------------------------------------------------------
    # Assign BIO labels using character spans
    # --------------------------------------------------------

    for entity in entities:

        start = entity.get(
            "start"
        )

        end = entity.get(
            "end"
        )

        label = entity.get(
            "label"
        )


        if not isinstance(
            start,
            int
        ):
            continue

        if not isinstance(
            end,
            int
        ):
            continue

        if label != "SKILL":
            continue


        first_token = True


        for token_index, (
            token_start,
            token_end,
        ) in enumerate(offsets):

            # Special tokens generally have (0, 0)
            if (
                token_start ==
                token_end
            ):
                continue


            # No overlap
            if token_end <= start:
                continue

            if token_start >= end:
                continue


            if first_token:

                labels[token_index] = (
                    LABEL2ID["B-SKILL"]
                )

                first_token = False

            else:

                labels[token_index] = (
                    LABEL2ID["I-SKILL"]
                )


    return {
        "input_ids": input_ids,

        "attention_mask":
            attention_mask,

        "labels":
            labels,
    }


# ============================================================
# PROCESS DATASET
# ============================================================

def process_dataset(
    input_path: Path,
    output_path: Path
):

    print(
        f"\nProcessing:\n{input_path}"
    )

    records = load_jsonl(
        input_path
    )

    print(
        f"Input records: {len(records)}"
    )


    converted = []


    for record in records:

        result = convert_record(
            record
        )

        if result:

            converted.append(
                result
            )


    with output_path.open(
        "w",
        encoding="utf-8"
    ) as file:

        for item in converted:

            file.write(
                json.dumps(
                    item
                )
                + "\n"
            )


    print(
        f"Output records: "
        f"{len(converted)}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    process_dataset(
        TRAIN_INPUT,
        TRAIN_OUTPUT
    )

    process_dataset(
        VALIDATION_INPUT,
        VALIDATION_OUTPUT
    )

    process_dataset(
        TEST_INPUT,
        TEST_OUTPUT
    )


    print(
        "\n" + "=" * 60
    )

    print(
        "BIO dataset preparation complete."
    )

    print(
        "=" * 60
    )

    print(
        "\nLabel mapping:"
    )

    print(
        LABEL2ID
    )


if __name__ == "__main__":
    main()