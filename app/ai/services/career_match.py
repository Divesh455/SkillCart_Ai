from app.recommendation.services.resume_document import build_resume_document
from app.recommendation.services.search_jobs import search_jobs
from app.core.railway_client import railway_client


class CareerMatchingService:

    @staticmethod
    async def match_career(resume, top_k: int = 10):
        """
        Recommend jobs based on resume similarity.
        """

        # Step 1: Convert Resume -> Text
        document = build_resume_document(resume)

        # Step 2: Search Qdrant
        job_ids = search_jobs(
            document=document,
            top_k=top_k
        )

        # Step 3: Fetch complete job details
        recommended_jobs = [job_ids]

        # for item in job_ids:

        #     try:
        #         job = railway_client.get_job(item["job_id"])

        #         recommended_jobs.append(job)

        #     except Exception:
        #         # Skip jobs that cannot be fetched
        #         continue

        return {
            "recommended_jobs": recommended_jobs,
            "total": len(recommended_jobs)
        }