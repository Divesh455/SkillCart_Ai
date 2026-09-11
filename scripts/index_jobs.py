from app.recommendation.services.company_jobs import (
    get_all_jobs,
)

from app.recommendation.services.job_embedding import (
    index_job,
)

from app.recommendation.qdrant.client import (
    ensure_collection,
)


def main():

    print()
    print("==============================================")
    print("       SKILLCART REAL JOB INDEXING")
    print("==============================================")

    # Make sure Qdrant collection exists
    ensure_collection()

    # ------------------------------------------
    # Fetch jobs
    # ------------------------------------------

    print("\nFetching jobs from Company API...")

    jobs = get_all_jobs()

    print(
        f"✅ Jobs received: {len(jobs)}"
    )

    # ------------------------------------------
    # Counters
    # ------------------------------------------

    success = 0
    skipped = 0
    failed = 0

    # ------------------------------------------
    # Index jobs
    # ------------------------------------------

    for index, job in enumerate(
        jobs,
        start=1,
    ):

        job_id = job.get("id")

        print()
        print(
            f"[{index}/{len(jobs)}] "
            f"Job ID: {job_id}"
        )

        try:

            # Validate ID
            if job_id is None:

                print(
                    "⚠️ Skipped: missing job ID"
                )

                skipped += 1

                continue

            # ----------------------------------
            # Check status
            # ----------------------------------

            status = job.get("status")

            if status and status.lower() != "active":

                print(
                    f"⚠️ Skipped: status={status}"
                )

                skipped += 1

                continue

            # ----------------------------------
            # Index
            # ----------------------------------

            result = index_job(job)

            print(
                f"✅ Indexed Job {job_id}"
            )

            success += 1

        except Exception as e:

            failed += 1

            print(
                f"❌ Failed Job {job_id}"
            )

            print(
                f"   Error: {e}"
            )

    # ------------------------------------------
    # Final result
    # ------------------------------------------

    print()
    print("==============================================")
    print("             INDEXING COMPLETE")
    print("==============================================")

    print(
        f"Total received : {len(jobs)}"
    )

    print(
        f"Successfully indexed : {success}"
    )

    print(
        f"Skipped : {skipped}"
    )

    print(
        f"Failed : {failed}"
    )

    print("==============================================")


if __name__ == "__main__":
    main()