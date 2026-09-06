from feedback import feedback_score
import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "BAAI/bge-small-en-v1.5"
ROOT = Path(__file__).resolve().parent
EMBEDDINGS_PATH = ROOT / "data" / "template_embeddings.json"
TEMPLATES_PATH = ROOT / "data" / "templates.json"
BRIEFS_PATH = ROOT / "data" / "briefs.json"
TOP_K = 3


def brief_to_text(brief: dict) -> str:
    systems = "; ".join(brief["systems"])
    criteria = "; ".join(brief["success_criteria"])
    return (
        f"{brief['account']}\n"
        f"Region: {brief['region']}\n"
        f"Segment: {brief['segment']}\n"
        f"Regulator: {brief['regulator']}\n"
        f"Problem solved: {brief['business_problem']}\n"
        f"Integrations: {systems}\n"
        f"Success criteria: {criteria}\n"
        f"Timeline: {brief['expected_timeline']}"
    )


def cosine_similarity(query: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    query_norm = np.linalg.norm(query)
    matrix_norms = np.linalg.norm(matrix, axis=1)
    return (matrix @ query) / (matrix_norms * query_norm)


def load_brief(brief_id: str) -> dict:
    briefs = json.loads(BRIEFS_PATH.read_text(encoding="utf-8"))
    for brief in briefs:
        if brief["brief_id"] == brief_id:
            return brief
    raise KeyError(f"Brief not found: {brief_id}")


def retrieve_templates(brief: dict, top_k: int = TOP_K) -> list[dict]:
    embedding_records = json.loads(EMBEDDINGS_PATH.read_text(encoding="utf-8"))
    templates = {
        template["template_id"]: template
        for template in json.loads(TEMPLATES_PATH.read_text(encoding="utf-8"))
    }

    model = SentenceTransformer(MODEL_NAME)
    query_embedding = np.asarray(
        model.encode(brief_to_text(brief), normalize_embeddings=True),
        dtype=np.float32,
    )
    template_ids = [record["template_id"] for record in embedding_records]
    matrix = np.asarray(
        [record["embedding"] for record in embedding_records],
        dtype=np.float32,
    )
    scores = cosine_similarity(query_embedding, matrix)

    results = []

    for index in range(len(template_ids)):
        template_id = template_ids[index]
        semantic_score = float(scores[index])
        feedback = feedback_score(template_id)

        results.append(
            {
                "template_id": template_id,
                "name": templates[template_id]["name"],
                "similarity": semantic_score,
                "feedback_score": feedback,
                "final_score": semantic_score + feedback,
                "segment": templates[template_id]["segment"],
                "problem_solved": templates[template_id]["problem_solved"],
            }
        )

    results.sort(
        key=lambda x: x["final_score"],
        reverse=True,
    )

    results = results[:top_k]

    return results


def test_brief_001() -> None:
    brief = load_brief("BRIEF-001")
    results = retrieve_templates(brief, top_k=3)

    assert len(results) == 3
    scores = [item["similarity"] for item in results]
    assert scores == sorted(scores, reverse=True)

    print(f"Query: {brief['brief_id']} - {brief['account']}")
    for rank, item in enumerate(results, start=1):
        print(
            f"{rank}. {item['template_id']}  {item['name']}  "
            f"score={item['similarity']:.4f}"
        )


if __name__ == "__main__":
    test_brief_001()
