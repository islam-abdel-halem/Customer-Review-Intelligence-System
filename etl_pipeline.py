"""
Phase 3 ETL Pipeline — Product Review Analysis
Stages: Extract/Clean (Pandas) → Load Schema → Load Data → Feature Engineering (SQL Window Function)
Idempotent: clears tables before each run so repeated runs produce the same result.
"""

import os
import re
import sqlite3
import pandas as pd
from datetime import datetime

# --- Paths ---
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
CSV_PATH    = os.path.join(BASE_DIR, "raw_data", "reviews.csv")
SCHEMA_PATH = os.path.join(BASE_DIR, "database", "schema.sql")
DB_PATH     = os.path.join(BASE_DIR, "database", "reviews_db.sqlite")

PRODUCT_NAME = "redmi 6"


# --- Stage 1: Extract & Clean ---

def extract_and_clean(csv_path: str) -> pd.DataFrame:
    """Read reviews.csv, parse/clean fields, and return a normalised DataFrame."""
    print("[EXTRACT] Reading CSV ...")
    df = pd.read_csv(csv_path, encoding="cp1252")
    print(f"  Raw rows: {len(df)}")

    df.rename(columns={
        "Review Title": "review_title", "Customer name": "customer_name",
        "Rating": "rating_raw", "Date": "date_raw",
        "Category": "category", "Comments": "review_text", "Useful": "useful_count",
    }, inplace=True)

    df.dropna(subset=["rating_raw", "customer_name"], inplace=True)

    # Parse "4.0 out of 5 stars" → 4.0
    def parse_rating(raw: str) -> float | None:
        m = re.search(r"(\d+(?:\.\d+)?)\s+out of", str(raw))
        return float(m.group(1)) if m else None

    df["rating"] = df["rating_raw"].apply(parse_rating)
    df.dropna(subset=["rating"], inplace=True)

    # Parse "on 1 October 2018" → "2018-10-01"
    def parse_date(raw: str) -> str | None:
        try:
            return datetime.strptime(str(raw).replace("on ", "").strip(), "%d %B %Y").strftime("%Y-%m-%d")
        except Exception:
            return None

    df["review_date"] = df["date_raw"].apply(parse_date)

    df["review_title"]  = df["review_title"].fillna("").str.lower().str.strip()
    df["customer_name"] = df["customer_name"].str.strip()
    df["category"]      = df["category"].fillna("general").str.strip()
    df["review_text"]   = df["review_text"].fillna("").str.strip()
    df["useful_count"]  = pd.to_numeric(df["useful_count"], errors="coerce").fillna(0).astype(int)
    df["product_name"]  = PRODUCT_NAME
    df.drop(columns=["rating_raw", "date_raw"], inplace=True)

    print(f"  Clean rows: {len(df)}")
    return df


# --- Stage 2: Load Schema ---

