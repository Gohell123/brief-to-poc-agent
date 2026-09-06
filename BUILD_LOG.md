# Build Log — Brief-to-POC Agent

## Overall Architecture

The system implements the required Brief-to-POC-Plan loop:

Won Opportunity Event
        ↓
      Brief
        ↓
 Template Retrieval
        ↓
 AI Agent
        ↓
POC Plan + Delivery Handoff
        ↓
 US Solution Architect
   Accept / Edit / Reject
        ↓
    OS Event
        ↓
Feedback → Template Ranking

In parallel:

OS Event → SLA Calculation → Green / Amber / Red
                              ↓
                         SLA Breach
                              ↓
                     Automatic Trigger

The Streamlit control surface brings the queue, Brief, seam health,
generated draft, recommended templates, trigger information and human
actions into one screen.

The architecture deliberately separates:
- retrieval
- generation
- human decision
- feedback
- SLA calculation
- trigger handling
- UI

This keeps the POC simple while allowing individual components to be
replaced by production services later.

---

## 1. R1 — Event In

**Requirement:** A won opportunity arrives as an OS event carrying the
Brief, including timestamp, owner and account.

**Decision:** Use a synthetic CRM-style `opportunity.won` OS event.

**Why:** The challenge allows synthetic data and does not require a real
CRM integration. The event shape demonstrates how a production webhook
would enter the system without spending the limited build time on
integration setup.

**Synthetic data:**
- 3 Briefs
- Timestamp
- Owner
- Account
- Region
- Segment
- Regulator
- Business problem
- Systems
- Expected timeline
- POC success criteria

**Assumption:** In production, the event would originate from the CRM
when an opportunity moves to Won. For the POC, the event is represented
locally.

---

## 2. Template Embedding

**Requirement:** Generate embeddings for the 8 solution templates.

**Decision:** Use local `BAAI/bge-small-en-v1.5`.

**Why:** Cohere Embed v4 through Bedrock was blocked by the AWS account.
Local embedding avoids the dependency and fits the 8-hour POC.

**AI Tool:** Cursor Agent

**Prompt:**

"Implement the template embedding step.

- Read data/template_documents.json
- Use BAAI/bge-small-en-v1.5 with sentence-transformers
- Generate embeddings for all 8 templates
- Save them to data/template_embeddings.json
- Each record should contain template_id and embedding
- Create embed_templates.py
- Keep it simple; don't build retrieval, vector DB, agent, or UI yet.
- First show me your plan, then implement."

**Result:** Cursor created `embed_templates.py` and generated embeddings
for all 8 templates.

**Validation:** 8 embeddings, 384 dimensions.

**Discarded approach:** Cohere Embed v4 via Amazon Bedrock because model
invocation was blocked for the AWS account.

---

## 3. Template Retrieval

**Requirement:** Retrieve relevant solution templates from the template
library for an incoming Brief.

**Decision:** Use BGE embeddings with cosine similarity. Retrieve the top
3 templates from the 8-template synthetic library.

**Why:** The POC has only 8 templates, so direct in-memory similarity
search is sufficient. A vector database would add infrastructure without
providing meaningful value at this scale.

**AI Tool:** Cursor Agent

**Prompt:**

"Implement template retrieval.

- Read template embeddings from data/template_embeddings.json
- Embed a Brief using BAAI/bge-small-en-v1.5
- Calculate cosine similarity against all template embeddings
- Return top 3 template_ids with scores
- Use data/templates.json to return the full template metadata
- Create retrieve_templates.py
- Add a simple test using BRIEF-001
- No vector DB or UI yet."

**Validation:**

Tested all 3 synthetic Briefs:

- BRIEF-001 → UK-001 KYC
- BRIEF-002 → UK-003 Claims
- BRIEF-003 → UK-002 Underwriting

The correct domain template ranked #1 for each Brief.

**Result:** Retrieval successfully identifies relevant templates across
different financial-services use cases.

**Discarded approach:** Vector database at this stage. Direct cosine
similarity is simpler and faster for an 8-template POC.

---

## 4. R2 — Agent Generation

**Requirement:** From a Brief and retrieved templates, generate match
explanations, an editable POC plan and an editable Delivery handoff.

**Decision:** Use local Ollama with Qwen3 8B.

**Why:** Local execution avoids API keys and external dependencies and
keeps the demo reproducible.

The generation instructions are kept separately in
`prompts/r2_generation.txt` so prompt iteration does not require code
changes.

**AI Tool:** Cursor Agent

**Prompt:**

"Implement R2 generation.

- Take a Brief and the top 3 retrieved templates
- Use a suitable LLM to explain matches, draft a POC plan, and draft a
  Delivery handoff
- Base output only on the Brief and retrieved templates
- Include template IDs used and proposed changes
- Return structured JSON
- Keep prompt/instructions in a separate file
- Choose the LLM for speed and simplicity, and document the choice
- Test with BRIEF-001
- No UI yet"

### Model iteration

**Initial model:** Qwen3 1.7B.

**Failure:** Testing showed recurring instruction-following and grounding
errors, including mixing Brief systems with template integrations and
making unsupported claims.

**Change:** Switched to Qwen3 8B.

**Result:** Qwen3 8B produced materially better template reasoning,
source separation and structured output using the same retrieval inputs
and generation prompt.

**Final decision:** Qwen3 8B for the POC.

**Validation:** `generate_r2.py` successfully produces structured R2
output including:
- match explanations
- POC plan
- Delivery handoff
- template IDs used
- proposed changes

**Discarded approaches:**
- Qwen3 1.7B due to grounding/instruction-following quality.
- Cloud LLM integration because local Ollama was already available and
  the POC was time constrained.

