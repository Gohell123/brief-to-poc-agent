Brief → POC Agent

A one-day POC that accelerates the Sales → PreSales handoff for financial-services opportunities.

It takes a won-opportunity Brief, retrieves reusable solution templates, drafts a POC plan and Delivery handoff, keeps the final decision with a human Solution Architect, and calculates handoff SLA health.

Architecture

Won Opportunity Event
        ↓
      Brief
        ↓
Template Retrieval (BGE)
        ↓
 AI-generated Draft
        ↓
POC Plan + Delivery Handoff
        ↓
US Solution Architect
   Accept / Reject
        ↓
    OS Event
        ↓
   Feedback → Ranking

OS Event → SLA Calculation → Green / Amber / Red
                                  ↓
                            SLA Breach Trigger

Challenge Mapping

R1: Synthetic opportunity.won events and 3 customer Briefs.

R2: Template retrieval + AI-generated POC plan and Delivery handoff.

R3: Human Accept/Reject decision recorded as an OS event and used as template feedback.

R4: 2-business-day SLA calculated as Green/Amber/Red; breach creates a trigger with context.

R5: Streamlit control surface for queue, Brief, SLA health, draft, and human actions.

R6: AI used for decomposition, implementation, debugging, prompt iteration, and model evaluation. Details are in BUILD_LOG.md.

Tech Stack

Python · Streamlit · python-docx · BGE (BAAI/bge-small-en-v1.5) · Ollama/Qwen3:8B · JSON

Deterministic Python logic handles SLA calculation, validation, events, and feedback.

Run

pip install -r requirements.txt
streamlit run app.py

Demo

Open a handoff.

Review Brief and Seam Health.

Click Generate POC Plan.

Review templates, plan, and Delivery handoff.

Click Accept or Reject as the US Solution Architect.

Verify the OS event and feedback.

Run test_R4.py and test_trigger.py to demonstrate SLA health and breach triggering.

R2 Testing Note

The R2 LLM generation path is implemented in generate_r2.py. Because local Qwen3:8B generation was too slow for repeated interactive testing within the one-day time box, app.py currently uses a deterministic synthetic R2 draft for the UI demo. This allows the R3 human-decision loop to be demonstrated without changing the R2 implementation.

Data & Evaluation

The POC contains 8 reusable templates across UK/India and 3 synthetic US Briefs.

Retrieval uses BGE embeddings and cosine similarity with lightweight human-feedback scoring. R2 output has deterministic validation for structure, template consistency, grounding, and supported systems/integrations.

Decision Boundary

The AI retrieves, reasons, drafts, and prepares the handoff. The US Solution Architect makes the final POC-plan decision. See DECISION_BOUNDARY.md.

Deliberate Cuts

To stay within the one-day constraint, the POC does not include real CRM/notification integrations, a production vector DB, background SLA scheduling, production auth/RBAC, advanced learned ranking, fine-tuning, or multi-agent orchestration.

See CUT_LIST.md.

Repository

app.py
generate_r2.py
retrieve_templates.py
decision.py
feedback.py
events.py
sla.py
validate_r2.py
data/
prompts/
BUILD_LOG.md
CUT_LIST.md
DECISION_BOUNDARY.md
requirements.txt

The implementation intentionally prioritizes demonstrating the complete event → agent → human decision → learning → SLA health loop within the one-day constraint.