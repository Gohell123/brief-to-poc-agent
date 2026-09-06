from sentence_transformers import SentenceTransformer

MODEL_NAME = "BAAI/bge-small-en-v1.5"

model = SentenceTransformer(MODEL_NAME)

text = """
KYC Document Review Assistant
Region: UK
Segment: retail_bank
Regulator: FCA
Problem solved: Automate first-level review of customer KYC documents and identify missing or inconsistent information.
Capabilities: Document classification; Identity information extraction; Missing document detection; KYC exception flagging
Integrations: Document Management System; Customer Master; KYC Case Management
Outcome: Reduced manual KYC review effort and improved identification of incomplete onboarding cases.
"""

embedding = model.encode(text)

print("Embedding successful!")
print("Dimension:", len(embedding))
print("First 5 values:", embedding[:5])