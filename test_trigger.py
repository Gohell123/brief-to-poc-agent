from datetime import datetime, timezone

from trigger import check_seam_and_trigger


def main():
    draft = {
        "objective": "Build KYC document review POC",
        "template_ids_used": ["UK-001", "IN-001"],
    }

    result = check_seam_and_trigger(
        brief_id="BRIEF-001",
        event_timestamp="2026-09-04T09:00:00+00:00",
        draft=draft,
        now=datetime(2026, 9, 8, 10, 0, tzinfo=timezone.utc),
    )

    print(result)

    assert result["triggered"] is True
    assert result["health"]["health"] == "red"
    assert result["event"]["event_type"] == "seam.sla_breached"
    assert result["event"]["metadata"]["draft"] == draft

    print("\nR4 trigger test passed.")


if __name__ == "__main__":
    main()