import json
from pathlib import Path

from sentence_transformers import SentenceTransformer

MODEL_NAME = "BAAI/bge-small-en-v1.5"
ROOT = Path(__file__).resolve().parent
INPUT_PATH = ROOT / "data" / "template_documents.json"
OUTPUT_PATH = ROOT / "data" / "template_embeddings.json"


def main() -> None:
    templates = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    if len(templates) != 8:
        raise ValueError(f"Expected 8 templates, found {len(templates)}")

    model = SentenceTransformer(MODEL_NAME)
    texts = [template["text"] for template in templates]
    embeddings = model.encode(texts, normalize_embeddings=True)

    records = [
        {
            "template_id": template["template_id"],
            "embedding": embedding.tolist(),
        }
        for template, embedding in zip(templates, embeddings)
    ]

    OUTPUT_PATH.write_text(json.dumps(records, indent=2), encoding="utf-8")
    print(f"Saved {len(records)} embeddings ({len(records[0]['embedding'])} dims) to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
