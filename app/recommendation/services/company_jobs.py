import requests

from app.core.config import settings


def get_job(job_id: int) -> dict:
    """
    Fetch a single job by ID.
    """

    url = f"{settings.COMPANY_API_URL}/jobs/{job_id}"

    response = requests.get(
        url,
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


def get_all_jobs(
    page_size: int = 20,
) -> list[dict]:
    """
    Fetch all jobs from the Company API.

    API response format:

    {
        "total": 94,
        "limit": 20,
        "offset": 0,
        "items": [...]
    }
    """

    all_jobs = []

    offset = 0

    while True:

        url = f"{settings.COMPANY_API_URL}/jobs"

        params = {
            "limit": page_size,
            "offset": offset,
        }

        response = requests.get(
            url,
            params=params,
            timeout=60,
        )

        response.raise_for_status()

        data = response.json()

        # Validate response
        if not isinstance(data, dict):
            raise ValueError(
                "Unexpected Company API response: "
                "expected JSON object"
            )

        items = data.get("items", [])

        if not isinstance(items, list):
            raise ValueError(
                "Unexpected Company API response: "
                "'items' must be a list"
            )

        total = data.get("total", 0)

        all_jobs.extend(items)

        print(
            f"Fetched {len(all_jobs)}/{total} jobs"
        )

        # ----------------------------------------
        # Stop conditions
        # ----------------------------------------

        if not items:
            break

        if len(all_jobs) >= total:
            break

        offset += len(items)

    return all_jobs