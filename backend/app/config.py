import os
from pydantic import BaseModel

class Settings(BaseModel):
    project_id: str = os.getenv("GOOGLE_CLOUD_PROJECT", "")
    location: str = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
    gcs_bucket: str = os.getenv("GCS_BUCKET", "")

settings = Settings()
