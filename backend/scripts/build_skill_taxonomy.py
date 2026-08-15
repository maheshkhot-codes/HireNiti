import json
import re
from pathlib import Path

import pandas as pd


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "taxonomy"
    / "esco"
    / "skills_en.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "taxonomy"
    / "skills.json"
)


# ============================================================
# HELPERS
# ============================================================

def clean_text(value) -> str:
    if pd.isna(value):
        return ""

    return str(value).strip()


def split_labels(value) -> list[str]:
    """
    ESCO CSV fields may contain multiple labels separated
    by newline characters.
    """

    text = clean_text(value)

    if not text:
        return []

    parts = re.split(
        r"[\r\n]+",
        text
    )

    result = []

    for part in parts:

        cleaned = part.strip()

        if cleaned:
            result.append(cleaned)

    return result


def normalize_text(value: str) -> str:

    value = value.lower().strip()

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("TalentHive Skill Taxonomy Builder")
    print("=" * 60)

    # --------------------------------------------------------
    # Check input
    # --------------------------------------------------------

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            f"ESCO file not found:\n{INPUT_FILE}"
        )

    print(
        f"\nReading:\n{INPUT_FILE}"
    )


    # --------------------------------------------------------
    # Read CSV
    # --------------------------------------------------------

    df = pd.read_csv(
        INPUT_FILE,
        sep=None,
        engine="python",
        dtype=str,
        keep_default_na=False
    )


    print(
        f"\nRows found: {len(df)}"
    )

    print(
        "\nColumns found:"
    )

    for column in df.columns:
        print(
            f"  - {column}"
        )


    # --------------------------------------------------------
    # Find relevant columns
    # --------------------------------------------------------

    preferred_column = None

    alias_column = None

    hidden_column = None

    skill_type_column = None


    for column in df.columns:

        lower = column.lower()

        if (
            preferred_column is None
            and "preferredlabel" in lower
        ):
            preferred_column = column

        if (
            alias_column is None
            and "altlabels" in lower
        ):
            alias_column = column

        if (
            hidden_column is None
            and "hiddenlabels" in lower
        ):
            hidden_column = column

        if (
            skill_type_column is None
            and "skilltype" in lower
        ):
            skill_type_column = column


    if preferred_column is None:

        raise ValueError(
            "Could not find the ESCO preferred label column."
        )


    print(
        f"\nPreferred label column: "
        f"{preferred_column}"
    )

    print(
        f"Alias column: "
        f"{alias_column}"
    )

    print(
        f"Hidden label column: "
        f"{hidden_column}"
    )

    print(
        f"Skill type column: "
        f"{skill_type_column}"
    )


    # --------------------------------------------------------
    # Build taxonomy
    # --------------------------------------------------------

    taxonomy = []

    seen = set()


    for _, row in df.iterrows():

        canonical = clean_text(
            row[preferred_column]
        )


        if not canonical:
            continue


        normalized_canonical = (
            normalize_text(
                canonical
            )
        )


        if normalized_canonical in seen:
            continue


        seen.add(
            normalized_canonical
        )


        aliases = []


        # ----------------------------------------------------
        # Alternate labels
        # ----------------------------------------------------

        if alias_column:

            aliases.extend(
                split_labels(
                    row[alias_column]
                )
            )


        # ----------------------------------------------------
        # Hidden labels
        # ----------------------------------------------------

        if hidden_column:

            aliases.extend(
                split_labels(
                    row[hidden_column]
                )
            )


        # ----------------------------------------------------
        # Add canonical label itself
        # ----------------------------------------------------

        aliases.append(
            canonical
        )


        # ----------------------------------------------------
        # Clean + deduplicate aliases
        # ----------------------------------------------------

        cleaned_aliases = []

        alias_seen = set()


        for alias in aliases:

            alias = alias.strip()

            if not alias:
                continue


            normalized_alias = (
                normalize_text(
                    alias
                )
            )


            if (
                normalized_alias
                in alias_seen
            ):
                continue


            alias_seen.add(
                normalized_alias
            )

            cleaned_aliases.append(
                alias
            )


        # ----------------------------------------------------
        # Skill category
        # ----------------------------------------------------

        category = ""


        if skill_type_column:

            category = clean_text(
                row[skill_type_column]
            )


        taxonomy.append(
            {
                "canonical": canonical,

                "aliases":
                    cleaned_aliases,

                "category":
                    category,
            }
        )


    # --------------------------------------------------------
    # Sort alphabetically
    # --------------------------------------------------------

    taxonomy.sort(
        key=lambda item:
            item["canonical"].lower()
    )


    # --------------------------------------------------------
    # Create output directory
    # --------------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )


    # --------------------------------------------------------
    # Save JSON
    # --------------------------------------------------------

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            taxonomy,
            file,
            indent=2,
            ensure_ascii=False
        )


    print(
        "\n" + "=" * 60
    )

    print(
        f"Skills generated: "
        f"{len(taxonomy)}"
    )

    print(
        f"Output file:\n"
        f"{OUTPUT_FILE}"
    )

    print(
        "=" * 60
    )


if __name__ == "__main__":
    main()