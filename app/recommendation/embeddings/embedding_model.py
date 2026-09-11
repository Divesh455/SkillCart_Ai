from langchain_google_genai import (
    GoogleGenerativeAIEmbeddings
)

from app.core.config import settings


embedding_model = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=settings.GEMINI_API_KEY,
)


def get_embedding(document: str) -> list[float]:

    if not document.strip():
        raise ValueError(
            "Cannot embed an empty document"
        )

    return embedding_model.embed_query(document)