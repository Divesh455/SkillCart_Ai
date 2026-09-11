from app.recommendation.services.company_jobs import (
    get_job,
)

from app.recommendation.services.job_embedding import (
    index_job,
)


def main():

    print()
    print("========================================")
    print("       REAL JOB EMBEDDING TEST")
    print("========================================")

    print("\nFetching Job 1...")

    job = get_job(1)

    print(
        f"Job ID  : {job.get('id')}"
    )

    print(
        f"Title   : {job.get('job_title')}"
    )

    company = job.get("company") or {}

    print(
        f"Company : "
        f"{company.get('company_name')}"
    )

    print("\nIndexing job...")

    result = index_job(job)

    print("\n✅ SUCCESS")
    print(result)

    print("========================================")


if __name__ == "__main__":
    main()