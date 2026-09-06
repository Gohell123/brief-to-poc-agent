import json
import urllib.error
import urllib.request
from pathlib import Path

from retrieve_templates import ROOT, TEMPLATES_PATH, load_brief, retrieve_templates

MODEL_NAME = "qwen3:8b"
OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
PROMPT_PATH = ROOT / "prompts" / "r2_generation.txt"
OUTPUT_DIR = ROOT / "data"


def load_template_library() -> dict:
    templates = json.loads(TEMPLATES_PATH.read_text(encoding="utf-8"))
    return {template["template_id"]: template for template in templates}


def attach_full_templates(retrieved: list[dict], library: dict) -> list[dict]:
    records = []
    for item in retrieved:
        template = dict(library[item["template_id"]])
        template["similarity"] = item["similarity"]
        records.append(template)
    return records


def call_llm(system_prompt: str, user_payload: dict) -> dict:
    body = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": json.dumps(user_payload, indent=2),
            },
        ],
        "stream": False,
        "format": "json",
        "think": False,
        "options": {"temperature": 0.1},
    }
    request = urllib.request.Request(
        OLLAMA_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=600) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise RuntimeError(
            "Ollama is not reachable at 127.0.0.1:11434. Start it, then retry."
        ) from exc

    content = payload["message"]["content"]
    if isinstance(content, dict):
        return content
    return json.loads(content)


def generate_r2(brief_id: str) -> dict:
    brief = load_brief(brief_id)
    retrieved = retrieve_templates(brief, top_k=3)
    retrieved_templates = attach_full_templates(retrieved, load_template_library())
    template_ids = [item["template_id"] for item in retrieved_templates]

    result = call_llm(
        PROMPT_PATH.read_text(encoding="utf-8"),
        {"brief": brief, "retrieved_templates": retrieved_templates},
    )

    result["brief_id"] = brief_id
    result["template_ids_used"] = template_ids
    result["model"] = MODEL_NAME
    if isinstance(result.get("poc_plan"), dict):
        result["poc_plan"]["template_ids_used"] = template_ids
    handoff = result.get("delivery_handoff")
    if isinstance(handoff, dict) and isinstance(handoff.get("notes_for_delivery"), str):
        handoff["notes_for_delivery"] = [handoff["notes_for_delivery"]]
    return result


REQUIRED_R2_FIELDS = {
    "brief_id",
    "template_ids_used",
    "match_explanations",
    "poc_plan",
    "delivery_handoff",
}
TEST_BRIEF_IDS = ("BRIEF-001", "BRIEF-002", "BRIEF-003")


def validate_r2(result: dict, brief_id: str) -> None:
    missing = REQUIRED_R2_FIELDS - set(result)
    if missing:
        raise AssertionError(f"{brief_id} missing keys: {sorted(missing)}")
    if result.get("brief_id") != brief_id:
        raise AssertionError(f"{brief_id} brief_id mismatch: {result.get('brief_id')}")
    if len(result["template_ids_used"]) != 3:
        raise AssertionError(f"{brief_id}: expected 3 template IDs")
    if len(result["match_explanations"]) != 3:
        raise AssertionError(f"{brief_id}: expected 3 match explanations")
    if not isinstance(result["poc_plan"], dict):
        raise AssertionError(f"{brief_id}: poc_plan must be an object")
    if not isinstance(result["delivery_handoff"], dict):
        raise AssertionError(f"{brief_id}: delivery_handoff must be an object")


def test_r2_briefs(brief_ids: tuple[str, ...] = TEST_BRIEF_IDS) -> list[Path]:
    saved = []
    for brief_id in brief_ids:
        result = generate_r2(brief_id)
        validate_r2(result, brief_id)
        output_path = OUTPUT_DIR / f"r2_{brief_id}.json"
        output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(json.dumps(result, indent=2))
        print(f"Saved {output_path}")
        saved.append(output_path)
    return saved


if __name__ == "__main__":
    test_r2_briefs()
