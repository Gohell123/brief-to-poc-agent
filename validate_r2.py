def validate_r2(result: dict, brief: dict, retrieved_template_ids: list[str]) -> list[str]:
    """
    Validate the structural and grounding constraints of an R2 result.

    Returns a list of validation errors.
    An empty list means the result passed validation.
    """

    errors = []

    # ---------------------------------------------------------
    # Top-level structure
    # ---------------------------------------------------------

    required_top_level = {
        "match_explanations",
        "poc_plan",
        "delivery_handoff",
    }

    missing = required_top_level - set(result)

    if missing:
        errors.append(
            f"Missing top-level fields: {sorted(missing)}"
        )

    poc_plan = result.get("poc_plan", {})
    delivery_handoff = result.get("delivery_handoff", {})

    # ---------------------------------------------------------
    # POC plan structure
    # ---------------------------------------------------------

    required_poc_fields = {
        "title",
        "objective",
        "scope_in",
        "scope_out",
        "week_by_week_plan",
        "systems",
        "success_criteria",
        "timeline",
        "template_ids_used",
        "proposed_changes",
    }

    missing = required_poc_fields - set(poc_plan)

    if missing:
        errors.append(
            f"Missing POC plan fields: {sorted(missing)}"
        )

    # ---------------------------------------------------------
    # Template IDs
    # ---------------------------------------------------------

    actual_template_ids = poc_plan.get(
        "template_ids_used",
        [],
    )

    if actual_template_ids != retrieved_template_ids:
        errors.append(
            "POC plan template_ids_used does not match retrieved templates"
        )

    # ---------------------------------------------------------
    # Systems grounding
    # ---------------------------------------------------------

    brief_systems = set(brief.get("systems", []))
    plan_systems = set(poc_plan.get("systems", []))

    unsupported_systems = plan_systems - brief_systems

    if unsupported_systems:
        errors.append(
            f"POC plan contains unsupported systems: "
            f"{sorted(unsupported_systems)}"
        )

    # ---------------------------------------------------------
    # Timeline grounding
    # ---------------------------------------------------------

    brief_timeline = brief.get("expected_timeline")

    if poc_plan.get("timeline") != brief_timeline:
        errors.append(
            "POC plan timeline does not match Brief expected_timeline"
        )

    # ---------------------------------------------------------
    # Success criteria grounding
    # ---------------------------------------------------------

    brief_success = set(brief.get("success_criteria", []))
    plan_success = set(poc_plan.get("success_criteria", []))

    unsupported_success = plan_success - brief_success

    if unsupported_success:
        errors.append(
            "POC plan contains success criteria not present in the Brief: "
            f"{sorted(unsupported_success)}"
        )

    # ---------------------------------------------------------
    # Delivery integrations
    # ---------------------------------------------------------

    brief_systems = set(brief.get("systems", []))
    integrations = set(
        delivery_handoff.get("integrations", [])
    )

    unsupported_integrations = integrations - brief_systems

    if unsupported_integrations:
        errors.append(
            "Delivery handoff contains unsupported integrations: "
            f"{sorted(unsupported_integrations)}"
        )

    # ---------------------------------------------------------
    # Recommended template
    # ---------------------------------------------------------

    recommended_template = delivery_handoff.get(
        "recommended_template_id"
    )

    if recommended_template not in retrieved_template_ids:
        errors.append(
            "Recommended template is not one of the retrieved templates"
        )

    return errors