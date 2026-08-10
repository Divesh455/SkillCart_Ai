from app.recommendation.embeddings.embedding_model import get_embedding
from app.recommendation.qdrant.client import client, COLLECTION_NAME


def search_jobs(document: str, top_k: int = 10):
    """
    Convert resume document into embedding and search similar jobs.

    Args:
        document (str): Resume converted into plain text.
        top_k (int): Number of similar jobs to return.

    Returns:
        list: [{"job_id": int, "score": float}]
    """

    # Step 1: Generate embedding
    vector = get_embedding(document)

    # Step 2: Search Qdrant
    result = client.query_points(
        collection_name=COLLECTION_NAME,
        query=vector,
        limit=top_k,
        with_payload=True,
    )

    recommendations = []

    for point in result.points:
        recommendations.append(
            {
                "job_id": point.id,
                "score": round(point.score, 4),
            }
        )

    return recommendations