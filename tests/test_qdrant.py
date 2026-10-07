import os
import requests
from dotenv import load_dotenv

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

print("=" * 60)
print("QDRANT CONNECTION TEST")
print("=" * 60)

print("QDRANT_URL:", QDRANT_URL)
print("API KEY EXISTS:", bool(QDRANT_API_KEY))

if not QDRANT_URL:
    print("❌ QDRANT_URL is missing from .env")
    exit()

if not QDRANT_API_KEY:
    print("❌ QDRANT_API_KEY is missing from .env")
    exit()

try:
    print("\nConnecting to Qdrant...")

    response = requests.get(
        f"{QDRANT_URL}/collections",
        headers={
            "api-key": QDRANT_API_KEY
        },
        timeout=15
    )

    print("HTTP STATUS:", response.status_code)
    print("RESPONSE:")
    print(response.text)

    if response.status_code == 200:
        print("\n✅ QDRANT CONNECTION SUCCESSFUL")
        print("Your cluster received a request.")
    else:
        print("\n❌ QDRANT REQUEST FAILED")

except requests.exceptions.Timeout:
    print("\n❌ Request timed out.")

except requests.exceptions.ConnectionError as e:
    print("\n❌ Connection error:")
    print(e)

except Exception as e:
    print("\n❌ Unexpected error:")
    print(type(e).__name__, e)

print("\n" + "=" * 60)