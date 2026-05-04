import os
import sqlite3
from fastapi import FastAPI, Depends, HTTPException, Header, status
from typing import Annotated
from .models import SentimentResponse, HealthResponse

app = FastAPI(title="Product Review Analytics API")

# Configuration
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "database", "reviews_db.sqlite")
API_KEY = os.getenv("ANALYTICS_API_KEY", "default_secret_key")

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

async def verify_api_key(x_api_key: Annotated[str | None, Header()] = None):
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key",
        )
    return x_api_key

@app.get("/health", response_model=HealthResponse)
async def health_check():
    db_status = "active"
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("SELECT 1")
        conn.close()
    except Exception:
        db_status = "inactive"
    
    return HealthResponse(status="ok", database_status=db_status)

@app.get("/api/v1/sentiment/{product_id}", response_model=SentimentResponse)
async def get_sentiment(
    product_id: int,
    db: sqlite3.Connection = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    query = """
        SELECT 
            p.product_id, 
            p.product_name, 
            psa.rating as latest_rating, 
            psa.rolling_avg_sentiment
        FROM ProductSentimentAnalytics psa
        JOIN Products p ON p.product_id = psa.product_id
        WHERE p.product_id = ?
        ORDER BY psa.review_date DESC
        LIMIT 1
    """
    row = db.execute(query, (product_id,)).fetchone()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found in analytics."
        )
    
    return SentimentResponse(
        product_id=row["product_id"],
        product_name=row["product_name"],
        latest_rating=row["latest_rating"],
        rolling_average_sentiment=row["rolling_avg_sentiment"]
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
