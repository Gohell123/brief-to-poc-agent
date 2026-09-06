# Cut List

The following capabilities were intentionally cut to stay within the one-day implementation constraint.

1. **Real CRM integration**
   - Synthetic OS events and briefs are used instead.
   - **At 10x volume:** replace synthetic events with CRM/webhook ingestion.

2. **Real Slack/Teams/email integration**
   - The Trigger Log represents the escalation path.
   - **At 10x volume:** connect SLA-breach events to the enterprise notification system.

3. **Production vector database**
   - The POC contains only 8 solution templates, so in-memory BGE cosine retrieval is sufficient.
   - **At 10x volume:** move retrieval to a production vector/hybrid search system with metadata filtering.

4. **Background SLA scheduler**
   - Seam health is recalculated when the control surface is refreshed.
   - **At 10x volume:** introduce scheduled/event-driven SLA monitoring.

5. **Advanced ML feedback model**
   - A lightweight acceptance/rejection score is used to demonstrate learning.
   - **At 10x volume:** evaluate a learned ranking model using accumulated human feedback.

6. **Production authentication and authorization**
   - Not required for the synthetic POC.
   - **At production scale:** enforce identity, RBAC, tenant isolation, and audit controls.

7. **Fine-tuning / multi-agent orchestration**
   - The POC uses a single LLM agent with retrieval and deterministic validation.
   - **At production scale:** consider these only if evaluation data demonstrates a measurable benefit.
