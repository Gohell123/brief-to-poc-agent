import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
FEEDBACK_PATH = ROOT / "data" / "template_feedback.json"


def load_feedback() -> dict:
    if not FEEDBACK_PATH.exists():
        return {}

    return json.loads(FEEDBACK_PATH.read_text(encoding="utf-8"))


def record_feedback(template_ids: list[str], decision: str) -> dict:
    if decision not in {"accepted", "rejected"}:
        raise ValueError("Decision must be accepted or rejected")

    feedback = load_feedback()

    delta = 1 if decision == "accepted" else -1

    for template_id in template_ids:
        if template_id not in feedback:
            feedback[template_id] = {
                "accepted": 0,
                "rejected": 0,
            }

        feedback[template_id][decision] += 1

    FEEDBACK_PATH.write_text(
        json.dumps(feedback, indent=2),
        encoding="utf-8",
    )

    return feedback


def feedback_score(template_id: str) -> float:
    feedback = load_feedback()

    stats = feedback.get(
        template_id,
        {"accepted": 0, "rejected": 0},
    )

    return (
        0.02 * stats["accepted"]
        - 0.02 * stats["rejected"]
    )