def load_schema(conn: sqlite3.Connection, schema_path: str) -> None:
    """Create core tables from schema.sql and the analytical ProductSentimentAnalytics table."""
    print("[SCHEMA] Creating tables ...")
    with open(schema_path, "r", encoding="utf-8") as f:
        conn.executescript(f.read())

    # Analytical table — stores the ETL-computed rolling average feature
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS ProductSentimentAnalytics (
            analytics_id          INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id            INTEGER NOT NULL,
            review_id             INTEGER NOT NULL,
            review_date           DATE,
            rating                REAL,
            rolling_avg_sentiment REAL,
            FOREIGN KEY (product_id) REFERENCES Products(product_id),
            FOREIGN KEY (review_id)  REFERENCES Reviews(review_id)
        );
        CREATE INDEX IF NOT EXISTS idx_psa_product_id ON ProductSentimentAnalytics(product_id);
    """)
    print("  Tables ready.")


# --- Stage 3: Load Data (Idempotent) ---

def load_data(conn: sqlite3.Connection, df: pd.DataFrame) -> None:
    """Clear and reload Products, Customers, and Reviews. Deletes in FK-safe order before inserting."""
    print("[LOAD] Resetting tables ...")
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")
    for tbl in ["ProductSentimentAnalytics", "Reviews", "Customers", "Products"]:
        cur.execute(f"DELETE FROM {tbl};")
    conn.commit()

    # Products
    cur.executemany("INSERT INTO Products (product_name) VALUES (?);",
                    [(n,) for n in df["product_name"].unique()])
    conn.commit()
    product_map = {r[1]: r[0] for r in cur.execute("SELECT product_id, product_name FROM Products;")}
    print(f"  Products: {len(product_map)}")

    # Customers
    cur.executemany("INSERT INTO Customers (customer_name) VALUES (?);",
                    [(n,) for n in df["customer_name"].unique()])
    conn.commit()
    customer_map = {r[1]: r[0] for r in cur.execute("SELECT customer_id, customer_name FROM Customers;")}
    print(f"  Customers: {len(customer_map)}")

    # Reviews
    rows = [
        (product_map[r["product_name"]], customer_map[r["customer_name"]],
         r["review_date"], r["rating"], r["review_title"],
         r["review_text"], r["category"], r["useful_count"])
        for _, r in df.iterrows()
    ]
    cur.executemany(
        "INSERT INTO Reviews (product_id, customer_id, review_date, rating, "
        "review_title, review_text, category, useful_count) VALUES (?,?,?,?,?,?,?,?);",
        rows,
    )
    conn.commit()
    print(f"  Reviews: {len(rows)}")


# --- Stage 4: Feature Engineering (SQL Window Function) ---

def compute_rolling_sentiment(conn: sqlite3.Connection) -> None:
    """
    Compute rolling_avg_sentiment (last 5 reviews per product) using a CTE and
    SQL Window Function, then persist results in ProductSentimentAnalytics.

    Window function:
      AVG(rating) OVER (
          PARTITION BY product_id          -- isolated per product
          ORDER BY review_date             -- chronological order
          ROWS BETWEEN 4 PRECEDING AND CURRENT ROW  -- sliding 5-row frame
      )
    """
    print("[FEATURE] Computing rolling average sentiment ...")
    conn.execute("DELETE FROM ProductSentimentAnalytics;")
    conn.commit()

    conn.execute("""
        -- CTE: compute rolling average for each review chronologically per product
        WITH RankedReviews AS (
            SELECT
                review_id, product_id, review_date, rating,
                AVG(rating) OVER (
                    PARTITION BY product_id
                    ORDER BY review_date
                    ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
                ) AS rolling_avg_sentiment
            FROM Reviews
        )
        INSERT INTO ProductSentimentAnalytics
            (product_id, review_id, review_date, rating, rolling_avg_sentiment)
        SELECT product_id, review_id, review_date, rating,
               ROUND(rolling_avg_sentiment, 4)
        FROM RankedReviews
        ORDER BY product_id, review_date;
    """)
    conn.commit()

    count = conn.execute("SELECT COUNT(*) FROM ProductSentimentAnalytics;").fetchone()[0]
    print(f"  Rows written: {count}")

    # Quick sanity check — first 10 rows
    print(f"\n  {'review_id':<12} {'review_date':<14} {'rating':<8} rolling_avg_sentiment")
    print(f"  {'-'*12} {'-'*14} {'-'*8} {'-'*21}")
    for row in conn.execute(
        "SELECT review_id, review_date, rating, rolling_avg_sentiment "
        "FROM ProductSentimentAnalytics ORDER BY review_date LIMIT 10;"
    ).fetchall():
        print(f"  {row[0]:<12} {str(row[1]):<14} {row[2]:<8} {row[3]}")


# --- Main ---

def main() -> None:
    print("=" * 55)
    print("  ETL Pipeline — Product Review Analysis (Phase 3)")
    print("=" * 55)

    df_clean = extract_and_clean(CSV_PATH)

    # Context manager ensures the connection is always closed cleanly
    with sqlite3.connect(DB_PATH) as conn:
        load_schema(conn, SCHEMA_PATH)
        load_data(conn, df_clean)
        compute_rolling_sentiment(conn)

    print(f"\n  Done. DB saved to: {DB_PATH}")


if __name__ == "__main__":
    main()
