from datetime import datetime, time, timedelta, timezone


SLA_BUSINESS_DAYS = 2
AMBER_THRESHOLD = 0.70
SECONDS_PER_BUSINESS_DAY = 24 * 60 * 60


def parse_timestamp(timestamp: str) -> datetime:
    dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return dt


def business_seconds_between(start: datetime, end: datetime) -> float:
    """Count elapsed time only on Monday-Friday."""
    if end <= start:
        return 0.0

    total_seconds = 0.0
    current = start

    while current < end:
        next_day = datetime.combine(
            current.date() + timedelta(days=1),
            time.min,
            tzinfo=current.tzinfo,
        )

        segment_end = min(next_day, end)

        if current.weekday() < 5:
            total_seconds += (segment_end - current).total_seconds()

        current = next_day

    return total_seconds


def seam_health(event_timestamp: str, now: datetime | None = None) -> dict:
    start = parse_timestamp(event_timestamp)

    if now is None:
        now = datetime.now(timezone.utc)

    elapsed = business_seconds_between(start, now)
    sla_seconds = SLA_BUSINESS_DAYS * SECONDS_PER_BUSINESS_DAY
    progress = elapsed / sla_seconds

    if progress >= 1.0:
        health = "red"
    elif progress >= AMBER_THRESHOLD:
        health = "amber"
    else:
        health = "green"

    return {
        "health": health,
        "elapsed_business_days": round(elapsed / SECONDS_PER_BUSINESS_DAY, 2),
        "sla_business_days": SLA_BUSINESS_DAYS,
        "sla_progress": round(progress, 2),
        "breached": health == "red",
    }