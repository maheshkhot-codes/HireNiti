import json
from pathlib import Path

import torch

from datasets import Dataset
from transformers import (
    AutoModelForTokenClassification,
    AutoTokenizer,
    DataCollatorForTokenClassification,
    Trainer,
    TrainingArguments,
    set_seed,
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_DIR = (
    BASE_DIR
    / "data"
    / "resume_extraction"
)

MODEL_DIR = (
    BASE_DIR
    / "models"
    / "skill_extractor"
)

TRAIN_FILE = (
    DATA_DIR
    / "train_bio.jsonl"
)

VALIDATION_FILE = (
    DATA_DIR
    / "validation_bio.jsonl"
)


# ============================================================
# MODEL
# ============================================================

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
# TRAINING SETTINGS
# ============================================================

# None = use the complete cleaned dataset.
MAX_TRAIN_SAMPLES = None

MAX_VALIDATION_SAMPLES = None


# Full training run.
EPOCHS = 3


# Your machine currently has CPU-only PyTorch.
BATCH_SIZE = 4


LEARNING_RATE = 5e-5


RANDOM_SEED = 42


# ============================================================
# LOAD JSONL
# ============================================================

def load_jsonl(
    path: Path,
    limit: int | None = None,
) -> list[dict]:
    """
    Load records from a JSONL file.

    When limit is None, all records are loaded.
    """

    records: list[dict] = []

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:

        for line in file:

            if (
                limit is not None
                and len(records) >= limit
            ):
                break

            line = line.strip()

            if not line:
                continue

            records.append(
                json.loads(line)
            )

    return records


# ============================================================
# CREATE HF DATASET
# ============================================================

def create_dataset(
    records: list[dict],
) -> Dataset:
    """
    Convert our JSONL records into a Hugging Face Dataset.
    """

    if not records:
        raise ValueError(
            "Cannot create dataset from zero records."
        )

    return Dataset.from_dict(
        {
            "input_ids": [
                record["input_ids"]
                for record in records
            ],

            "attention_mask": [
                record["attention_mask"]
                for record in records
            ],

            "labels": [
                record["labels"]
                for record in records
            ],
        }
    )


# ============================================================
# VALIDATE RECORDS
# ============================================================

def validate_records(
    records: list[dict],
    dataset_name: str,
) -> None:
    """
    Check that all required fields exist and have matching
    lengths.
    """

    if not records:
        raise ValueError(
            f"{dataset_name} is empty."
        )

    required_fields = {
        "input_ids",
        "attention_mask",
        "labels",
    }

    for index, record in enumerate(
        records
    ):

        missing = (
            required_fields
            - set(record.keys())
        )

        if missing:

            raise ValueError(
                f"{dataset_name} record "
                f"{index} is missing: "
                f"{sorted(missing)}"
            )


        input_length = len(
            record["input_ids"]
        )

        attention_length = len(
            record["attention_mask"]
        )

        label_length = len(
            record["labels"]
        )


        if not (
            input_length
            == attention_length
            == label_length
        ):

            raise ValueError(
                f"{dataset_name} record "
                f"{index} has inconsistent "
                f"sequence lengths: "
                f"input_ids={input_length}, "
                f"attention_mask={attention_length}, "
                f"labels={label_length}"
            )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("TalentHive Skill Extractor Training")
    print("=" * 60)


    # --------------------------------------------------------
    # Reproducibility
    # --------------------------------------------------------

    set_seed(
        RANDOM_SEED
    )


    # --------------------------------------------------------
    # Check files
    # --------------------------------------------------------

    if not TRAIN_FILE.exists():

        raise FileNotFoundError(
            "Training file not found:\n"
            f"{TRAIN_FILE}"
        )


    if not VALIDATION_FILE.exists():

        raise FileNotFoundError(
            "Validation file not found:\n"
            f"{VALIDATION_FILE}"
        )


    # --------------------------------------------------------
    # Environment
    # --------------------------------------------------------

    print(
        f"\nPyTorch: "
        f"{torch.__version__}"
    )

    print(
        f"CUDA available: "
        f"{torch.cuda.is_available()}"
    )


    if torch.cuda.is_available():

        print(
            f"GPU: "
            f"{torch.cuda.get_device_name(0)}"
        )

    else:

        print(
            "Training device: CPU"
        )


    # --------------------------------------------------------
    # Training settings
    # --------------------------------------------------------

    print(
        "\nTraining configuration:"
    )

    print(
        f"Model: "
        f"{MODEL_NAME}"
    )

    print(
        f"Epochs: "
        f"{EPOCHS}"
    )

    print(
        f"Batch size: "
        f"{BATCH_SIZE}"
    )

    print(
        f"Learning rate: "
        f"{LEARNING_RATE}"
    )

    print(
        f"Random seed: "
        f"{RANDOM_SEED}"
    )


    # --------------------------------------------------------
    # Load data
    # --------------------------------------------------------

    print(
        "\nLoading training data..."
    )


    train_records = load_jsonl(
        TRAIN_FILE,
        MAX_TRAIN_SAMPLES,
    )


    validation_records = load_jsonl(
        VALIDATION_FILE,
        MAX_VALIDATION_SAMPLES,
    )


    print(
        f"Training records: "
        f"{len(train_records)}"
    )

    print(
        f"Validation records: "
        f"{len(validation_records)}"
    )


    # --------------------------------------------------------
    # Validate records
    # --------------------------------------------------------

    print(
        "\nValidating training data..."
    )


    validate_records(
        train_records,
        "Training",
    )


    validate_records(
        validation_records,
        "Validation",
    )


    print(
        "Dataset validation passed."
    )


    # --------------------------------------------------------
    # Create datasets
    # --------------------------------------------------------

    train_dataset = (
        create_dataset(
            train_records
        )
    )


    validation_dataset = (
        create_dataset(
            validation_records
        )
    )


    print(
        f"\nHF training dataset size: "
        f"{len(train_dataset)}"
    )

    print(
        f"HF validation dataset size: "
        f"{len(validation_dataset)}"
    )


    # --------------------------------------------------------
    # Tokenizer
    # --------------------------------------------------------

    print(
        "\nLoading tokenizer..."
    )


    tokenizer = (
        AutoTokenizer.from_pretrained(
            MODEL_NAME,
            use_fast=True,
        )
    )


    # --------------------------------------------------------
    # Model
    # --------------------------------------------------------

    print(
        "Loading model..."
    )


    model = (
        AutoModelForTokenClassification
        .from_pretrained(
            MODEL_NAME,
            num_labels=3,
            id2label=ID2LABEL,
            label2id=LABEL2ID,
        )
    )


    # --------------------------------------------------------
    # Data collator
    # --------------------------------------------------------

    data_collator = (
        DataCollatorForTokenClassification(
            tokenizer=tokenizer
        )
    )


    # --------------------------------------------------------
    # Output directory
    # --------------------------------------------------------

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


    # --------------------------------------------------------
    # Training arguments
    # --------------------------------------------------------

    training_args = TrainingArguments(

        output_dir=str(
            MODEL_DIR
        ),

        num_train_epochs=EPOCHS,

        per_device_train_batch_size=
            BATCH_SIZE,

        per_device_eval_batch_size=
            BATCH_SIZE,

        learning_rate=
            LEARNING_RATE,

        logging_steps=25,

        report_to="none",

        fp16=False,

        dataloader_num_workers=0,

    )


    # --------------------------------------------------------
    # Trainer
    # --------------------------------------------------------

    trainer = Trainer(

        model=model,

        args=training_args,

        train_dataset=train_dataset,

        eval_dataset=validation_dataset,

        data_collator=data_collator,

    )


    # --------------------------------------------------------
    # TRAIN
    # --------------------------------------------------------

    print(
        "\nStarting full training..."
    )


    print(
        "This may take a long time because "
        "your PyTorch installation is CPU-only."
    )


    train_result = (
        trainer.train()
    )


    # --------------------------------------------------------
    # SAVE MODEL
    # --------------------------------------------------------

    print(
        "\nSaving trained model..."
    )


    trainer.save_model(
        str(MODEL_DIR)
    )


    tokenizer.save_pretrained(
        str(MODEL_DIR)
    )


    # --------------------------------------------------------
    # SAVE TRAINING METRICS
    # --------------------------------------------------------

    metrics = (
        train_result.metrics
    )


    metrics_file = (
        MODEL_DIR
        / "training_metrics.json"
    )


    with metrics_file.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            metrics,
            file,
            indent=2,
        )


    # --------------------------------------------------------
    # EVALUATE
    # --------------------------------------------------------

    print(
        "\nRunning validation evaluation..."
    )


    evaluation_metrics = (
        trainer.evaluate()
    )


    evaluation_file = (
        MODEL_DIR
        / "evaluation_metrics.json"
    )


    with evaluation_file.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            evaluation_metrics,
            file,
            indent=2,
        )


    # --------------------------------------------------------
    # PRINT METRICS
    # --------------------------------------------------------

    print(
        "\nTraining metrics:"
    )


    for key, value in metrics.items():

        print(
            f"{key}: {value}"
        )


    print(
        "\nValidation metrics:"
    )


    for key, value in (
        evaluation_metrics.items()
    ):

        print(
            f"{key}: {value}"
        )


    # --------------------------------------------------------
    # COMPLETE
    # --------------------------------------------------------

    print(
        "\n" + "=" * 60
    )

    print(
        "Full training complete."
    )

    print(
        "Model saved to:"
    )

    print(
        MODEL_DIR
    )

    print(
        "\nTraining metrics:"
    )

    print(
        metrics_file
    )

    print(
        "\nEvaluation metrics:"
    )

    print(
        evaluation_file
    )

    print(
        "=" * 60
    )


if __name__ == "__main__":
    main()