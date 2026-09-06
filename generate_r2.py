import json
import urllib.error
import urllib.request
from pathlib import Path

from retrieve_templates import (
    ROOT,
    TEMPLATES_PATH,
    load_brief,
    retrieve_templates,
)
from validate_r2 import validate_r2


MODEL_NAME = "qwen3:8b"
OLLAMA_URL = "http://127.0.0.1:11434/api/chat"

PROMPT_PATH = ROOT / "prompts" / "r2_generation.txt"
OUTPUT_DIR = ROOT / "data"


def load_template_library() -> dict:
    templates = json.loads(
        TEMPLATES_PATH.read_text(encoding="utf-8")
    )

    return {
        template["template_id"]: template
        for template in templates
    }


def attach_full_templates(
    retrieved: list[dict],
    library: dict,
) -> list[dict]:

    records = []

    for item in retrieved:
        template = dict(
            library[item["template_id"]]
        )

        template["similarity"] = item["similarity"]

        records.append(template)

    return records


def call_llm(
    system_prompt: str,
    user_payload: dict,
) -> dict:

    body = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": json.dumps(
                    user_payload,
                    indent=2,
                ),
            },
        ],
        "stream": False,
        "format": "json",
        "think": False,
        "options": {
            "temperature": 0.1,
        },
    }

    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=600,
        ) as response:

            payload = json.loads(
                response.read().decode("utf-8")
            )

    except urllib.error.URLError as exc:

        raise RuntimeError(
            "Ollama is not reachable at "
            "127.0.0.1:11434. Start it, then retry."
        ) from exc

    content = payload["message"]["content"]

    if isinstance(content, dict):
        return content

    return json.loads(content)


def repair_result(
    result: dict,
    validation_errors: list[str],
    brief: dict,
    retrieved_templates: list[dict],
) -> dict:

    repair_prompt = """
You are repairing an AI-generated Solutions Engineering POC plan.

The original result failed application validation.

Repair ONLY the issues identified by the validation errors.

Preserve correct information from the original result.

Do not invent facts.

Use only:
- the Brief
- the retrieved templates
- the validation errors
- the original result

Return the complete corrected JSON object.

Validation errors:
""" + json.dumps(
        validation_errors,
        indent=2,
    )

    repair_payload = {
        "brief": brief,
        "retrieved_templates": retrieved_templates,
        "original_result": result,
    }

    return call_llm(
        repair_prompt,
        repair_payload,
    )


def generate_r2(brief_id: str) -> dict:

    brief = load_brief(brief_id)

    retrieved = retrieve_templates(
        brief,
        top_k=3,
    )

    retrieved_templates = attach_full_templates(
        retrieved,
        load_template_library(),
    )

    template_ids = [
        item["template_id"]
        for item in retrieved_templates
    ]

    system_prompt = PROMPT_PATH.read_text(
        encoding="utf-8"
    )

    # ---------------------------------------------------------
    # Initial generation
    # ---------------------------------------------------------

    result = call_llm(
        system_prompt,
        {
            "brief": brief,
            "retrieved_templates": retrieved_templates,
        },
    )

    # ---------------------------------------------------------
    # Validate initial result
    # ---------------------------------------------------------

    validation_errors = validate_r2(
        result=result,
        brief=brief,
        retrieved_template_ids=template_ids,
    )

    # ---------------------------------------------------------
    # One bounded repair attempt
    # ---------------------------------------------------------

    if validation_errors:

        result = repair_result(
            result=result,
            validation_errors=validation_errors,
            brief=brief,
            retrieved_templates=retrieved_templates,
        )

        # Validate repaired result
        validation_errors = validate_r2(
            result=result,
            brief=brief,
            retrieved_template_ids=template_ids,
        )

        if validation_errors:

            raise ValueError(
                "R2 output failed validation after one repair attempt:\n"
                + "\n".join(
                    f"- {error}"
                    for error in validation_errors
                )
            )

    # ---------------------------------------------------------
    # Add application metadata
    # ---------------------------------------------------------

    result["brief_id"] = brief_id
    result["template_ids_used"] = template_ids
    result["model"] = MODEL_NAME

    if isinstance(
        result.get("poc_plan"),
        dict,
    ):
        result["poc_plan"][
            "template_ids_used"
        ] = template_ids

    handoff = result.get(
        "delivery_handoff"
    )

    if (
        isinstance(handoff, dict)
        and isinstance(
            handoff.get("notes_for_delivery"),
            str,
        )
    ):
        handoff["notes_for_delivery"] = [
            handoff["notes_for_delivery"]
        ]

    return result


def test_brief_001() -> Path:

    result = generate_r2(
        "BRIEF-001"
    )

    required = {
        "brief_id",
        "template_ids_used",
        "match_explanations",
        "poc_plan",
        "delivery_handoff",
    }

    missing = required - set(result)

    if missing:
        raise AssertionError(
            f"R2 JSON missing keys: {sorted(missing)}"
        )

    if len(
        result["template_ids_used"]
    ) != 3:

        raise AssertionError(
            "Expected 3 template IDs"
        )

    if len(
        result["match_explanations"]
    ) != 3:

        raise AssertionError(
            "Expected 3 match explanations"
        )

    output_path = (
        OUTPUT_DIR
        / "r2_BRIEF-001.json"
    )

    output_path.write_text(
        json.dumps(
            result,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        json.dumps(
            result,
            indent=2,
        )
    )

    print(
        f"Saved {output_path}"
    )

    return output_path


if __name__ == "__main__":
    test_brief_001()