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

