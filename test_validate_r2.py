import json

from retrieve_templates import load_brief, retrieve_templates
from validate_r2 import validate_r2


def main():
    brief_id = "BRIEF-001"

    with open(
        "data/r2_BRIEF-001.json",
        "r",
        encoding="utf-8",
    ) as file:
        result = json.load(file)

    brief = load_brief(brief_id)

    retrieved = retrieve_templates(
        brief,
        top_k=3,
    )

    retrieved_template_ids = [
        item["template_id"]
        for item in retrieved
    ]

    errors = validate_r2(
        result=result,
        brief=brief,
        retrieved_template_ids=retrieved_template_ids,
    )

    if errors:
        print("VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
    else:
        print("VALIDATION PASSED")


if __name__ == "__main__":
    main()