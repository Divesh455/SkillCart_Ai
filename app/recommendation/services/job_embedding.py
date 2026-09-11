from qdrant_client.models import PointStruct

from app.recommendation.embeddings.embedding_model import (
    get_embedding,
)

from app.recommendation.qdrant.client import (
    client,
    COLLECTION_NAME,
)

from app.recommendation.services.job_document import (
    build_job_document,
)


def index_job(job: dict) -> dict:

    job_id = job.get("id")

    if job_id is None:
        raise ValueError("Job ID is missing")

    job_id = int(job_id)

    document = build_job_document(job)

    if not document:
        raise ValueError(
            f"Job {job_id} has no embeddable content"
        )

    print(
        f"Generating embedding for job {job_id}..."
    )

    vector = get_embedding(document)

    print(
        f"Embedding dimensions: {len(vector)}"
    )

    if len(vector) != 3072:
        raise ValueError(
            f"Expected 3072 dimensions, "
            f"got {len(vector)}"
        )

    point = PointStruct(
        id=job_id,
        vector=vector,
        payload={
            "job_id": job_id
        },
    )

    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[point],
    )

    return {
        "job_id": job_id,
        "status": "indexed",
    }