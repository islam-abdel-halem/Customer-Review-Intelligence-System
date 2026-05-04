# Customer Review Intelligence System

A data engineering and analytics solution designed to extract, transform, and serve product review data to power business intelligence and product improvement decisions.

## Project Structure

- `raw_data/`: Contains the raw customer review dataset (`reviews.csv`).
- `database/`: Contains the structured SQLite database and Entity-Relationship Diagram (`schema_erd.png`).
- `api_service/`: A FastAPI backend that serves rolling sentiment analytics.
- `etl_pipeline.py`: The ETL script to process raw data and load it into the database.
- `strategy_report.md`: Business problem statement and data science lifecycle plan.

## Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd Customer-Review-Intelligence-System
   ```

2. **Install dependencies:**
   It's recommended to use a virtual environment.
   ```bash
   pip install -r api_service/requirements.txt
   pip install pandas
   ```

3. **Run the ETL Pipeline:**
   This step extracts raw data, transforms it (including rolling sentiment calculation), and populates the SQLite database.
   ```bash
   python etl_pipeline.py
   ```

4. **Start the API Service:**
   The FastAPI server provides secured access to the processed analytics.
   ```bash
   python -m uvicorn api_service.app:app --host 127.0.0.1 --port 8000 --reload
   ```

5. **Access the API:**
   - Swagger UI Documentation: `http://127.0.0.1:8000/docs`
   - Health Check: `http://127.0.0.1:8000/health`
   - **Note:** The analytics endpoints are secured. You must provide the API key (`x-api-key: default_secret_key`) in your request headers.

## Key Features

- **Automated ETL Pipeline**: Cleans and normalizes raw CSV data into a robust relational model (Products, Customers, Reviews, Analytics).
- **Advanced Transformations**: Computes a rolling average sentiment to track changes in customer satisfaction over time.
- **RESTful API**: Fast, asynchronous endpoints built with FastAPI, featuring request validation via Pydantic and built-in API key authentication.
- **Strategic Foundation**: Grounded in a clear business problem statement and data science life cycle plan.
