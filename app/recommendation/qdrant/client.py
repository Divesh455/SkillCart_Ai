from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

from app.core.config import settings

COLLECTION_NAME = "jobs"

client = QdrantClient(
    url=settings.QDRANT_URL,
    api_key=settings.QDRANT_API_KEY,
    timeout=60,
    check_compatibility=False,
)

# Create collection if it doesn't exist
collections = client.get_collections().collections
collection_names = [c.name for c in collections]

if COLLECTION_NAME not in collection_names:
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=3072,      
            distance=Distance.COSINE,
        ),
    )
    print("✅ Jobs collection created")
else:
    print("✅ Jobs collection already exists")