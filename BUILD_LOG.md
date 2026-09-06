## 1. Template Embedding

**Requirement:** Generate embeddings for the 8 solution templates.

**Decision:** Use local `BAAI/bge-small-en-v1.5`.

**Why:** Cohere Embed v4 through Bedrock was blocked by the AWS
account. Local embedding avoids the dependency and fits the 8-hour POC.

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

**Result:** Cursor created embed_templates.py and generated embeddings
for all 8 templates.

**Validation:** 8 embeddings, 384 dimensions.

**Discarded approach:** Cohere Embed v4 via Amazon Bedrock because
model invocation was blocked for the AWS account.

## 2. Template Retrieval

**Requirement:** Retrieve relevant solution templates from the template library for an incoming Brief.

**Decision:** Use BAAI/bge-small-en-v1.5 embeddings with cosine similarity. Retrieve top 3 templates from the 8-template synthetic library.

**Why:** The POC has only 8 templates, so an in-memory similarity search is sufficient and avoids unnecessary vector DB complexity within the 8-hour constraint.

**AI Tool:** Cursor Agent

**Prompt:**
Implement template retrieval.

- Read template embeddings from data/template_embeddings.json
- Embed a Brief using BAAI/bge-small-en-v1.5
- Calculate cosine similarity against all template embeddings
- Return top 3 template_ids with scores
- Use data/templates.json to return the full template metadata
- Create retrieve_templates.py
- Add a simple test using BRIEF-001
- No vector DB or UI yet.

**Validation:**
Tested all 3 synthetic briefs. The correct domain template ranked #1 for each:
- BRIEF-001 → UK-001 KYC
- BRIEF-002 → UK-003 Claims
- BRIEF-003 → UK-002 Underwriting

**Result:** Retrieval successfully identifies relevant templates across different use cases.

**Discarded approach:** Vector database at this stage. With only 8 templates, direct cosine similarity is simpler and faster for the POC.

## 3. R2 Generation

**Requirement:** From a Brief and the top 3 retrieved templates, generate match explanations, an editable POC plan, and an editable Delivery handoff as structured JSON. Ground output only in the Brief and templates.

**Decision:** Local Ollama `qwen3:1.7b` via `http://127.0.0.1:11434`. Prompt lives in `prompts/r2_generation.txt`. Script is `generate_r2.py`.

**Why:** The model is already on the machine, needs no cloud API key, and avoids Amazon Bedrock invoke (Cohere Embed was previously blocked on this AWS account). 1.7b is fast enough for this small JSON task. Instructions stay in a separate file so the prompt can be edited without changing code.

**AI Tool:** Cursor Agent

**Prompt:**
Implement R2 generation.

- Take a Brief and the top 3 retrieved templates
- Use a suitable LLM to explain matches, draft a POC plan, and draft a Delivery handoff
- Base output only on the Brief and retrieved templates
- Include template IDs used and proposed changes
- Return structured JSON; keep prompt/instructions in a separate file
- Choose the LLM for speed and simplicity, and document the choice
- Test with BRIEF-001
- No UI yet

**Validation:** `generate_r2.py` with BRIEF-001 writes `data/r2_BRIEF-001.json`.

**Discarded approach:** Amazon Bedrock LLMs, because embedding invoke was already blocked on this account and local Ollama was available. Larger cloud models were skipped for speed and setup cost in the 8-hour POC.

### R2 model selection

Initial generation used Qwen3 1.7B locally. Testing showed recurring
instruction-following and grounding errors, including mixing Brief
systems with template integrations and unsupported claims.

Switched to Qwen3 8B locally. The same retrieval inputs and generation
prompt produced materially better template reasoning, source separation,
and structured output.

Decision: use Qwen3 8B for the POC.

### R3 — Human decision and feedback learning

Decision:
- The human decision-maker is the US Solution Architect.
- The Solution Architect can accept, edit, or reject the generated POC plan.
- Each decision is recorded as an OS event with timestamp, owner, brief ID, decision, and template IDs.
- Accepted and edited decisions provide positive feedback for the templates used.
- Rejected decisions provide negative feedback.
- Template ranking uses a lightweight feedback adjustment on top of semantic similarity rather than training a separate ML model.

Implementation:
- `decision.py` records the human decision as an OS event.
- `feedback.py` persists accepted/rejected counts in `data/template_feedback.json`.
- `retrieve_templates.py` combines semantic similarity with the feedback score when ranking templates.

Feedback scoring:
- Accepted template: +0.02
- Rejected template: -0.02
- Final ranking score = semantic similarity + feedback score.

Validation:
- Tested accepted, edited, and rejected decisions.
- Verified that each decision creates an OS event owned by `US Solution Architect`.
- Verified that feedback is persisted.
- Verified that accepted templates receive a higher ranking score on subsequent retrieval.

Assumption:
- The requirement states that reuse rate and template ranking should learn from acceptance/rejection but does not specify a learning algorithm. A lightweight feedback-based ranking approach was chosen for the one-day POC.

### R4 — Seam health and automatic trigger

Decision:
- SLA is 2 business days.
- Health is calculated automatically from the OS event timestamp.
- Green = below 70% of SLA.
- Amber = 70–100% of SLA.
- Red = SLA breached.
- On breach, an automatic `seam.sla_breached` OS event is created for the US Solution Architect with the current SLA context and generated draft attached.
- For the POC, the trigger is persisted to `data/trigger_log.json` rather than integrating Slack/email.

Assumption:
- The requirement specifies green/amber/red but does not define the amber threshold, so 70% was chosen.
- "Continuously" is simulated by recalculating seam health whenever the system checks the seam; a background scheduler is intentionally cut for the one-day POC.

Validation:
- Tested green, amber, and red states.
- Tested Friday-to-Tuesday business-day calculation.
- Tested automatic breach trigger and verified draft attachment.

