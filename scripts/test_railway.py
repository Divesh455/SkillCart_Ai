from app.recommendation.services.search_jobs import search_jobs

document = """
Python
FastAPI
Machine Learning
Docker
REST API
"""

jobs = search_jobs(document)

print(jobs)