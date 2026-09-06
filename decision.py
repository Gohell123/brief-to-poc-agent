from events import create_os_event
from feedback import record_feedback


HUMAN_ROLE = "US Solution Architect"


def record_decision(
    brief_id: str,
    decision: str,
    template_ids: list[str],
    edited_plan: dict | None = None,
) -> dict:

    if decision not in {"accepted", "edited", "rejected"}:
        raise ValueError(
            "Decision must be accepted, edited, or rejected"
        )

    metadata = {
        "decision": decision,
        "template_ids": template_ids,
    }

    if edited_plan is not None:
        metadata["edited_plan"] = edited_plan

    event = create_os_event(
        event_type=f"poc_plan.{decision}",
        owner=HUMAN_ROLE,
        brief_id=brief_id,
        metadata=metadata,
    )

    feedback_decision = (
        "accepted"
        if decision in {"accepted", "edited"}
        else "rejected"
    )

    record_feedback(
        template_ids=template_ids,
        decision=feedback_decision,
    )

    return event