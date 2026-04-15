-- Schema for Product Review Link Analysis Database

-- Enable Foreign Key support
PRAGMA foreign_keys = ON;

-- Table: Products
-- Stores unique product information.
-- Since the current dataset is only for "Redmi 6", this table will initially have one record.
CREATE TABLE IF NOT EXISTS Products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT NOT NULL UNIQUE
);

-- Table: Customers
-- Stores unique customer information to normalize the database and avoid redundancy in Reviews.
CREATE TABLE IF NOT EXISTS Customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT NOT NULL
);

-- Table: Reviews
-- Stores the core review data, linking products and customers.
-- Includes the review content, rating, date, and category (aspect).
CREATE TABLE IF NOT EXISTS Reviews (
    review_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    review_date DATE,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    review_title TEXT,
    review_text TEXT,
    category TEXT, -- Represents the aspect of the review (e.g., Battery, Camera)
    useful_count INTEGER DEFAULT 0,
    FOREIGN KEY (product_id) REFERENCES Products(product_id) ON DELETE CASCADE,
    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id) ON DELETE CASCADE
);

-- Index for faster lookups by product and category
CREATE INDEX IF NOT EXISTS idx_reviews_product_id ON Reviews(product_id);
CREATE INDEX IF NOT EXISTS idx_reviews_category ON Reviews(category);
