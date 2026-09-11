from app.recommendation.services.company_jobs import (
    get_all_jobs,
)


def main():

    print()
    print("========================================")
    print("      COMPANY API JOB FETCH TEST")
    print("========================================")

    jobs = get_all_jobs()

    print()
    print("========================================")
    print("RESULT")
    print("========================================")

    print(f"Total jobs fetched: {len(jobs)}")

    if jobs:

        print()
        print("First job:")
        print(
            f"ID    : {jobs[0].get('id')}"
        )
        print(
            f"Title : {jobs[0].get('job_title')}"
        )

        print()
        print("Last job:")
        print(
            f"ID    : {jobs[-1].get('id')}"
        )
        print(
            f"Title : {jobs[-1].get('job_title')}"
        )

    print("========================================")


if __name__ == "__main__":
    main()