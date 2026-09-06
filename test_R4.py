from datetime import datetime, timezone

from sla import seam_health


def test_green():
    event_time = "2026-09-07T09:00:00+00:00"
    now = datetime(2026, 9, 7, 15, 0, tzinfo=timezone.utc)

    result = seam_health(event_time, now)

    print("GREEN TEST")
    print(result)
    assert result["health"] == "green"


def test_amber():
    event_time = "2026-09-07T09:00:00+00:00"
    now = datetime(2026, 9, 8, 21, 0, tzinfo=timezone.utc)

    result = seam_health(event_time, now)

    print("\nAMBER TEST")
    print(result)
    assert result["health"] == "amber"


def test_red():
    event_time = "2026-09-04T09:00:00+00:00"  # Friday
    now = datetime(2026, 9, 8, 10, 0, tzinfo=timezone.utc)  # Tuesday

    result = seam_health(event_time, now)

    print("\nRED TEST")
    print(result)
    assert result["health"] == "red"


if __name__ == "__main__":
    test_green()
    test_amber()
    test_red()
    print("\nR4 SLA tests passed.")