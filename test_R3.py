from decision import record_decision


def main():

    accepted = record_decision(
        brief_id="BRIEF-001",
        decision="accepted",
        template_ids=["UK-001"],
    )

    print("ACCEPT:")
    print(accepted)

    edited = record_decision(
        brief_id="BRIEF-001",
        decision="edited",
        template_ids=["UK-001"],
        edited_plan={
            "title": "Updated KYC Document Review POC",
            "timeline": "4 weeks",
        },
    )

    print("\nEDIT:")
    print(edited)

    rejected = record_decision(
        brief_id="BRIEF-002",
        decision="rejected",
        template_ids=["UK-003"],
    )

    print("\nREJECT:")
    print(rejected)


if __name__ == "__main__":
    main()