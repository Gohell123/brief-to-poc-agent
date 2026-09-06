import json
from datetime import datetime, timezone
from pathlib import Path

from events import create_os_event
from sla import seam_health


ROOT = Path(__file__).resolve().parent
TRIGGER_LOG = ROOT / "data" / "trigger_log.json"

TRIGGER_OWNER = "US Solution Architect"


def load_trigger_log() -> list[dict]:
    if not TRIGGER_LOG.exists():
        return []

    return json.loads(TRIGGER_LOG.read_text(encoding="utf-8"))


def save_trigger_log(events: list[dict]) -> None:
    TRIGGER_LOG.write_text(
        json.dumps(events, indent=2),
        encoding="utf-8",
    )


def check_seam_and_trigger(
    brief_id: str,
    event_timestamp: str,
    draft: dict,
    owner: str = TRIGGER_OWNER,
    now: datetime | None = None,
) -> dict:

    health = seam_health(event_timestamp, now)

    if not health["breached"]:
        return {
            "triggered": False,
            "health": health,
        }

    event = create_os_event(
        event_type="seam.sla_breached",
        owner=owner,
        brief_id=brief_id,
        metadata={
            "health": health,
            "draft": draft,
            "triggered_at": datetime.now(timezone.utc).isoformat(),
        },
    )

    trigger_log = load_trigger_log()
    trigger_log.append(event)
    save_trigger_log(trigger_log)

    return {
        "triggered": True,
        "health": health,
        "event": event,
    }