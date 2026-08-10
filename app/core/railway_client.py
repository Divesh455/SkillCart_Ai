import requests

from app.core.config import settings


class RailwayClient:

    def __init__(self):

        self.base_url = settings.RAILWAY_API

    # -----------------------------------------

    def get_job(self, job_id: int):

        """
        Fetch one job by ID
        """

        response = requests.get(
            f"{self.base_url}/jobs/{job_id}",
            timeout=30
        )

        response.raise_for_status()

        return response.json()

    # -----------------------------------------

    def get_company(self, company_id: int):

        """
        Fetch one company
        """

        response = requests.get(
            f"{self.base_url}/companies/{company_id}",
            timeout=30
        )

        response.raise_for_status()

        return response.json()

    # -----------------------------------------

    def get_jobs(self, limit=100, offset=0):

        """
        Fetch all jobs
        """

        response = requests.get(

            f"{self.base_url}/jobs",

            params={

                "limit": limit,

                "offset": offset

            },

            timeout=30

        )

        response.raise_for_status()

        return response.json()

    # -----------------------------------------

    def get_roles_summary(self):

        response = requests.get(

            f"{self.base_url}/roles/summary",

            timeout=30

        )

        response.raise_for_status()

        return response.json()


railway_client = RailwayClient()