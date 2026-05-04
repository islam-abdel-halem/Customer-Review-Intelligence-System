from pydantic import BaseModel
from typing import Optional

class SentimentResponse(BaseModel):
    product_id: int
    product_name: str
    latest_rating: float
    rolling_average_sentiment: float

class HealthResponse(BaseModel):
    status: str
    database_status: str
