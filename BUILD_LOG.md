Build Log — Brief-to-POC Agent

Architecture

Won Opportunity Event → Brief → Template Retrieval → AI Agent
                                      ↓
                         POC Plan + Delivery Handoff
                                      ↓
                         US Solution Architect
                           Accept / Edit / Reject
                                      ↓
                                  OS Event
                                      ↓
                         Feedback → Template Ranking

OS Event → SLA Calculation → Green / Amber / Red
                                      ↓
                               SLA Breach → Trigger

The Streamlit control surface exposes the queue, Brief, seam health, draft,
templates and human actions. Retrieval, generation, human decisions,
feedback, SLA and trigger logic remain separate modules.

1. R1 — Event In

Decision: Synthetic CRM-style opportunity.won OS events with 3 varied
Briefs containing timestamp, owner, account, region, segment, regulator,
business problem, systems, timeline and success criteria.

Why: Demonstrates the required event boundary without spending the
8-hour POC on real CRM integration.

Assumption: Production would receive the event from CRM when an
opportunity moves to Won.

2. Embedding & Retrieval

Decision: Local BAAI/bge-small-en-v1.5; cosine similarity; top 3 of
8 synthetic templates.

Why: Sufficient for the POC scale and avoids unnecessary vector-DB
infrastructure.

AI Tool / Prompt: Cursor Agent / prompts/embed_templates.txt,
prompts/retrieval.txt.

Validation: All 3 Briefs tested; the correct domain template ranked #1.

Discarded: Cohere Embed v4 via Bedrock (AWS model access blocked) and
production vector DB (unnecessary at 8 templates).

3. R2 — Agent Generation

Decision: Ollama + Qwen3 8B. Generation instructions are maintained in
prompts/r2_generation.txt.

Why: Local, reproducible and no API-key dependency.

Model iteration: Qwen3 1.7B showed grounding/instruction-following
errors, so Qwen3 8B was selected after materially better results.

Validation: generate_r2.py produced structured match explanations,
POC plan, Delivery handoff, template IDs and proposed changes.

AI development: Cursor Agent was used for implementation and prompt
iteration.

Known limitation: Local Qwen3 8B can be slow. The Streamlit demo uses a
deterministic synthetic R2 draft so R3 can be tested interactively without
waiting for LLM generation; the real R2 path remains implemented.

4. R3 — Human Decision & Learning

Decision: The US Solution Architect owns Accept / Edit / Reject.
Each decision creates a timestamped OS event. Accepted/edited decisions
add positive feedback; rejected decisions add negative feedback.

Implementation: decision.py, events.py, feedback.py and
retrieve_templates.py.

Learning: final_score = semantic_similarity + feedback_score, with
accepted = +0.02 and rejected = -0.02.

Validation: Accept, Edit and Reject tested; OS events and persisted
feedback verified; feedback changes subsequent ranking.

5. R4 — Seam Health & Trigger

Decision: 2-business-day SLA calculated from the OS event timestamp.
Green <70%, Amber 70–100%, Red >100%.

On breach: create seam.sla_breached, assign the US Solution Architect,
attach SLA context and draft, and persist the trigger locally.

Assumptions: 70% amber threshold was selected because the requirement
does not specify one. “Continuously” is implemented by recalculation on
system check/refresh rather than a background scheduler.

Validation: Green, Amber, Red, business-day calculation and breach
trigger tested.

6. R5 — Control Surface

Decision: Streamlit for the one-screen control surface.

Includes: open handoffs, Brief, seam health/SLA, generated plan,
recommended templates, Delivery handoff and Accept/Reject actions.

The UI calls the existing R2/R3/R4 modules rather than duplicating logic.

7. R6 — AI-Assisted Development

AI was used for decomposition, implementation, debugging, prompt
iteration, model evaluation and architecture decisions. Prompts used during
the build are retained under prompts/.

Key Architectural Decisions

Event-driven state: OS events are the source of truth for important
handoff actions.

Retrieval before generation: templates are retrieved first and supplied
to the LLM as grounding context.

Human-in-the-loop: AI performs volume work; the US Solution Architect
makes the final decision.

Deterministic business logic: SLA, events, feedback and ranking
adjustments are handled in Python, not by the LLM.

Lightweight learning: human feedback adjusts ranking rather than
training a separate model.

Deliberate Cuts

Real CRM/notification integrations, production vector DB, background SLA
scheduler, production auth/RBAC/database, fine-tuning, full evaluation
harness, multi-agent orchestration and deployment infrastructure were cut
to honor the one-day constraint. See CUT_LIST.md.

Synthetic Data

8 reusable templates across UK/India and 3 synthetic US Briefs are used.
No proprietary customer data is used.

Validation Summary

R1 event flow, retrieval, R2 generation, R3 decisions/feedback, R4 SLA and
trigger behavior, and R5 interactive control-surface actions were tested
within the POC time box.