---

## 5. R3 — Human Decision and Feedback Learning

**Requirement:** The US Solution Architect accepts, edits or rejects the
draft. The decision becomes an OS event and feeds back into reuse and
template ranking.

**Decision:**

- Human decision-maker = US Solution Architect.
- Supported actions = Accept / Edit / Reject.
- Each decision creates an OS event.
- Accepted and edited decisions provide positive feedback.
- Rejected decisions provide negative feedback.
- Template ranking incorporates this feedback.

**Implementation:**

- `decision.py` records the human decision.
- `events.py` creates timestamped OS events.
- `feedback.py` persists feedback.
- `data/template_feedback.json` stores acceptance/rejection counts.
- `retrieve_templates.py` incorporates feedback into ranking.

**Feedback scoring:**

- Accepted = +0.02
- Rejected = -0.02
- Final ranking score = semantic similarity + feedback score

**Why:** The requirement specifies that ranking should learn from
acceptance/rejection but does not prescribe a learning algorithm.
A lightweight feedback-based ranking mechanism was chosen instead of
training a separate ML model.

**Validation:**

- Accept tested.
- Edit tested.
- Reject tested.
- OS events verified with timestamp, owner, Brief ID and decision.
- Feedback persistence verified.
- Feedback score verified to influence subsequent ranking.

---

## 6. R4 — Seam Health and Automatic Trigger

**Requirement:** Continuously calculate Brief age against the two-business-
day SLA, show green/amber/red health and trigger escalation on breach.

**Decision:**

- SLA = 2 business days.
- Health calculated automatically from the OS event timestamp.
- Green = below 70% of SLA.
- Amber = 70–100% of SLA.
- Red = SLA breached.

**Trigger:**

On breach:
- create `seam.sla_breached` OS event
- assign it to the US Solution Architect
- attach SLA context
- attach the current draft
- persist the trigger in the trigger log

For the POC, the trigger is represented locally rather than integrated
with Slack/email.

**Assumptions:**

- The requirement defines green/amber/red but does not define the amber
  threshold, so 70% was selected.
- "Continuously" is implemented by recalculating health whenever the
  system checks/refreshes the seam rather than introducing a background
  scheduler.

**Validation:**

- Green state tested.
- Amber state tested.
- Red state tested.
- Business-day calculation tested.
- Breach trigger tested.
- Draft attachment verified.

---

## 7. R5 — One Control Surface

**Requirement:** One screen must contain the queue, seam health,
current draft, trigger log and actions.

**Decision:** Use Streamlit.

**Why:** Streamlit provides the fastest path to an interactive control
surface within the one-day constraint.

**Control surface includes:**

- Open Handoffs queue
- Open action
- Current Brief
- Seam Health
- SLA information
- AI-generated POC plan
- Recommended templates
- Delivery handoff
- Human decision actions

The Open action changes the currently selected Brief, allowing the
Solution Architect to work on a specific handoff rather than viewing
static information.

**Architecture decision:** The UI calls the existing R2/R3/R4 modules
rather than duplicating retrieval, decision or SLA logic.

---

## 8. R6 — AI-Assisted Development

AI was used throughout the build for:
- decomposition
- implementation
- code generation
- debugging
- prompt iteration
- model evaluation
- architectural trade-off discussion

The main AI iteration was the R2 generation prompt and model selection.

The build process deliberately used small implementation steps so each
requirement could be independently tested before moving to the next.

---

## 9. Key Architectural Decisions

### Event-driven state

OS events are the source of truth for important handoff actions.
Examples:
- opportunity won
- POC plan accepted
- POC plan edited
- POC plan rejected
- SLA breached

This follows the RevenueOS requirement that handoffs are represented as
timestamped, owned events.

### Retrieval before generation

The LLM does not search an unstructured knowledge base itself. The
application first retrieves candidate templates and passes those
grounded records to the generation step.

This makes template recommendations explainable and allows retrieval to
be evaluated independently.

### Human-in-the-loop

The AI owns volume work:
- retrieval
- matching
- drafting

The US Solution Architect owns the final decision.

This deliberately keeps business judgement outside the agent.

### Deterministic business logic outside the LLM

SLA calculation, event creation, feedback persistence and ranking
adjustment are implemented in Python rather than delegated to the LLM.

This makes these behaviors deterministic and testable.

### Local-first architecture

BGE embeddings and Qwen3 8B run locally.

This was selected for:
- reproducibility
- no API key dependency
- fast setup
- suitability for an 8-hour POC

### Lightweight learning

Feedback is implemented as a ranking adjustment rather than model
training.

This demonstrates the required learning loop without introducing an
additional ML training pipeline.

---

## 10. Deliberate Cuts

The following were intentionally not implemented because of the
one-day constraint:

- Production CRM integration
- Real Slack/email trigger integration
- Production vector database
- Background SLA scheduler
- Authentication/RBAC
- Persistent production database
- Model fine-tuning
- Full evaluation harness
- Multi-agent architecture
- Production deployment infrastructure

These can be introduced independently without changing the core
Brief → Retrieve → Draft → Human Decision → Feedback → SLA loop.

---

## 11. Known Limitation

Local Qwen3 8B generation can be slow.

The core retrieval, human-decision, feedback, SLA and trigger paths were
validated independently. The POC prioritizes demonstrating the complete
architecture and control loop within the eight-hour constraint rather
than optimizing local LLM latency.

---

## 12. Synthetic Data

All Briefs, solution templates and OS events used for the POC are
synthetic.

The template library contains 8 templates across UK and India and covers
financial-services use cases including KYC, underwriting, claims,
customer service and fraud.

No proprietary customer or company data was used.