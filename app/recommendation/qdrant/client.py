from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from app.core.config import settings


COLLECTION_NAME = "skillcart_real_jobs"


client = QdrantClient(
    url=settings.QDRANT_URL,
    api_key=settings.QDRANT_API_KEY,
    timeout=60,
    check_compatibility=False,
)


def ensure_collection():

    collections = client.get_collections().collections

    collection_names = [
        collection.name
        for collection in collections
    ]

    if COLLECTION_NAME not in collection_names:

        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=3072,
                distance=Distance.COSINE,
            ),
        )

        print(
            f"✅ Created collection: {COLLECTION_NAME}"
        )

    else:

        print(
            f"✅ Collection already exists: "
            f"{COLLECTION_NAME}"
        )