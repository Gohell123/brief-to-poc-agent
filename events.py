from datetime import datetime, timezone
from uuid import uuid4


def create_os_event(
    event_type: str,
    owner: str,
    brief_id: str,
    metadata: dict | None = None,
) -> dict:
    return {
        "event_id": str(uuid4()),
        "event_type": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "owner": owner,
        "brief_id": brief_id,
        "metadata": metadata or {},
    }