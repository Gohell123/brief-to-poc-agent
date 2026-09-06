import json
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

from generate_r2 import generate_r2
from sla import seam_health


ROOT = Path(__file__).resolve().parent
BRIEFS_PATH = ROOT / "data" / "briefs.json"
EVENTS_PATH = ROOT / "data" / "os_events.json"


st.set_page_config(
    page_title="Brief → POC Control Surface",
    layout="wide",
)


# ---------------------------------------------------------
# Data loading
# ---------------------------------------------------------

def load_briefs() -> list[dict]:
    return json.loads(
        BRIEFS_PATH.read_text(encoding="utf-8")
    )


def load_events() -> list[dict]:
    return json.loads(
        EVENTS_PATH.read_text(encoding="utf-8")
    )


briefs = load_briefs()
events = load_events()

events_by_brief = {
    event["brief_id"]: event
    for event in events
}


# ---------------------------------------------------------
# Session state
# ---------------------------------------------------------

if "selected_brief_id" not in st.session_state:
    st.session_state.selected_brief_id = briefs[0]["brief_id"]

if "r2_result" not in st.session_state:
    st.session_state.r2_result = None


# ---------------------------------------------------------
# Page
# ---------------------------------------------------------

st.title("Brief → POC Control Surface")
st.caption("Sales → PreSales handoff")


# ---------------------------------------------------------
# Open Handoffs
# ---------------------------------------------------------

st.subheader("Open Handoffs")

header1, header2, header3, header4, header5, header6 = st.columns(
    [3, 1, 1.5, 1.2, 1.2, 1]
)

header1.write("**Account**")
header2.write("**Region**")
header3.write("**Segment**")
header4.write("**Brief ID**")
header5.write("**Seam Health**")
header6.write("**Action**")


for brief in briefs:

    col1, col2, col3, col4, col5, col6 = st.columns(
        [3, 1, 1.5, 1.2, 1.2, 1]
    )

    col1.write(brief["account"])
    col2.write(brief["region"])
    col3.write(brief["segment"])
    col4.write(brief["brief_id"])

    event = events_by_brief[brief["brief_id"]]

    health = seam_health(
        event["timestamp"],
        now=datetime.now(timezone.utc),
    )

    health_label = {
        "green": "🟢 Green",
        "amber": "🟡 Amber",
        "red": "🔴 Red",
    }[health["health"]]

    col5.write(health_label)

    if col6.button(
        "Open",
        key=f"open_{brief['brief_id']}",
    ):
        st.session_state.selected_brief_id = brief["brief_id"]

        # Clear previous generated draft when changing brief
        st.session_state.r2_result = None


st.divider()


# ---------------------------------------------------------
# Current Brief
# ---------------------------------------------------------

selected_brief = next(
    brief
    for brief in briefs
    if brief["brief_id"] == st.session_state.selected_brief_id
)

selected_event = events_by_brief[selected_brief["brief_id"]]


st.subheader("Current Brief")

col1, col2 = st.columns(2)


with col1:

    st.write("**Account**")
    st.write(selected_brief["account"])

    st.write("**Business problem**")
    st.write(selected_brief["business_problem"])

    st.write("**Systems**")
    st.write(", ".join(selected_brief["systems"]))


with col2:

    st.write("**Region**")
    st.write(selected_brief["region"])

    st.write("**Regulator**")
    st.write(selected_brief["regulator"])

    st.write("**Expected timeline**")
    st.write(selected_brief["expected_timeline"])


# ---------------------------------------------------------
# Seam Health
# ---------------------------------------------------------

st.subheader("Seam Health")

current_health = seam_health(
    selected_event["timestamp"],
    now=datetime.now(timezone.utc),
)

health = current_health["health"]


if health == "green":
    st.success("🟢 GREEN — handoff is within SLA.")

elif health == "amber":
    st.warning("🟡 AMBER — handoff is approaching SLA breach.")

else:
    st.error("🔴 RED — handoff has breached the SLA.")


metric1, metric2, metric3 = st.columns(3)

metric1.metric(
    "Elapsed business days",
    current_health["elapsed_business_days"],
)

metric2.metric(
    "SLA",
    f"{current_health['sla_business_days']} days",
)

metric3.metric(
    "SLA progress",
    f"{current_health['sla_progress'] * 100:.0f}%",
)


# ---------------------------------------------------------
# Generate POC Plan
# ---------------------------------------------------------

st.divider()

st.subheader("AI-Generated POC Plan")

if st.button(
    "Generate POC Plan",
    type="primary",
):

    with st.spinner("Retrieving templates and generating POC plan..."):

        try:
            st.session_state.r2_result = generate_r2(
                selected_brief["brief_id"]
            )

        except Exception as exc:
            st.error(f"Generation failed: {exc}")


# ---------------------------------------------------------
# Display R2 result
# ---------------------------------------------------------

if st.session_state.r2_result:

    result = st.session_state.r2_result

    st.write("### Recommended Templates")

    for match in result.get("match_explanations", []):

        template_id = match.get("template_id", "Unknown")
        explanation = match.get("explanation", "")

        st.write(f"**{template_id}**")
        st.write(explanation)


    st.write("### POC Plan")

    poc_plan = result.get("poc_plan", {})

    if poc_plan:

        st.write("**Objective**")
        st.write(poc_plan.get("objective", ""))

        st.write("**Success Criteria**")

        for criterion in poc_plan.get("success_criteria", []):
            st.write(f"- {criterion}")

        st.write("**Scope In**")

        for item in poc_plan.get("scope_in", []):
            st.write(f"- {item}")

        st.write("**Scope Out**")

        for item in poc_plan.get("scope_out", []):
            st.write(f"- {item}")

        st.write("**Week-by-Week Plan**")

        for item in poc_plan.get("week_by_week_plan", []):
            st.write(f"- {item}")


    st.write("### Delivery Handoff")

    handoff = result.get("delivery_handoff", {})

    if handoff:

        st.write("**Summary**")
        st.write(handoff.get("summary", ""))

        st.write("**Integrations**")

        for integration in handoff.get("integrations", []):
            st.write(f"- {integration}")

        st.write("**Notes for Delivery**")

        notes = handoff.get("notes_for_delivery", [])

        if isinstance(notes, str):
            notes = [notes]

        for note in notes:
            st.write(f"- {note}")