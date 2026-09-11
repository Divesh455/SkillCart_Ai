from app.recommendation.qdrant.client import (
    client,
    COLLECTION_NAME,
    ensure_collection,
)


def main():

    print()
    print("========================================")
    print("        SKILLCART QDRANT TEST")
    print("========================================")

    try:

        # Test connection
        collections = client.get_collections()

        print("\n✅ Qdrant connection successful")

        print("\nExisting collections:")

        for collection in collections.collections:
            print(f"   - {collection.name}")

        # Make sure our collection exists
        ensure_collection()

        # Get our collection information
        info = client.get_collection(
            COLLECTION_NAME
        )

        print("\n----------------------------------------")
        print("Our Collection")
        print("----------------------------------------")

        print(f"Name       : {COLLECTION_NAME}")
        print(f"Points     : {info.points_count}")

        print("\n========================================")

    except Exception as e:

        print("\n❌ Qdrant connection failed")
        print(f"Error: {e}")

        raise


if __name__ == "__main__":
    main()